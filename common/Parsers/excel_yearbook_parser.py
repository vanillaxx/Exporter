import xlrd
import re
from datetime import date

from common.Utils.Errors import UniqueError
from common.Utils.gpw_utils import save_value_to_database
from common.Utils.parsing_result import ParsingResult


class ExcelYearbookParser:
    def __init__(self):
        self.workbook = None
        self.date = None
        self.unification_info = []
        self.overlapping_info = {}

    def parse(self, pdf_path, year=None):
        self.workbook = xlrd.open_workbook(pdf_path)
        self.date, sheet_names = self.get_date_and_sheet_names(year)
        data = [self.parse_sheet(sheet_name) for sheet_name in sheet_names]
        if not data:
            raise ValueError('No data found')

        if self.overlapping_info and self.overlapping_info['values']:
            raise UniqueError(self.overlapping_info)

        if self.unification_info:
            return ParsingResult(unification_info=self.unification_info)

    def get_date_and_sheet_names(self, year):
        sheet = self.workbook.sheet_by_index(0)
        sheet_name_column = 'tab'
        market_value_row = 'market value'
        year_pattern = r'(\d{4})'

        sheet_names = []
        for row_index in range(sheet.nrows):
            sheet_name = None
            for value in sheet.row_values(row_index):
                if year is None:
                    match = re.search(year_pattern, value)
                    if match:
                        year = match.group(0)
                if sheet_name_column in value.lower():
                    sheet_name = value.strip()
                elif market_value_row in value.lower():
                    sheet_names.append(sheet_name)

        if not sheet_names:
            raise ValueError('Sheet names not found')
        if year is None:
            raise ValueError('Date not found')

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

            if name and market_value:
                market_value = market_value * multiplier
                save_value_to_database(name, isin, market_value, self.date, self.overlapping_info, self.unification_info)
                data.append([name, isin, market_value])
        return data

    @staticmethod
    def get_indexes(sheet, row_index):
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
            raise ValueError('Columns not found')

        return company_column, isin_column, market_value_column
