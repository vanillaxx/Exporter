import lxml
import numbers
import requests
import pandas as pd
from common.DAL.db_queries import insert_company, insert_stock_quotes, get_company_id_from_ticker
from common.Utils.Errors import CompanyNotFoundError
import re
from datetime import date, timedelta


class StooqParser:
    def __init__(self):
        self._all_companies_date_ulr_base = 'https://stooq.com/t/?i=513&n=0&v=1&d={year:04d}{month:02d}{day:02d}&l={number}'
        self._all_companies_date_ulr_change = 'https://stooq.com/t/?i=513&n=0&v=0&d={year:04d}{month:02d}{day:02d}&l={number}'
        self._company_url_base = 'https://stooq.com/q/d/?s={company}&c=0&i={interval}&d1={year1:04d}{month1:02d}{day1:02d}&d2={year2:04d}{month2:02d}{day2:02d}&l={number}'
        self._tables_filter = re.compile(r'.*:.*')

    # daily StockQuotes for given date for all available companies (contains turnover)
    def download_all_companies(self, user_date):
        day, month, year = user_date.day, user_date.month, user_date.year
        new_companies = []

        i = 1
        frames = []
        frames_change = []
        found = False
        while True:
            url = self._all_companies_date_ulr_base.format(number=i, day=day, month=month, year=year)
            site_html = requests.get(url).content.decode("utf-8")

            try:
                df_list = pd.read_html(site_html)
            except ValueError:
                break
            except lxml.etree.ParserError:
                break

            if len(df_list) == 0:
                break

            for df in df_list:
                if 'Symbol' in df.columns and 'Name' in df.columns and 'Last' in df.columns:
                    if not df.empty and not df.Symbol.apply(lambda x: bool(self._tables_filter.match(str(x)))).any():
                        frames.append(df)
                        found = True

            if not found:
                break

            i += 1
            found = False

        i = 1
        found = False
        while True:
            url_change = self._all_companies_date_ulr_change.format(number=i, day=day, month=month, year=year)
            site_html_change = requests.get(url_change).content

            try:
                df_list_change = pd.read_html(site_html_change)
            except ValueError:
                break
            except lxml.etree.ParserError:
                break

            if len(df_list_change) == 0:
                break

            for df in df_list_change:
                if 'Symbol' in df.columns and 'Name' in df.columns and 'Change' in df.columns:
                    if not df.empty and not df.Symbol.apply(lambda x: bool(self._tables_filter.match(str(x)))).any():
                        frames_change.append(df)
                        found = True

            if not found:
                break

            i += 1
            found = False

        if len(frames) == 0:
            raise ValueError("No stock quotes for companies")
        if len(frames_change) == 0:
            raise ValueError("No stock quotes for companies")

        result = pd.concat(frames)
        result_change = pd.concat(frames_change)
        result_change = result_change[['Symbol', 'Change.1']]
        result = result.join(result_change.set_index('Symbol'), on='Symbol')
        try:
            result['Volume'] = result['Volume'].apply(lambda x: _convert_kmb(x))
            result['Turnover'] = result['Turnover'].apply(lambda x: _convert_kmb(x))
        except ValueError:
            raise ValueError('Wrong data in Volume/Turnover column')

        for index, row in result.iterrows():
            company_id = get_company_id_from_ticker(row['Symbol'])
            if company_id is None:
                insert_company(company_name=row['Symbol'], company_ticker=row['Symbol'], company_isin=None)
                new_companies.append(row['Symbol'])

            insert_stock_quotes((company_id, date(year, month, day), date(year, month, day), row['Last'],
                                 row['Change.1'], row['Open'], row['High'], row['Low'], row['Volume'], row['Turnover']))

        return new_companies

    def download_company(self, company, start_date, end_date,
                         interval='d'):  # interval StockQuotes for given dates for company (no turnover)
        # interval: 'd' - day, 'w' - week, 'm' - month, 'q' - quoter, 'y' - year
        start_day, start_month, start_year = start_date.day, start_date.month, start_date.year
        end_day, end_month, end_year = end_date.day, end_date.month, end_date.year
        i = 1
        frames = []
        found = False
        new_companies = []

        company_id = get_company_id_from_ticker(company)
        if company_id is None:
            insert_company(company_name=company, company_ticker=company, company_isin=None)
            new_companies.append(company)

        while True:
            url = self._company_url_base.format(number=i, company=company,
                                                day1=start_day, month1=start_month, year1=start_year,
                                                day2=end_day, month2=end_month, year2=end_year,
                                                interval=interval)
            site_html = requests.get(url).content.decode("utf-8")

            try:
                df_list = pd.read_html(site_html)
            except ValueError:
                break
            except lxml.etree.ParserError:
                break

            if len(df_list) == 0:
                break
            for df in df_list:
                if 'Date' in df.columns and 'Close' in df.columns:
                    if not df.empty and not df.Date.isnull().any():
                        frames.append(df)
                        found = True

            if not found:
                break

            i += 1
            found = False

        result = pd.concat(frames)
        result = result[::-1]

        try:
            result['Volume'] = result['Volume'].apply(lambda x: _convert_kmb(x))
        except ValueError:
            raise ValueError('Wrong data in Volume column')

        previous_date = date(start_year, start_month, start_day)
        if interval == 'y':
            previous_date = previous_date.replace(day=1, month=1)
        elif interval == 'q':
            previous_date = _get_first_day_of_the_quarter(previous_date)
        elif interval == 'm':
            previous_date = previous_date.replace(day=1)
        elif interval == 'w':
            previous_date = previous_date - timedelta(days=previous_date.weekday())

        for index, row in result.iterrows():
            if pd.isnull(row['No.']):
                continue

            try:
                parsed_date = _parse_date(row['Date'])
            except (ValueError, TypeError):
                raise ValueError('Wrong date')

            insert_stock_quotes((company_id, previous_date, parsed_date, row['Close'],
                                row['Change.1'], row['Open'], row['High'], row['Low'], row['Volume'], None))

            previous_date = parsed_date + timedelta(days=1)

        return new_companies


def _parse_date(date_str):
    months = {'Jan': 1,
              'Feb': 2,
              'Mar': 3,
              'Apr': 4,
              'May': 5,
              'Jun': 6,
              'Jul': 7,
              'Aug': 8,
              'Sep': 9,
              'Oct': 10,
              'Nov': 11,
              'Dec': 12}

    parts = date_str.split(' ')

    year = int(parts[2])
    month = months[parts[1]]
    day = int(parts[0])

    return date(year, month, day)


def _convert_comas_digit(val):
    if pd.isnull(val) or val is None:
        return None

    if isinstance(val, numbers.Number):
        return val
    val = val.replace(',', '')

    return int(val)


def _convert_kmb(val):
    if pd.isnull(val) or val is None:
        return None

    if isinstance(val, numbers.Number):
        return val

    if not val.endswith('k') and not val.endswith('m') and not val.endswith('b'):
        return int(val)

    lookup = {'k': 1000, 'm': 1000000, 'b': 1000000000}
    unit = val[-1]
    number = float(val[:-1])

    if unit in lookup:
        return int(lookup[unit] * number)

    return int(val)


def _get_quarter(input_date):
    return (input_date.month - 1) / 3 + 1


def _get_first_day_of_the_quarter(input_date):
    quarter = _get_quarter(input_date)
    return date(input_date.year, 3 * quarter - 2, 1)
