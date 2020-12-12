import xlrd
import re
from datetime import date

from common.Parsers.gpw_parser import GPWParser
from common.Utils.Errors import UniqueError, DateError, ParseError
from common.Utils.gpw_utils import save_value_to_database
from common.Utils.parsing_result import ParsingResult


class ExcelYearbookParser(GPWParser):
    def __init__(self, save, override):
        self.workbook = None
        self.date = None
        self.unification_info = []
        self.overlapping_info = {}
        self.save = save
        self.override = override
        self.path = None

    def parse(self, path, data_date=None):
        self.path = path
        self.workbook = xlrd.open_workbook(self.path, on_demand=True)
        self.date, sheet_names = self.get_date_and_sheet_names(data_date)
        data = [self.parse_sheet(sheet_name) for sheet_name in sheet_names]
        data = [d for d in data if d]
        if not data:
            raise ParseError(self.path, 'No data found.')

        if self.unification_info:
            if self.overlapping_info and self.overlapping_info['values']:
                result = ParsingResult(unification_info=self.unification_info,
                                       overlapping_info=self.overlapping_info)
            else:
                result = ParsingResult(unification_info=self.unification_info)
            return result

        if self.overlapping_info and self.overlapping_info['values']:
            raise UniqueError(self.overlapping_info)

        return None

    def get_date_and_sheet_names(self, data_date):
        sheet = self.workbook.sheet_by_index(0)
        sheet_name_column = 'tab'
        market_value_row = 'market value'
        year_pattern = r'(\d{4})'

        year = data_date
        sheet_names = []
        for row_index in range(sheet.nrows):
            sheet_name = None
            for value in sheet.row_values(row_index):
                if not year:
                    match = re.search(year_pattern, value)
                    if match:
                        year = match.group(0)
                if sheet_name_column in value.lower():
                    sheet_name = value.strip()
                elif market_value_row in value.lower():
                    sheet_names.append(sheet_name)

        if not sheet_names:
            raise ParseError(self.path, 'Sheet names not found.')
        if year is None:
            raise DateError(self.path)

        if not data_date:
            data_date = date(int(year), month=12, day=31)
        return data_date, sheet_names

    def parse_sheet(self, sheet_name):
        sheet = self.workbook.sheet_by_name(sheet_name)

        columns_names_row = 2
        company_column, isin_column, market_value_column = self.get_indexes(sheet, columns_names_row)

        start_row = columns_names_row + 1
        multiplier = 1e6

        data = []
        for row_index in range(start_row, sheet.nrows):
            row = sheet.row_values(row_index)
            name = row[company_column]
            market_value = row[market_value_column]
            isin = None
            if isin_column is not None:
                isin = row[isin_column]

            if name and market_value is not None:
                market_value = market_value * multiplier
                save_value_to_database(name, isin, market_value, self.date, self.overlapping_info,
                                       self.unification_info, self.save, self.override)
                data.append([name, isin, market_value])
        return data

    def get_indexes(self, sheet, row_index):
        company = ['spółka', 'company']
        isin = 'isin'
        market_value = ['wartość rynkowa', 'market value']
        currency = ['zł', 'pln']

        company_column, isin_column, market_value_column = None, None, None

        for col_index in range(sheet.ncols):
            cell_value = sheet.cell_value(row_index, col_index).lower()
            if any(value in cell_value for value in company):
                company_column = col_index
            elif isin in cell_value:
                isin_column = col_index
            elif any(value in cell_value for value in market_value) and any(value in cell_value for value in currency):
                market_value_column = col_index

        if company_column is None or market_value_column is None:
            raise ParseError(self.path, 'Columns not found.')

        return company_column, isin_column, market_value_column
