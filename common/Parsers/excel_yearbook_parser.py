import xlrd
import re
from datetime import date
from common.DAL.db_queries import insert_market_value, insert_company, get_company_id
from common.Utils.Errors import CompanyNotFoundError, ParseError


class ExcelYearbookParser:
    def __init__(self):
        self.workbook = None
        self.date = None

    def parse(self, pdf_path, year=None):
        self.workbook = xlrd.open_workbook(pdf_path)
        self.date, sheet_names = self.get_date_and_sheet_names(year)
        data = [self.parse_sheet(sheet_name) for sheet_name in sheet_names]
        return data

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
                self.save_value_to_database(name, isin, market_value)
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

    def save_value_to_database(self, company_name, company_isin, market_value):
        company_id = get_company_id(company_name=company_name, company_isin=company_isin)
        if company_id is None:
            company_id = insert_company(company_name=company_name, company_isin=company_isin)

        insert_market_value(company_id, market_value, self.date)

