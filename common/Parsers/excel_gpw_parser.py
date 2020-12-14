from common.Parsers.gpw_parser import GPWParser
from common.Utils.Errors import ParseError, UniqueError, DateError
from common.Utils.dates import *
from common.Utils.gpw_utils import save_value_to_database
import xlrd

from common.Utils.parsing_result import ParsingResult


class ExcelGPWParser(GPWParser):
    def __init__(self, save, override):
        self.workbook = None
        self.save = save
        self.override = override
        self.path = None

    def parse(self, path, end_date=None):
        self.path = path
        self.workbook = xlrd.open_workbook(path, on_demand=True)

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
        unification_info = []
        overlapping_info = {}

        end_date = self.get_date(end_date)

        if "isin" in excel_sheet.cell(headers_check_row, isin_column).value.lower() and "nazwa" in excel_sheet.cell(
                headers_check_row, name_column).value.lower():
            while curr_row < excel_sheet.nrows:
                isin = excel_sheet.cell(curr_row, isin_column).value
                name = excel_sheet.cell(curr_row, name_column).value
                value = excel_sheet.cell(curr_row, capitalization_column).value * milion

                save_value_to_database(name, isin, value, end_date, overlapping_info, unification_info,
                                       self.save, self.override)

                curr_row = curr_row + 1

        elif "nazwa" in excel_sheet.cell(headers_check_row,
                                         isin_column).value.lower():  # case where name is in place of isin
            name_column = 1
            capitalization_column = 3
            while curr_row < excel_sheet.nrows:
                name = excel_sheet.cell(curr_row, name_column).value
                value = excel_sheet.cell(curr_row, capitalization_column).value * milion
                isin = None

                save_value_to_database(name, isin, value, end_date, overlapping_info, unification_info,
                                       self.save, self.override)

                curr_row = curr_row + 1
        else:
            raise ParseError(path, '1: "ISIN" should be in B5 cell and "Nazwa" should be in C5 cell or 2: "Nazwa" '
                                   'should be in B5 cell')

        if unification_info:
            if overlapping_info and overlapping_info['values']:
                result = ParsingResult(unification_info=unification_info, overlapping_info=overlapping_info)
            else:
                result = ParsingResult(unification_info=unification_info)
            return result

        if overlapping_info and overlapping_info['values']:
            raise UniqueError(overlapping_info)

        return None

    def get_date(self, end_date):
        if end_date:
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
                    raise DateError(self.path)
                end_date = find_date_in_monthly_statistics(value) \
                    or find_date_in_quarterly_statistics(value) \
                    or find_date_in_halfyearly_statistics(value) \
                    or find_date_in_yearly_statistics(value)

        if not end_date:
            raise DateError(self.path)
        return end_date
