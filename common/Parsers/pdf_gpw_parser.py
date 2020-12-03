import camelot
import fitz
import collections
import numpy as np

from common.Parsers.gpw_parser import GPWParser
from common.Utils.Errors import UniqueError, DateError, ParseError
from common.Utils.gpw_utils import save_value_to_database, df_with_new_indexes, check_if_data_correct
from common.Utils.dates import *
from common.Utils.parsing_result import ParsingResult


class PdfGPWParser(GPWParser):
    table_title = 'Spółki krajowe według kapitalizacji'
    skip = [
        table_title,
        'Domestic companies by market capitalisation (month-end)',
        'Domestic companies by market capitalisation (eop)',
        'Domestic companies by market capitalisation',
        'Domestic companies by market capitalization'
    ]
    # end = [
    #     'Biuletyn Statystyczny GPW'
    # ]
    stop_parsing = [
        'Biuletyn Statystyczny GPW',
        'Statystyki roczne GPW'
    ]
    isin_code_column = 'ISIN'
    capitalisation_value_column = 'Kapitalizacja'
    company_column = 'Nazwa'

    def __init__(self, save, override):
        self.doc = None
        self.pdf_path = None
        self.date = None
        self.overlapping_info = {}
        self.unification_info = []
        self.save = save
        self.override = override
        self.warnings = []

    def parse(self, pdf_path, data_date=None):
        self.pdf_path = pdf_path
        self.doc = fitz.Document(pdf_path)

        self.date = self.find_data_date(data_date)

        dataframes = [self.process_page(page, page_num) for page_num, page in enumerate(self.doc.pages())]
        dataframes = [dataframe for dataframe in dataframes if dataframe is not None]
        if not dataframes:
            raise ParseError(self.pdf_path, 'No data found. Probably problems with encoding.')

        if self.unification_info:
            if self.overlapping_info and self.overlapping_info['values']:
                result = ParsingResult(unification_info=self.unification_info,
                                       overlapping_info=self.overlapping_info)
            else:
                result = ParsingResult(unification_info=self.unification_info)
            return result

        if self.overlapping_info and self.overlapping_info['values']:
            raise UniqueError(self.overlapping_info)

        if self.warnings:
            return ParsingResult(warnings=self.warnings)

        return None

    def find_data_date(self, data_date):
        if data_date:
            return data_date

        page = self.doc[0]
        text = page.getText()
        data_date = find_date_in_monthly_statistics(text) or find_date_in_quarterly_statistics(text) \
            or find_date_in_halfyearly_statistics(text) or find_date_in_yearly_statistics_pdf(page, text)
        if data_date is None:
            raise DateError(self.pdf_path)
        else:
            return data_date

    def process_page(self, page, page_num):
        media_box = page.MediaBox
        x_max, x_min, y_max = media_box.x1, 0, 0
        title_rect = page.searchFor(self.table_title, hit_max=1)
        if title_rect:
            # print(page_num)
            bottom_left = title_rect[0].bottom_left
            table_area = [x_min, media_box.y1 - bottom_left.y, x_max, y_max]
            table_area = ','.join('%f' % coord for coord in table_area)

            tables = camelot.read_pdf(self.pdf_path, pages=str(page_num + 1), flavor='stream', table_areas=[table_area])
            if tables:
                return self.parse_table(tables[0], page_num + 1)
        else:
            return None

    # TODO refactor
    def parse_table(self, table, page_num):
        df = table.df
        rows_number = len(df)
        columns = ['' for _ in range(15)]
        columns_parsed = False
        isin_pattern = re.compile(r'(?P<index>\d+) (?P<isin>([A-Z]{2})([A-Z0-9]{9})([0-9]))')
        name_pattern = re.compile(r'(?P<index>\d+) (?P<name>\w+)\*?')
        name_pattern2 = re.compile(r'(?P<name>\w+)\n(?P<index>\d+)')
        name_pattern3 = re.compile(r'(?P<index>\d+)\n(?P<name>\w+)')
        drop_index = None
        for row, value in enumerate(df.values):
            if np.in1d(self.stop_parsing, value).any():
                drop_index = row
                break
            match_isin = isin_pattern.match(value[0])
            match_name_old = name_pattern.match(value[0]) or name_pattern2.match(value[0]) or name_pattern3.match(
                value[0])
            match_name = name_pattern.match(value[1]) or name_pattern.match(value[2])

            if match_isin:
                isin = match_isin.group('isin')
                value[0] = isin
                df.loc[[row], 0] = isin
                columns_parsed = True

            elif value[0].isdigit() and re.compile(r'\w+').match(value[1]):
                columns_parsed = True
                if not re.match(r'^\s*$', columns[1]) and columns[1] != self.company_column:
                    df.loc[[row], 0] = value[1]
                    columns[0] = self.company_column
                else:
                    columns[1] = self.company_column

            elif match_name_old:
                columns_parsed = True
                pattern = re.compile(r'^\s*$')

                if not pattern.match(columns[1]) and columns[1] != self.company_column:
                    df.loc[[row], 0] = match_name_old.group('name')
                    columns[0] = self.company_column

                else:
                    columns[1] = self.company_column
                    df.loc[[row], 1] = match_name_old.group('name')
                    df.loc[[row], 0] = match_name_old.group('index')

            elif match_name:
                columns_parsed = True
                index = match_name.group('index')
                name = match_name.group('name')
                value[1] = index
                value[2] = name
                df.loc[[row], 1:2] = index, name

            elif value[1].isdigit():
                columns_parsed = True
                counter = collections.Counter(value)
                if counter[''] >= 7:
                    df = df.drop(row)
            else:
                if not columns_parsed:
                    for col, val in enumerate(value):
                        if val not in self.skip and not val.isdigit():
                            tmp = columns[col] + ' ' + val
                            columns[col] = tmp
                df = df.drop(row)

        if drop_index:
            indexes_to_drop = range(drop_index, rows_number)
            df = df.drop(indexes_to_drop)

        df.replace('', np.nan, inplace=True)
        df = df.dropna(how='all', axis='columns')

        index = [index for index, val in enumerate(columns) if val.strip() == 'PLN']
        if index:
            columns[index[0]] = ''

        df.columns = range(0, len(df.columns))

        for col, name in enumerate(columns):
            name = name.strip()
            name = re.sub(r'[\t\n]', ' ', name)
            columns[col] = re.sub(r'\s\s+', ' ', name)
        columns = [name for name in columns if name]

        new_columns = [self.isin_code_column, self.company_column, self.capitalisation_value_column]
        multiplier = 1e6
        for new_name in new_columns:
            column_info = [(name, index) for index, name in enumerate(columns) if new_name in name]
            if column_info:
                column_name, index = column_info[0]
                if new_name == self.capitalisation_value_column:
                    if 'mln' or 'mil' in column_name:
                        multiplier = 1000000
                    elif 'tys' in column_name:
                        multiplier = 1000
                columns[index] = new_name

        if not all(name in columns for name in new_columns) and \
                (self.company_column not in columns or self.capitalisation_value_column not in columns):
            raise ParseError(self.pdf_path, 'Invalid column names.')

        columns = columns + ['', '']
        df = df.rename(columns=lambda s: columns[s])

        new_columns = [name for name in new_columns if name in df.columns]

        new_df = df[new_columns].replace(regex=r'\*', value='')
        new_df[self.capitalisation_value_column] = new_df[self.capitalisation_value_column] \
            .replace(regex=r'\s+', value='') \
            .replace(regex=',', value='.')
        new_df = df_with_new_indexes(new_df)

        new_df.apply(self.save_value_to_database, axis=1, args=(multiplier, page_num))
        return new_df

    def save_value_to_database(self, row, multiplier, page_num):
        row_index = row.name
        company_name = row[self.company_column]
        company_isin = row.get(self.isin_code_column)
        market_value = row[self.capitalisation_value_column]

        market_value = check_if_data_correct(warnings=self.warnings, row_index=row_index, page_num=page_num,
                                             company_name=company_name, company_isin=company_isin,
                                             market_value=market_value, multiplier=multiplier)

        if market_value is not None:
            save_value_to_database(company_name, company_isin, market_value, self.date,
                                   self.overlapping_info, self.unification_info, self.save, self.override)
