from abc import ABC, abstractmethod
from sqlite3 import IntegrityError

from common.DAL.db_queries_get import exactly_same_stock_quote, exactly_same_assets, exactly_same_equity_liabilities, \
    exactly_same_assets_categories, exactly_same_equity_liabilities_categories, exactly_same_financial_ratios, \
    exactly_same_dupont_indicators
from common.DAL.db_queries_insert import insert_market_value, insert_stock_quotes, insert_values_without_ignore
from common.Utils.company_unification import Company
import json
import common.Utils.gpw_utils


class UnificationInfo(ABC):
    def __init__(self, company: Company, possible_matches: [], data_type: str, *args, **kwargs):
        self.company = company
        self.possible_matches = possible_matches
        self.data_type = data_type

    @staticmethod
    def list_to_json(data):
        return json.dumps(list(map(lambda x: x.to_json(), data)))

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @staticmethod
    def from_json(ui_json):
        class_from_data_type = {
            'gpw': GPWUnificationInfo,
            'stooq': StooqUnificationInfo,
            'notoria': NotoriaUnificationInfo
        }
        ui_dict = json.loads(ui_json)
        ui_dict['company'] = Company(**ui_dict['company'])
        return class_from_data_type[ui_dict['data_type']](**ui_dict)

    @abstractmethod
    def insert_data_to_db(self, overlapping_data: [], company_id, company_name=None):
        pass

    @abstractmethod
    def get_data_type(self):
        pass


class GPWUnificationInfo(UnificationInfo):
    def __init__(self, company: Company, possible_matches: [], value=None, end_date=None, data=None,  data_type='gpw', *args, **kwargs):
        super().__init__(company, possible_matches, data_type, *args, **kwargs)
        if value is not None and end_date is not None:
            self.data = {
                'value': value,
                'end_date': str(end_date)
            }
        elif data is not None:
            self.data = data

    def insert_data_to_db(self, overlapping_data: [], company_id, company_name=None):
        try:
            insert_market_value(company_id, self.data['value'], self.data['end_date'])
        except IntegrityError:
            common.Utils.gpw_utils.add_overlapping_info(overlapping_data[0], company_id, company_name,
                                                        self.data['value'], self.data['end_date'])

    def get_data_type(self):
        return 'GPW file'


class StooqUnificationInfo(UnificationInfo):
    def __init__(self, company: Company, possible_matches: [], data: [],  data_type='stooq', *args, **kwargs):
        super().__init__(company, possible_matches, data_type, *args, **kwargs)
        self.data = data

    def insert_data_to_db(self, overlapping_data: [], company_id, company_name=None):
        for data in self.data:
            data[0] = company_id
            data = tuple(data)
            try:
                insert_stock_quotes(data)
            except IntegrityError:
                if not exactly_same_stock_quote(data):
                    overlapping_info = overlapping_data[0]
                    if not overlapping_info:
                        overlapping_info['table_name'] = 'StockQuotes'
                        overlapping_info['columns'] = ['CompanyID', 'Date', 'Stock', 'Change', 'Open', 'High', 'Low',
                                                       'Volume', 'Turnover', 'Interval']
                        overlapping_info['values'] = []

                    overlapping_info['values'].append(data)

    def get_data_type(self):
        return 'stooq.com data'

    def add_data(self, data):
        self.data.append(data)


class NotoriaUnificationInfo(UnificationInfo):
    def __init__(self, company: Company, possible_matches: [], data: [], data_type='notoria', *args, **kwargs):
        super().__init__(company, possible_matches, data_type, *args, **kwargs)
        self.data = data
        self.exactly_same_fun = {
            'Assets': exactly_same_assets,
            'EquityLiabilities': exactly_same_equity_liabilities,
            'AssetsCategories': exactly_same_assets_categories,
            'EquityLiabilitiesCategories': exactly_same_equity_liabilities_categories,
            'FinancialRatios': exactly_same_financial_ratios,
            'DuPontIndicators': exactly_same_dupont_indicators
        }

    def insert_data_to_db(self, overlapping_data: [], company_id, company_name=None):
        for data in self.data:
            data['data'][0] = company_id
            table_name = data['table_name']
            columns = data['columns']
            values = data['data']
            try:
                insert_values_without_ignore(table_name=table_name, columns=columns, values=values)
            except IntegrityError:
                if not self.exactly_same_fun[table_name](columns, values):
                    overlapping_info = self.__get_overlapping_for_table(overlapping_data, table_name)
                    if not overlapping_info:
                        overlapping_info['table_name'] = table_name
                        overlapping_info['columns'] = columns
                        overlapping_info['values'] = []
                    overlapping_info['values'].append(values)

    @staticmethod
    def __get_overlapping_for_table(overlapping_data, table):
        if not overlapping_data[0]:
            return overlapping_data[0]

        overlapping = list(filter(lambda d: d['table_name'] == table, overlapping_data))
        if overlapping:
            return overlapping[0]
        else:
            overlapping_info = {}
            overlapping_data.append(overlapping_info)
            return overlapping_info

    def get_data_type(self):
        return 'Notoria file'

    def add_data(self, table_name: str, columns: [], data: []):
        self.data.append({
            'table_name': table_name,
            'columns': columns,
            'data': data
        })
