import camelot
import fitz
import re
import collections
import pandas as pd
from datetime import date

from common.Utils.Errors import UniqueError, DateError
from common.Utils.gpw_utils import save_value_to_database
from common.Utils.parsing_result import ParsingResult


class PdfYearbookParser:
    table_title = 'Spółki według wartości rynkowej'
    old_table_title = 'Spółki o największej wartości rynkowej'
    market = ['Główny Rynek GPW',
              'Giełda Papierów Wartościowych w Warszawie']
    data_year, yearbook_year = None, None
    skip = [
        f'Spółki według wartości rynkowej (na koniec {data_year} r.)',
        f'Spółki według wartości rynkowej (na koniec {data_year} r.) (cd.)',
        f'Spółki o największej wartości rynkowej na koniec {data_year} r.'
    ]
    end_columns = [
        'Spółki krajowe', 'Spólki krajowe razem:', 'Spólki zagraniczne',
        'Spólki zagraniczne razem:', 'Razem spółki krajowe',
        'Razem spółki zagraniczne', 'Razem'
    ]
    stop_parsing = [
        'Razem spółki zagraniczne',
        'Spółki zagraniczne razem:'
        f'{yearbook_year} Rocznik Giełdowy'
    ]
    year_pattern = r'Rocznik Giełdowy (?P<yearbook_year>\d{4})|Dane statystyczne za rok (?P<data_year>\d{4})'
    market_value_column = 'Wartość rynkowa'
    company_column = 'Spółka'

    def __init__(self, save, override):
        self.doc = None
        self.pdf_path = None
        self.date = None
        self.overlapping_info = {}
        self.unification_info = []
        self.save = save
        self.override = override

    # TODO errore
    def parse(self, pdf_path, data_date=None):
        self.pdf_path = pdf_path
        self.doc = fitz.Document(pdf_path)

        if data_date:
            self.date = data_date
        else:
            self.find_data_date()
            self.date = date(int(self.data_year), month=12, day=31)

        dataframes = [self.process_page(page, page_num) for page_num, page in enumerate(self.doc.pages())]
        dataframes = [dataframe for dataframe in dataframes if dataframe is not None]
        if not dataframes:
            raise ValueError('No data found')

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

    def find_data_date(self):
        for page in self.doc.pages():
            text = page.getText()
            match = re.search(self.year_pattern, text)
            if match:
                if match.group('yearbook_year'):
                    self.yearbook_year = match.group('yearbook_year')
                if match.group('data_year'):
                    self.data_year = match.group('data_year')
            if self.yearbook_year and self.data_year:
                return

        if self.yearbook_year and self.data_year is None:
            self.data_year = int(self.yearbook_year) - 1
        elif self.yearbook_year is None and self.data_year is None:
            raise DateError(self.pdf_path)

    def process_page(self, page, page_num):
        media_box = page.MediaBox
        x_max, x_min, y_max = media_box.x1, 0, 0
        title_rect = page.searchFor(self.table_title, hit_max=1) or page.searchFor(self.old_table_title, hit_max=1)
        if title_rect:
            # print(page_num)
            next_page = page_num + 1 if page_num + 1 < self.doc.pageCount else self.doc.pageCount
            gpw = [page.searchFor(market, hit_max=1) or self.doc.loadPage(next_page).searchFor(market, hit_max=1)
                   for market in self.market]
            gpw = [item for item in gpw if item]
            if not gpw and int(self.data_year) > 2001:
                return

            bottom_left = title_rect[0].bottom_left
            table_area = [x_min, media_box.y1 - bottom_left.y, x_max, y_max]
            table_area = ','.join('%f' % coord for coord in table_area)

            tables = camelot.read_pdf(self.pdf_path, pages=str(page_num + 1), flavor='stream', table_areas=[table_area])
            if tables:
                return self.parse_table(tables[0])

    def parse_table(self, table):
        df = table.df
        rows_number = len(df)
        columns_num = len(df.columns)

        pattern = re.compile(r'(?P<index>\d+) (?P<company>\w+)\*?')
        columns = ["" for _ in range(columns_num)]
        columns_parsed = False
        drop_index = None

        for row, value in enumerate(df.values):
            if value.any() in self.stop_parsing:
                drop_index = row
                break

            match = pattern.match(value[0]) or pattern.match(value[1])
            if match:
                index = match.group('index')
                company = match.group('company')
                value[0] = index
                value[1] = company
                df.loc[[row], 0:1] = index, company

            if not value[0].isdigit():
                if not columns_parsed:
                    for col, val in enumerate(value):
                        if val in self.end_columns:
                            break
                        if val not in self.skip and not val.isdigit():
                            tmp = columns[col] + ' ' + val
                            columns[col] = tmp
                df = df.drop(row)

            else:
                columns_parsed = True
                counter = collections.Counter(value)
                if counter[''] >= 7:
                    df = df.drop(row)

        if drop_index:
            indexes_to_drop = range(drop_index, rows_number)
            df = df.drop(indexes_to_drop)

        for col, name in enumerate(columns):
            name = name.strip()
            name = re.sub(r'\t', ' ', name)
            columns[col] = re.sub(r',', '', name)

        column_info = [(name, index) for index, name in enumerate(columns) if re.search(self.market_value_column, name)]
        if column_info:
            market_value_column_name, index = column_info[0]
        else:
            raise ValueError('Invalid column names: Market Value column not found.')

        multipliers = {
            'mln': 1000000,
            'mil': 1000000,
            'tys': 1000
        }
        multiplier = 1
        found_multipliers = [multiplier for multiplier in multipliers.keys() if multiplier in market_value_column_name]
        if found_multipliers:
            multiplier = multipliers[found_multipliers[0]]

        columns[index] = self.market_value_column
        df = df.rename(columns=lambda s: columns[s])

        if self.company_column in df.columns and self.market_value_column in df.columns:
            new_df = df[[self.company_column, self.market_value_column]].replace(regex=r'\*', value='')
            new_df[self.market_value_column] = new_df[self.market_value_column] \
                .replace(regex=' ', value='') \
                .replace(regex=',', value='.') \
                .astype('float') \
                .mul(multiplier)

            new_df.apply(self.save_value_to_database, axis=1)

            return new_df
        else:
            raise ValueError('Invalid column names')

    def save_value_to_database(self, row):
        company_name = row[self.company_column]
        market_value = row[self.market_value_column]
        company_isin = None

        save_value_to_database(company_name, company_isin, market_value, self.date,
                               self.overlapping_info, self.unification_info, self.save, self.override)
