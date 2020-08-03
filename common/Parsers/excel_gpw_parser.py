import common.DAL.db_queries
from common.Utils.Errors import CompanyNotFoundError, ParseError
from common.Parsers.Common.dates import *
import xlrd


class ExcelGPWParser:
    def __init__(self):
        self.workbook = None

    def parse(self, path, end_date=None):
        self.workbook = xlrd.open_workbook(path)

        sheet_name = 'kap'
        excel_sheet = self.workbook.sheet_by_name(sheet_name)
        start_row = 8
        curr_row = start_row
        isin_column = 1
        headers_check_row = 4
        name_column = 2
        capitalization_column = 4
        values = []
        milion = 1e6

        end_date = self.get_date(end_date)

        if "isin" in excel_sheet.cell(headers_check_row, isin_column).value.lower() and "nazwa" in excel_sheet.cell(
                headers_check_row, name_column).value.lower():
            while curr_row < excel_sheet.nrows:
                isin = excel_sheet.cell(curr_row, isin_column).value
                name = excel_sheet.cell(curr_row, name_column).value
                value = excel_sheet.cell(curr_row, capitalization_column).value * milion
                try:
                    common.DAL.db_queries.insert_market_value(value, end_date, name, isin)
                except CompanyNotFoundError as err:
                    print(err)
                    common.DAL.db_queries.insert_company(company_name=name, company_isin=isin)
                    common.DAL.db_queries.insert_market_value(value, end_date, name, isin)
                curr_row = curr_row + 1
        elif "nazwa" in excel_sheet.cell(headers_check_row,
                                         isin_column).value.lower():  # case where name is in place of isin
            name_column = 1
            capitalization_column = 3
            while curr_row < excel_sheet.nrows:
                name = excel_sheet.cell(curr_row, name_column).value
                value = excel_sheet.cell(curr_row, capitalization_column).value * milion
                try:
                    common.DAL.db_queries.insert_market_value(value, end_date, name)
                except CompanyNotFoundError as err:
                    print(err)
                    common.DAL.db_queries.insert_company(company_name=name)
                    common.DAL.db_queries.insert_market_value(value, end_date, name)
                curr_row = curr_row + 1
        else:
            raise ParseError(path, '1: "ISIN" should be in B5 cell and "Nazwa" should be in C5 cell or 2: "Nazwa" '
                                   'should be in B5 cell')

    def get_date(self, end_date):
        if end_date is not None:
            return end_date
        sheet = self.workbook.sheet_by_index(0)
        for row_index in range(sheet.nrows):
            if end_date is not None:
                break
            values = sheet.row_values(row_index)
            for value in values:
                if end_date is not None:
                    break
                if 'Kapitalizacja' in value or 'capitalization' in value:
                    raise ValueError('Date not found')
                end_date = find_date_in_monthly_statistics(value) \
                    or find_date_in_quarterly_statistics(value) \
                    or find_date_in_halfyearly_statistics(value) \
                    or find_date_in_yearly_statistics(value)

        return end_date

