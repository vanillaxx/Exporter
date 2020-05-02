import requests
import pandas as pd


class StooqParser:
    def __init__(self):
        self._all_companies_current_ulr_base = 'https://stooq.com/t/?i=513&v=1&l={number}'
        self._all_companies_date_ulr_base = 'https://stooq.com/t/?i=513&v=1&d={year:04d}{month:02d}{day:02d}&l={number}'
        self._company_current_url_base = 'https://stooq.com/q/d/?s={company}'
        self._company_period_url_base = 'https://stooq.com/q/d/?s={company}&i=d&d1={year1:04d}{month1:02d}{day1:02d}&d2={year2:04d}{month2:02d}{day2:02d}&l={number}'

    def download_company_current(self, company):
        url = self._company_current_url_base.format(company=company)
        site_html = requests.get(url).content

        try:
            df_list = pd.read_html(site_html, attrs={'id': 'fth1'})
        except ValueError:
            return False

        result = df_list[0].loc[0]
        print(result)
        return True

    def download_company_period(self, company, start_date, end_date):
        start_day, start_month, start_year = start_date
        end_day, end_month, end_year = end_date
        i = 1
        frames = []
        while True:
            url = self._company_period_url_base.format(number=i, company=company,
                                                       day1=start_day, month1=start_month, year1=start_year,
                                                       day2=end_day, month2=end_month, year2=end_year)
            site_html = requests.get(url).content

            try:
                df_list = pd.read_html(site_html, attrs={'id': 'fth1'})
            except ValueError:
                break

            if len(df_list) == 0 or df_list[0].empty:
                break

            frames.append(df_list[0])
            i += 1

        result = pd.concat(frames)
        print(result)
        return True

    def download_all_companies_date(self, date):
        day, month, year = date
        i = 1
        frames = []
        while True:
            url = self._all_companies_date_ulr_base.format(number=i, day=day, month=month, year=year)
            site_html = requests.get(url).content

            try:
                df_list = pd.read_html(site_html, attrs={'id': 'fth1'})
            except ValueError:
                break

            if len(df_list) == 0 or df_list[0].empty:
                break

            frames.append(df_list[0])
            i += 1

        result = pd.concat(frames)
        print(result)
        return True

    def download_all_companies_current(self):
        i = 1
        frames = []
        while True:
            url = self._all_companies_current_ulr_base.format(number=i)
            site_html = requests.get(url).content

            try:
                df_list = pd.read_html(site_html, attrs={'id': 'fth1'})
            except ValueError:
                break

            if len(df_list) == 0 or df_list[0].empty:
                break

            frames.append(df_list[0])
            i += 1

        result = pd.concat(frames)
        print(result)
        return True


sp = StooqParser()
sp.download_all_companies_current()
sp.download_all_companies_date((30, 4, 2020))
sp.download_company_current("wig20")
sp.download_company_period("bnp", (23, 4, 2020), (28, 4, 2020))
