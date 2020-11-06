from abc import ABC, abstractmethod

from common.DAL.db_queries import insert_market_value, insert_stock_quotes, insert_values
from common.Utils.company_unification import Company
import json


class UnificationInfo(ABC):
    def __init__(self, company: Company, possible_matches: [], *args, **kwargs):
        self.company = company
        self.possible_matches = possible_matches

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
    def insert_data_to_db(self, company_id):
        pass

    @abstractmethod
    def get_data_type(self):
        pass


class GPWUnificationInfo(UnificationInfo):
    def __init__(self, company: Company, possible_matches: [], value=None, end_date=None, data=None, *args, **kwargs):
        super().__init__(company, possible_matches, *args, **kwargs)
        self.data_type = 'gpw'
        if value is not None and end_date is not None:
            self.data = {
                'value': value,
                'end_date': str(end_date)
            }
        elif data is not None:
            self.data = data

    def insert_data_to_db(self, company_id):
        insert_market_value(company_id, self.data['value'], self.data['end_date'])

    def get_data_type(self):
        return 'GPW file'


class StooqUnificationInfo(UnificationInfo):
    def __init__(self, company: Company, possible_matches: [], data: [], *args, **kwargs):
        super().__init__(company, possible_matches, *args, **kwargs)
        self.data_type = 'stooq'
        self.data = data

    def insert_data_to_db(self, company_id):
        for data in self.data:
            data[0] = company_id
            insert_stock_quotes(tuple(data))

    def get_data_type(self):
        return 'stooq.com data'

    def add_data(self, data):
        self.data.append(data)


class NotoriaUnificationInfo(UnificationInfo):
    def __init__(self, company: Company, possible_matches: [], data: [], *args, **kwargs):
        super().__init__(company, possible_matches, *args, **kwargs)
        self.data_type = 'notoria'
        self.data = data

    def insert_data_to_db(self, company_id):
        for data in self.data:
            data['data'][0] = company_id
            print('db', data)
            insert_values(table_name=data['table_name'], columns=data['columns'], values=data['data'])

    def get_data_type(self):
        return 'Notoria file'

    def add_data(self, table_name: str, columns: [], data: []):
        self.data.append({
            'table_name': table_name,
            'columns': columns,
            'data': data
        })
