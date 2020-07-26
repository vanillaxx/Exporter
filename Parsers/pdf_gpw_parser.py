import camelot
import fitz
import re
import collections
import pandas as pd
import numpy as np
from datetime import date, datetime
import calendar
import locale
from DAL.db_queries import insert_market_value, insert_company
from Utils.Errors import CompanyNotFoundError
from DAL.db_utils import set_up_database_tables


class PdfGPWParser:
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
    yearly_patterns = [
        r'Rok (?P<year>\d{4})',
        r'Year (?P<year>\d{4})',
        r'(?P<year>^\d{4})',
        r'(?P<year>\d{4}$)',
        r'\((?P<year>\d{4})\)',
        r'(?:Statystyki roczne GPW|WSE annual statistics) - (?P<year>\d{4})'
    ]
    halfyearly_patterns = [
        r'(?P<half>I|II) półrocze (?P<year>\d{4})',
        r'(?P<half>1st|2nd) Half(?:-year)? (?P<year>\d{4})',
        r'(?P<year>\d{4})H(?P<half>1|2)',
        r'(?:Biuletyn Półroczny GPW|WSE Halfyearly Bulletin) \((?P<half>1|2)/(?P<year>\d{4})\)'
    ]
    quarterly_patterns = [
        r'(?P<quarter>I|II|III|IV) (?:kwartał|kw\.) (?P<year>\d{4})',
        r'kw\. (?P<quarter>I|II|III|IV) (?P<year>\d{4})',
        r'(?P<quarter>1st|2nd|3rd|4th) Quarter (?P<year>\d{4})',
        r'Q(?P<quarter>1|2|3|4), (?P<year>\d{4})',
        r'(?P<quarter>1|2|3|4) Q (?P<year>\d{4})',
        r'(?:Biuletyn Kwartalny GPW|WSE Quarterly Bulletin) \((?P<quarter>1|2|3|4)/(?P<year>\d{4})\)',
        r'(?:Statystyki kwartalne GPW|WSE quarterly statistics) - (?P<quarter>1|2|3|4)/(?P<year>\d{4})'
    ]
    monthly_patterns = [
        r'(?P<date>(?:\()?(?:January|February|March|April|May|June|July|August|September|November|December)'
        r'(?:\))?(?:,)? \d{4})',
        r'(?P<pl_date>(?:\()?(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|listopad|grudzień)'
        r'(?:\))?(?:,)? \d{4})',
        r'(?:Biuletyn GPW|WSE Bulletin) \((?P<month>\d{1,2})/(?P<year>\d{4})\) '
    ]
    isin_code_column = 'ISIN'
    capitalisation_value_column = 'Kapitalizacja'
    company_column = 'Nazwa'

    def __init__(self):
        self.doc = None
        self.pdf_path = None
        self.date = None

    def parse(self, pdf_path, data_date=None):
        self.pdf_path = pdf_path
        self.doc = fitz.Document(pdf_path)

        if data_date is None:
            self.date = self.find_data_date()

        dataframes = [self.process_page(page, page_num) for page_num, page in enumerate(self.doc.pages())]
        dataframes = [dataframe for dataframe in dataframes if dataframe is not None]
        if dataframes:
            return pd.concat(dataframes, ignore_index=True)
        else:
            raise ValueError('No data found')

    # TODO errors
    def find_data_date(self):
        page = self.doc[0]
        text = page.getText()
        data_date = self.find_date_in_monthly_statistics(text) or self.find_date_in_quarterly_statistics(text) \
            or self.find_date_in_halfyearly_statistics(text) or self.find_date_in_yearly_statistics(page, text)
        if not data_date:
            raise ValueError('Date not found')
        else:
            return data_date

    def find_date_in_yearly_statistics(self, page, text):
        match = next(filter(bool, (re.search(pattern, text) for pattern in self.yearly_patterns)), None) \
                or self.search_for_year_using_page_dict(page)
        if match:
            year = int(match.group('year'))
            month = 12
            day = 31
            return date(year, month, day)
        else:
            return None

    @staticmethod
    def search_for_year_using_page_dict(page):
        page_dict = page.getText('dict')

        for block in page_dict['blocks']:
            for lines in block['lines']:
                for spans in lines['spans']:
                    text = spans['text']
                    match = re.match(r'(?P<year>\d{4}$)', text.strip())
                    if match:
                        return match

    # TODO errors
    def find_date_in_halfyearly_statistics(self, text):
        first_half = ['I', '1', '1st']
        second_half = ['II', '2', '2nd']

        match = next(filter(bool, (re.search(pattern, text) for pattern in self.halfyearly_patterns)), None)
        if match:
            year = int(match.group('year'))
            half = match.group('half')
            if half in first_half:
                month = 6
            elif half in second_half:
                month = 12
            else:
                raise ValueError('Invalid date(?)')
            day = calendar.monthrange(year, month)[1]
            return date(year, month, day)
        else:
            return None

    # TODO errors
    def find_date_in_quarterly_statistics(self, text):
        first = ['I', '1', '1st']
        second = ['II', '2', '2nd']
        third = ['III', '3', '3rd']
        fourth = ['IV', '4', '4th']

        match = next(filter(bool, (re.search(pattern, text) for pattern in self.quarterly_patterns)), None)
        if match:
            year = int(match.group('year'))
            quarter = match.group('quarter')
            if quarter in first:
                month = 3
            elif quarter in second:
                month = 6
            elif quarter in third:
                month = 9
            elif quarter in fourth:
                month = 12
            else:
                raise ValueError('Invalid date(?)')
            day = calendar.monthrange(year, month)[1]
            return date(year, month, day)
        else:
            return None

    # TODO errors
    def find_date_in_monthly_statistics(self, text):
        match = next(filter(bool, (re.search(pattern, text) for pattern in self.monthly_patterns)), None)
        if match:
            groupdict = match.groupdict()
            if 'date' in groupdict or 'pl_date' in groupdict:
                if 'pl_date' in groupdict:
                    locale.setlocale(locale.LC_TIME, 'pl_PL')
                    month_year = re.sub(r'[,()]', '', match.group('pl_date').strip().replace('ń', 'ñ'))
                else:
                    month_year = re.sub(r'[,()]', '', match.group('date').strip())
                try:
                    date_time = datetime.strptime(month_year, '%B %Y')
                except ValueError:
                    raise ValueError('Invalid date(?)')
                year = date_time.year
                month = date_time.month
            elif 'month' in groupdict and 'year' in groupdict:
                month = int(match.group('month'))
                if month < 1 or month > 12:
                    raise ValueError('Invalid date(?)')
                year = int(match.group('year'))
            day = calendar.monthrange(year, month)[1]
            return date(year, month, day)
        else:
            return None

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
                return self.parse_table(tables[0])
        else:
            return None

    # TODO refactor
    def parse_table(self, table):
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
            # print(value)
            if value.any() in self.stop_parsing:
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
        for new_name in new_columns:
            column_info = [(name, index) for index, name in enumerate(columns) if new_name in name]
            if column_info:
                column_name, index = column_info[0]
                if new_name == self.capitalisation_value_column:
                    multiplier = 1
                    if 'mln' or 'mil' in column_name:
                        multiplier = 1000000
                    elif 'tys' in column_name:
                        multiplier = 1000
                columns[index] = new_name

        if not all(name in columns for name in new_columns) and \
                (self.company_column not in columns or self.capitalisation_value_column not in columns):
            raise ValueError('Invalid column names')

        columns = columns + ['', '']
        df = df.rename(columns=lambda s: columns[s])

        new_columns = [name for name in new_columns if name in df.columns]

        new_df = df[new_columns].replace(regex=r'\*', value='')
        new_df[self.capitalisation_value_column] = new_df[self.capitalisation_value_column] \
            .replace(regex=' ', value='') \
            .replace(regex=',', value='.') \
            .astype('float') \
            .mul(multiplier)

        new_df.apply(self.save_value_to_database, axis=1)
        return new_df

    def save_value_to_database(self, row):
        company_name = row[self.company_column]
        company_isin = row.get(self.isin_code_column)
        market_value = row[self.capitalisation_value_column]

        try:
            insert_market_value(market_value, self.date, company_name, company_isin)
        except CompanyNotFoundError:
            print(f'Company {company_name} not found')
            # TODO (what next?)
            # insert_company(company_name=company_name, company_isin=company_isin)
            # print(f'Company {company_name} inserted')
            # self.save_value_to_database(row)


if __name__ == '__main__':
    path = 'C:\\Users\\Dominika\\Documents\\Studia\\Inżynierka\\examples\\2019_GPW.pdf'
    doc_date = None

    parser = PdfGPWParser()
    data = parser.parse(path, doc_date)

    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.float_format', '{:.0f}'.format):
        print(data)
