import lxml
import numbers
import requests
import pandas as pd
from exporter.DAL.utils import set_up_database_tables, insert_stock_quotes, get_company_id_from_ticker
from exporter.Utils.Errors import CompanyNotFoundError
import re
from datetime import date
import bs4 as bs


class StooqParser:
    def __init__(self):
        self._all_companies_current_ulr_base = 'https://stooq.com/t/?i=513&n=0&v=1&l={number}'
        self._all_companies_current_ulr_base_change = 'https://stooq.com/t/?i=513&n=0&v=0&l={number}'
        self._all_companies_date_ulr_base = 'https://stooq.com/t/?i=513&n=0&v=1&d={year:04d}{month:02d}{day:02d}&l={number}'
        self._all_companies_date_ulr_change = 'https://stooq.com/t/?i=513&n=0&v=0&d={year:04d}{month:02d}{day:02d}&l={number}'
        self._company_url_base = 'https://stooq.com/q/d/?s={company}&i={interval}&d1={year1:04d}{month1:02d}{day1:02d}&d2={year2:04d}{month2:02d}{day2:02d}&l={number}'
        self._tables_filter = re.compile(r'.*:.*')

    def download_all_companies_current(self): # daily StockQuotes for all available companies (contains turnover)
        i = 1
        frames = []
        frames_change = []
        found = False
        while True:
            url = self._all_companies_current_ulr_base.format(number=i)
            site_html = requests.get(url).content

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
            url_change = self._all_companies_current_ulr_base_change.format(number=i)
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
            print(row['Symbol'])
            company_id = get_company_id_from_ticker(row['Symbol'])
            if company_id is None:
                raise CompanyNotFoundError

            insert_stock_quotes((company_id, date.today(), row['Last'],
                                row['Change.1'], row['Open'], row['High'], row['Low'], row['Volume'], row['Turnover']))

    def download_all_companies_date(self, date_tuple): # daily StockQuotes for given date for all available companies (contains turnover)
        day, month, year = date_tuple

        i = 1
        frames = []
        frames_change = []
        found = False
        while True:
            url = self._all_companies_date_ulr_base.format(number=i, day=day, month=month, year=year)
            site_html = requests.get(url).content

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
            print(row['Symbol'])
            company_id = get_company_id_from_ticker(row['Symbol'])
            if company_id is None:
                raise CompanyNotFoundError

            insert_stock_quotes((company_id, date(year, month, day), row['Last'],
                                row['Change.1'], row['Open'], row['High'], row['Low'], row['Volume'], row['Turnover']))

    # TODO: fix and finish
    def download_company(self, company, start_date, end_date, interval='d'):  # interval StockQuotes for given dates for company (no turnover)
        # interval: 'd' - day, 'w' - week, 'm' - month, 'q' - quoter, 'y' - year
        start_day, start_month, start_year = start_date
        end_day, end_month, end_year = end_date
        i = 1
        frames = []
        found = False
        while i<2:
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

            print(df_list)
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
        print(result)


def _convert_comas_digit(val):
    if isinstance(val, numbers.Number):
        return val
    val = val.replace(',', '')
    return int(val)


def _convert_kmb(val):
    if isinstance(val, numbers.Number):
        return val
    if not val.endswith('k') and not val.endswith('m') and not val.endswith('b'):
        return int(val)
    lookup = {'k': 1000, 'm': 1000000, 'b': 1000000000}
    unit = val[-1]
    number = int(val[:-1])
    if unit in lookup:
        return lookup[unit] * number
    return int(val)

# test
# set_up_database_tables()
# insert_company("06n", "06N")
# insert_company("08n", "08N")
sp = StooqParser()
sp.download_all_companies_current()
sp.download_all_companies_date((1, 6, 2020))
# sp.download_company("06n", (30, 2, 2019), (30, 12, 2020), 'y')
