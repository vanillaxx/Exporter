import xlrd
import common.DAL.db_queries_insert
import common.DAL.db_queries_get
import datetime
from calendar import monthrange
from common.Utils.Errors import UniqueError, ParseError
from sqlite3 import IntegrityError
from common.DAL.db_queries_get import exactly_same_assets, exactly_same_assets_categories, \
    exactly_same_equity_liabilities, \
    exactly_same_equity_liabilities_categories, exactly_same_financial_ratios, exactly_same_dupont_indicators
from common.Utils.company_unification import Company
from common.Utils.parsing_result import ParsingResult
from common.Utils.unification_info import NotoriaUnificationInfo


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
    common.DAL.db_queries_insert.insert_ekd_section(ekd_section)
    common.DAL.db_queries_insert.insert_ekd_class(ekd_class)


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

        return Company(name=company_name, ticker=company_ticker, isin=isin, bloomberg=company_bloomberg,
                       ekd_section=ekd_section, ekd_class=ekd_class)

    def parse_balance_sheet(self, path, sheet_name, override=False, save=False):
        if sheet_name not in self.available_sheets:
            raise ParseError(path, "Available sheet names: QS, YS")
        excel_sheet = get_sheet(path, sheet_name)
        is_directory_import = not (override or save)
        company_id, unification_info = self.get_company_id_balance_sheet(path, is_directory_import)
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

                    if unification_info is not None:
                        data_to_insert = [
                            ("Assets", assets_attributes, assets),
                            ("EquityLiabilities", equity_liabilities_attributes, equity_liabilities),
                            ("AssetsCategories", assets_categories_attributes, assets_categories),
                            ("EquityLiabilitiesCategories", equity_liabilities_categories_attributes,
                             equity_liabilities_categories),
                        ]
                        for data in data_to_insert:
                            unification_info.add_data(table_name=data[0], columns=data[1], data=data[2])

                    else:
                        if override:
                            common.DAL.db_queries_insert.replace_values(table_name="Assets",
                                                                        columns=assets_attributes,
                                                                        values=assets)
                            common.DAL.db_queries_insert.replace_values(table_name="EquityLiabilities",
                                                                        columns=equity_liabilities_attributes,
                                                                        values=equity_liabilities)
                            common.DAL.db_queries_insert.replace_values(table_name="AssetsCategories",
                                                                        columns=assets_categories_attributes,
                                                                        values=assets_categories)
                            common.DAL.db_queries_insert.replace_values(table_name="EquityLiabilitiesCategories",
                                                                        columns=equity_liabilities_categories_attributes,
                                                                        values=equity_liabilities_categories)
                        elif save:
                            common.DAL.db_queries_insert.insert_values(table_name="Assets",
                                                                       columns=assets_attributes,
                                                                       values=assets)
                            common.DAL.db_queries_insert.insert_values(table_name="EquityLiabilities",
                                                                       columns=equity_liabilities_attributes,
                                                                       values=equity_liabilities)
                            common.DAL.db_queries_insert.insert_values(table_name="AssetsCategories",
                                                                       columns=assets_categories_attributes,
                                                                       values=assets_categories)
                            common.DAL.db_queries_insert.insert_values(table_name="EquityLiabilitiesCategories",
                                                                       columns=equity_liabilities_categories_attributes,
                                                                       values=equity_liabilities_categories)
                        else:

                            try:
                                common.DAL.db_queries_insert.insert_values_without_ignore(table_name="Assets",
                                                                                          columns=assets_attributes,
                                                                                          values=assets)
                            except IntegrityError:
                                if not exactly_same_assets(assets_attributes, assets):
                                    if not overlapping_assets:
                                        init_overlapping_info(overlapping_assets, "Assets", assets_attributes)
                                    overlapping_assets["values"].append(assets)

                            try:
                                common.DAL.db_queries_insert.insert_values_without_ignore(
                                    table_name="EquityLiabilities",
                                    columns=equity_liabilities_attributes,
                                    values=equity_liabilities)
                            except IntegrityError:
                                if not exactly_same_equity_liabilities(equity_liabilities_attributes,
                                                                       equity_liabilities):
                                    if not overlapping_equity_liabilities:
                                        init_overlapping_info(overlapping_equity_liabilities,
                                                              "EquityLiabilities",
                                                              equity_liabilities_attributes)
                                    overlapping_equity_liabilities["values"].append(equity_liabilities)

                            try:
                                common.DAL.db_queries_insert.insert_values_without_ignore(table_name="AssetsCategories",
                                                                                          columns=assets_categories_attributes,
                                                                                          values=assets_categories)
                            except IntegrityError:
                                if not exactly_same_assets_categories(assets_categories_attributes, assets_categories):
                                    if not overlapping_assets_categories:
                                        init_overlapping_info(overlapping_assets_categories,
                                                              "AssetsCategories",
                                                              assets_categories_attributes)
                                    overlapping_assets_categories["values"].append(assets_categories)

                            try:
                                common.DAL.db_queries_insert.insert_values_without_ignore(
                                    table_name="EquityLiabilitiesCategories",
                                    columns=equity_liabilities_categories_attributes,
                                    values=equity_liabilities_categories)
                            except IntegrityError:
                                if not exactly_same_equity_liabilities_categories(
                                        equity_liabilities_categories_attributes,
                                        equity_liabilities_categories):
                                    if not overlapping_equity_liabilities_categories:
                                        init_overlapping_info(overlapping_equity_liabilities_categories,
                                                              "EquityLiabilitiesCategories",
                                                              equity_liabilities_categories_attributes)
                                    overlapping_equity_liabilities_categories["values"].append(
                                        equity_liabilities_categories)

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
        overlapping_data = []
        if overlapping_assets:
            overlapping_data.append(overlapping_assets)
        if overlapping_assets_categories:
            overlapping_data.append(overlapping_assets_categories)
        if overlapping_equity_liabilities:
            overlapping_data.append(overlapping_equity_liabilities)
        if overlapping_equity_liabilities_categories:
            overlapping_data.append(overlapping_equity_liabilities_categories)
        if overlapping_data and not is_directory_import:
            raise UniqueError(*overlapping_data)
        if unification_info is not None and unification_info.data:
            return ParsingResult([unification_info])
        return None

    def parse_financial_ratios(self, path, sheet_name, override=False, save=False):
        return self.parse_ratios(path, sheet_name, 'Financial ratios', 'FinancialRatios', override, save)

    def parse_du_pont_indicators(self, path, sheet_name, override=False, save=False):
        return self.parse_ratios(path, sheet_name, 'DuPont indicators', 'DuPontIndicators', override, save)

    def parse_ratios(self, path, sheet_name, ratio_name, table_name, override=False, save=False):
        function_mapping = {'FinancialRatios': exactly_same_financial_ratios,
                            'DuPontIndicators': exactly_same_dupont_indicators}
        if sheet_name not in self.available_sheets:
            raise ParseError(path, "Available sheet names: QS, YS")
        excel_sheet = get_sheet(path, sheet_name)
        is_directory_import = not (override or save)
        company_id, unification_info = self.get_company_id_balance_sheet(path, is_directory_import)
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
                    if unification_info is not None:
                        unification_info.add_data(table_name=table_name, columns=attributes, data=ratios)

                    else:
                        if override:
                            common.DAL.db_queries_insert.replace_values(table_name=table_name,
                                                                        columns=attributes,
                                                                        values=ratios)
                        elif save:
                            common.DAL.db_queries_insert.insert_values(table_name=table_name,
                                                                       columns=attributes,
                                                                       values=ratios)
                        else:
                            try:
                                common.DAL.db_queries_insert.insert_values_without_ignore(table_name=table_name,
                                                                                          columns=attributes,
                                                                                          values=ratios)
                            except IntegrityError:
                                if not function_mapping[table_name](attributes, ratios):
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
        if overlapping_ratios and not is_directory_import:
            raise UniqueError(overlapping_ratios)
        if unification_info is not None and unification_info.data:
            return ParsingResult([unification_info])
        return None


    def get_company_id_balance_sheet(self, path, is_directory_import):
        company = self.parse_company(path)

        company_id, possible_companies = common.DAL.db_queries_get.get_company(company)

        if company_id is None and (not possible_companies or is_directory_import):
            company_id = common.DAL.db_queries_insert.insert_company(company)
            return company_id, None

        elif possible_companies:
            return None, NotoriaUnificationInfo(company, possible_matches=possible_companies, data=[])
        else:
            return company_id, None


ep = ExcelParser()
functions = {'bs': ep.parse_balance_sheet,
             'fr': ep.parse_financial_ratios,
             'dp': ep.parse_du_pont_indicators
             }
