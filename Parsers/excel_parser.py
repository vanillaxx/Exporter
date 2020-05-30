import xlrd
import DAL.utils
import sys
import datetime
from calendar import monthrange


def get_start_end_date(period):
    period = period.split('-')
    start, end = period[0], period[1]
    start = datetime.datetime.strptime(start, '%m.%y')
    end = datetime.datetime.strptime(end, '%m.%y')
    end = end.replace(day=monthrange(end.year, end.month)[1])
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def get_sheet(path, sheet_name):
    excel_file = xlrd.open_workbook(path)
    return excel_file.sheet_by_name(sheet_name)


def insert_ekd_data(ekd_section, ekd_class):
    DAL.utils.insert_ekd_section(ekd_section)
    DAL.utils.insert_ekd_class(ekd_class)


def insert_float_value(where, value):
    if value:
        where.append(float(value))
    else:
        where.append(0.0)


class ExcelParser():
    def __init__(self):
        self.assets_categories = [
            'Non-current assets', 'Current assets',
            'Assets held for sale and discontinuing operations',
            'Called up capital', 'Own shares'
        ]
        self.equity_liabilities_categories = [
            'Equity shareholders of the parent', 'Non-controlling interests',
            'Non-current liabilities', 'Current liabilities',
            'Liabilities related to assets held for sale and discontinued operations'
        ]
        self.available_sheets = [
            'QS', 'YS'
        ]

    def parse_company(self, path):
        def parse_ekd(ekd):
            parsed_ekd = ekd.split('.')
            return parsed_ekd[0], parsed_ekd[1]

        excel_sheet = get_sheet(path, 'Info')
        attribute_column = 0
        value_column = 1
        name_row = 2
        ticker_row = 12
        bloomberg_row = 16
        ekd_row = 25
        if excel_sheet.cell(name_row, attribute_column).value == 'Nazwa':
            company_name = excel_sheet.cell(name_row, value_column).value
        else:
            raise ValueError('(A3=Nazwa) of company should be in B3 cell')
        if excel_sheet.cell(ticker_row, attribute_column).value == 'TICKER':
            company_ticker = excel_sheet.cell(ticker_row, value_column).value
        else:
            raise ValueError('(A13=TICKER) of company should be in B13 cell')
        if excel_sheet.cell(bloomberg_row, attribute_column).value == 'Bloomberg':
            company_bloomberg = excel_sheet.cell(bloomberg_row, value_column).value
        else:
            raise ValueError('(A17=Bloomberg) of company should be in B17 cell')
        if excel_sheet.cell(ekd_row, attribute_column).value == 'EKD 1':
            company_ekd = excel_sheet.cell(ekd_row, value_column).value
        else:
            raise ValueError('(A26=EKD 1) of company should be in B26 cell')

        ekd_section, ekd_class = parse_ekd(company_ekd)
        insert_ekd_data(ekd_section, ekd_class)
        DAL.utils.insert_company(company_name, company_ticker, company_bloomberg,
                                 ekd_section, ekd_class)

    def parse_balance_sheet(self, path, sheet_name):
        if sheet_name not in self.available_sheets:
            raise ValueError("Available sheet names: QS, YS")
        excel_sheet = get_sheet(path, sheet_name)
        company_id = self.get_company(path)
        curr_row = 0
        curr_column = 2
        assets = equity_liabilities_categories = [company_id]
        equity_liabilities = assets_categories = [company_id]
        while curr_row < excel_sheet.nrows:
            if excel_sheet.cell(curr_row, curr_column).value == 'Balance sheet':
                attributes_column = curr_column
                curr_column += 1
                dates_row = curr_row + 1
                sum_row = dates_row + 1
                curr_row += 3
                assets_attributes = equity_liabilities_categories_attributes = ['CompanyID', 'Date']
                assets_categories_attributes = equity_liabilities_attributes = ['CompanyID', 'Date']
                while curr_column < excel_sheet.ncols:
                    # check if data for that period exists
                    if not excel_sheet.cell(sum_row, curr_column).value:
                        curr_column += 1
                        continue
                    # add date to list
                    date_value = excel_sheet.cell(dates_row, curr_column).value
                    assets.append(date_value)
                    assets_categories.append(date_value)
                    equity_liabilities.append(date_value)
                    equity_liabilities_categories.append(date_value)
                    # iterate from the first element until assets end
                    while excel_sheet.cell(curr_row, attributes_column).value != '':
                        attribute = excel_sheet.cell(curr_row, attributes_column).value
                        curr_value = excel_sheet.cell(curr_row, curr_column).value
                        if attribute in self.assets_categories:
                            assets_categories_attributes.append(attribute)
                            insert_float_value(assets_categories, curr_value)
                        else:
                            assets_attributes.append(attribute)
                            insert_float_value(assets, curr_value)
                        curr_row += 1

                    curr_row += 2
                    # omit headers and iterate until equities and liabilities end
                    while excel_sheet.cell(curr_row, attributes_column).value != 'Date of publication':
                        attribute = excel_sheet.cell(curr_row, attributes_column).value
                        curr_value = excel_sheet.cell(curr_row, curr_column).value
                        if attribute in self.equity_liabilities_categories:
                            equity_liabilities_categories_attributes.append(attribute)
                            insert_float_value(equity_liabilities_categories, curr_value)
                        else:
                            equity_liabilities_attributes.append(attribute)
                            insert_float_value(equity_liabilities, curr_value)
                        curr_row += 1

                    DAL.utils.insert_values(table_name="Assets",
                                            columns=assets_attributes,
                                            values=assets)
                    DAL.utils.insert_values(table_name="EquityLiabilities",
                                            columns=equity_liabilities_attributes,
                                            values=equity_liabilities)
                    DAL.utils.insert_values(table_name="AssetsCategories",
                                            columns=assets_categories_attributes,
                                            values=assets_categories)
                    DAL.utils.insert_values(table_name="EquityLiabilitiesCategories",
                                            columns=equity_liabilities_categories_attributes,
                                            values=equity_liabilities_categories)
                    assets_attributes = equity_liabilities_categories_attributes = ['CompanyID', 'Date']
                    assets_categories_attributes = equity_liabilities_attributes = ['CompanyID', 'Date']
                    assets = equity_liabilities_categories = [company_id]
                    assets_categories = equity_liabilities = [company_id]
                    curr_column += 1
                    curr_row = sum_row + 1
                break
            curr_row += 1

    def parse_financial_ratios(self, path, sheet_name):
        self.parse_ratios(path, sheet_name, 'Financial ratios', 'FinancialRatios')

    def parse_du_pont_indicators(self, path, sheet_name):
        self.parse_ratios(path, sheet_name, 'DuPont indicators', 'DuPontIndicators')

    def parse_ratios(self, path, sheet_name, ratio_name, table_name):
        if sheet_name not in self.available_sheets:
            raise ValueError("Available sheet names: QS, YS")
        excel_sheet = get_sheet(path, sheet_name)
        company_id = self.get_company(path)
        curr_row = 200
        if ratio_name == 'DuPont indicators':
            curr_row = 225
        curr_column = 2
        ratios = [company_id]
        while curr_row < excel_sheet.nrows:
            if excel_sheet.cell(curr_row, curr_column).value == ratio_name:
                attributes_column = curr_column
                curr_column += 1
                dates_row = curr_row + 1
                curr_row += 2
                attributes = ['CompanyID', 'PeriodStart', 'PeriodEnd']
                while curr_column < excel_sheet.ncols:
                    date_value = excel_sheet.cell(dates_row, curr_column).value
                    if not date_value:
                        curr_column += 1
                        continue
                    period_start, period_end = get_start_end_date(date_value)
                    ratios += [period_start, period_end]

                    while excel_sheet.cell(curr_row, attributes_column).value != '':
                        attribute = excel_sheet.cell(curr_row, attributes_column).value
                        curr_value = excel_sheet.cell(curr_row, curr_column).value
                        attributes.append(attribute)
                        insert_float_value(ratios, curr_value)
                        curr_row += 1

                    DAL.utils.insert_values(table_name=table_name,
                                            columns=attributes,
                                            values=ratios)
                    attributes = ['CompanyID', 'PeriodStart', 'PeriodEnd']
                    ratios = [company_id]
                    curr_column += 1
                    curr_row = dates_row + 1
                break
            curr_row += 1

    def get_company(self, path):
        self.parse_company(path)
        excel_sheet = get_sheet(path, 'Info')
        value_column = 1
        name_row = 2
        company_name = excel_sheet.cell(name_row, value_column).value
        return DAL.utils.get_company_id_from_name(company_name)


if __name__ == "__main__":
    ep = ExcelParser()
    help = '''[path] [option]
    options
    -b QS - parse QS of balance sheet
    -b YS - parse YS of balance sheet
    -f QS - parse QS of financial ratio
    -f YS - parse YS of financial ratio
    -d QS - parse QS of Du Pont indicators
    -d YS - parse YS of Du Pont indicators'''

    functions = {'-b': ep.parse_balance_sheet,
                 '-f': ep.parse_financial_ratios,
                 '-d': ep.parse_du_pont_indicators
                 }
    if len(sys.argv) < 4:
        print(help)
    else:
        excel_file = sys.argv[1]
        sheet = sys.argv[3]
        try:
            functions[sys.argv[2]](excel_file, sheet)
        except ValueError as e:
            print(e)
