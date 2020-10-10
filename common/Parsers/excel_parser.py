import xlrd
import common.DAL.db_queries
import sys
import datetime
from calendar import monthrange
import re
from common.Utils.Errors import UniqueError, ParseError
from sqlite3 import IntegrityError


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
    common.DAL.db_queries.insert_ekd_section(ekd_section)
    common.DAL.db_queries.insert_ekd_class(ekd_class)


def insert_float_value(where, value):
    if value:
        where.append(float(value))
    else:
        where.append(0.0)


def init_overlapping_info(overlapping_info, table_name, columns):
    overlapping_info["table_name"] = table_name
    overlapping_info["columns"] = columns
    overlapping_info["values"] = []


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
        isin_row = 17
        isin_column = 3
        ticker_row = 12
        bloomberg_row = 16
        ekd_row = 25
        if excel_sheet.cell(name_row, attribute_column).value == 'Nazwa':
            company_name = excel_sheet.cell(name_row, value_column).value
        else:
            raise ParseError(path, '(A3=Nazwa) of company should be in B3 cell')
        if excel_sheet.cell(isin_row, isin_column).value == 'ISIN':
            isin = excel_sheet.cell(isin_row, isin_column + 1).value
        else:
            raise ParseError(path, '(D18=ISIN) of company should be in E18 cell')
        if excel_sheet.cell(ticker_row, attribute_column).value == 'TICKER':
            company_ticker = excel_sheet.cell(ticker_row, value_column).value
        else:
            raise ParseError(path, '(A13=TICKER) of company should be in B13 cell')
        if excel_sheet.cell(bloomberg_row, attribute_column).value == 'Bloomberg':
            company_bloomberg = excel_sheet.cell(bloomberg_row, value_column).value
        else:
            raise ParseError(path, '(A17=Bloomberg) of company should be in B17 cell')
        if excel_sheet.cell(ekd_row, attribute_column).value == 'EKD 1':
            company_ekd = excel_sheet.cell(ekd_row, value_column).value
        else:
            raise ParseError(path, '(A26=EKD 1) of company should be in B26 cell')

        ekd_section, ekd_class = parse_ekd(company_ekd)
        insert_ekd_data(ekd_section, ekd_class)
        common.DAL.db_queries.insert_full_company(company_name, isin, company_ticker, company_bloomberg,
                                                  ekd_section, ekd_class)

    def parse_balance_sheet(self, path, sheet_name):
        if sheet_name not in self.available_sheets:
            raise ParseError(path, "Available sheet names: QS, YS")
        excel_sheet = get_sheet(path, sheet_name)
        company_id = self.get_company_id_balance_sheet(path)
        curr_row = 0
        curr_column = 2
        assets = [company_id]
        assets_categories = [company_id]
        equity_liabilities = [company_id]
        equity_liabilities_categories = [company_id]
        overlapping_assets = {}
        overlapping_assets_categories = {}
        overlapping_equity_liabilities = {}
        overlapping_equity_liabilities_categories = {}
        while curr_row < excel_sheet.nrows:
            if excel_sheet.cell(curr_row, curr_column).value == 'Balance sheet':
                attributes_column = curr_column
                curr_column += 1
                dates_row = curr_row + 1
                sum_row = dates_row + 1
                curr_row += 3
                assets_attributes = ['CompanyID', 'Date']
                equity_liabilities_categories_attributes = ['CompanyID', 'Date']
                assets_categories_attributes = ['CompanyID', 'Date']
                equity_liabilities_attributes = ['CompanyID', 'Date']
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

                    try:
                        common.DAL.db_queries.insert_values_without_ignore(table_name="Assets",
                                                                           columns=assets_attributes,
                                                                           values=assets)
                    except IntegrityError:
                        if not overlapping_assets:
                            init_overlapping_info(overlapping_assets, "Assets", assets_attributes)
                        overlapping_assets["values"].append(assets)

                    try:
                        common.DAL.db_queries.insert_values_without_ignore(table_name="EquityLiabilities",
                                                                           columns=equity_liabilities_attributes,
                                                                           values=equity_liabilities)
                    except IntegrityError:
                        if not overlapping_equity_liabilities:
                            init_overlapping_info(overlapping_equity_liabilities,
                                                  "EquityLiabilities",
                                                  equity_liabilities_attributes)
                        overlapping_equity_liabilities["values"].append(equity_liabilities)

                    try:
                        common.DAL.db_queries.insert_values_without_ignore(table_name="AssetsCategories",
                                                                           columns=assets_categories_attributes,
                                                                           values=assets_categories)
                    except IntegrityError:
                        if not overlapping_assets_categories:
                            init_overlapping_info(overlapping_assets_categories,
                                                  "AssetsCategories",
                                                  assets_categories_attributes)
                        overlapping_assets_categories["values"].append(assets_categories)

                    try:
                        common.DAL.db_queries.insert_values_without_ignore(table_name="EquityLiabilitiesCategories",
                                                                           columns=equity_liabilities_categories_attributes,
                                                                           values=equity_liabilities_categories)
                    except IntegrityError:
                        if not overlapping_equity_liabilities_categories:
                            init_overlapping_info(overlapping_equity_liabilities_categories,
                                                  "EquityLiabilitiesCategories",
                                                  equity_liabilities_categories_attributes)
                        overlapping_equity_liabilities_categories["values"].append(equity_liabilities_categories)

                    assets_attributes = ['CompanyID', 'Date']
                    assets_categories_attributes = ['CompanyID', 'Date']
                    equity_liabilities_attributes = ['CompanyID', 'Date']
                    equity_liabilities_categories_attributes = ['CompanyID', 'Date']
                    assets = [company_id]
                    equity_liabilities = [company_id]
                    assets_categories = [company_id]
                    equity_liabilities_categories = [company_id]
                    curr_column += 1
                    curr_row = sum_row + 1
                break
            curr_row += 1
        if overlapping_assets or overlapping_assets_categories or overlapping_equity_liabilities or overlapping_equity_liabilities_categories:
            raise UniqueError(overlapping_assets, overlapping_assets_categories, overlapping_equity_liabilities,
                              overlapping_equity_liabilities_categories)

    def parse_financial_ratios(self, path, sheet_name):
        self.parse_ratios(path, sheet_name, 'Financial ratios', 'FinancialRatios')

    def parse_du_pont_indicators(self, path, sheet_name):
        self.parse_ratios(path, sheet_name, 'DuPont indicators', 'DuPontIndicators')

    def parse_ratios(self, path, sheet_name, ratio_name, table_name):
        if sheet_name not in self.available_sheets:
            raise ParseError(path, "Available sheet names: QS, YS")
        excel_sheet = get_sheet(path, sheet_name)
        company_id = self.get_company_id_balance_sheet(path)
        curr_row = 200
        if ratio_name == 'DuPont indicators':
            curr_row = 225
        curr_column = 2
        ratios = [company_id]
        overlapping_ratios = {}
        while curr_row < excel_sheet.nrows:
            if excel_sheet.cell(curr_row, curr_column).value == ratio_name:
                attributes_column = curr_column
                curr_column += 1
                dates_row = curr_row + 1
                curr_row += 2
                attributes = ['CompanyID', 'Period start', 'Period end']
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

                    try:
                        common.DAL.db_queries.insert_values_without_ignore(table_name=table_name,
                                                                           columns=attributes,
                                                                           values=ratios)
                    except IntegrityError:
                        if not overlapping_ratios:
                            init_overlapping_info(overlapping_ratios,
                                                  table_name,
                                                  attributes)
                        overlapping_ratios["values"].append(ratios)

                    attributes = ['CompanyID', 'Period start', 'Period end']
                    ratios = [company_id]
                    curr_column += 1
                    curr_row = dates_row + 1
                break
            curr_row += 1
        if overlapping_ratios:
            raise UniqueError(overlapping_ratios)


    def get_company_id_balance_sheet(self, path):
        self.parse_company(path)
        excel_sheet = get_sheet(path, 'Info')
        value_column = 1
        name_row = 2
        isin_row = 17
        isin_column = 4
        ticker_row = 12
        company_name = excel_sheet.cell(name_row, value_column).value
        company_ticker = excel_sheet.cell(ticker_row, value_column).value
        company_isin = excel_sheet.cell(isin_row, isin_column).value
        return common.DAL.db_queries.get_company_id(company_name, company_ticker, company_isin)


ep = ExcelParser()
functions = {'bs': ep.parse_balance_sheet,
             'fr': ep.parse_financial_ratios,
             'dp': ep.parse_du_pont_indicators
             }

if __name__ == "__main__":
    help = '''[path] [option]
    options
    -b QS - parse QS of balance sheet
    -b YS - parse YS of balance sheet
    -f QS - parse QS of financial ratio
    -f YS - parse YS of financial ratio
    -d QS - parse QS of Du Pont indicators
    -d YS - parse YS of Du Pont indicators'''

    if len(sys.argv) < 3:
        print(help)
    elif sys.argv[2] == '-g':
        excel_file = sys.argv[1]
        end_date = sys.argv[3]
        pattern = re.compile("\d\d\d\d-\d\d-\d\d")
        if pattern.match(end_date):
            functions[sys.argv[2]](excel_file, end_date)
        else:
            print("Pass end date in format YYYY-MM-DD")
    else:
        excel_file = sys.argv[1]
        sheet = sys.argv[3]
        try:
            functions[sys.argv[2]](excel_file, sheet)
        except ValueError as e:
            print(e)
