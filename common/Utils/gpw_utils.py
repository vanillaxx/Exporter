import copy
from sqlite3 import IntegrityError

from common.DAL.db_queries_insert import insert_market_value, insert_company
from common.DAL.db_queries_get import get_company, get_existing_data_for_market_values
from common.Utils.company_unification import Company
import common.Utils.unification_info


def save_value_to_database(name, isin, value, end_date, overlapping_info: {}, unification_info: []):
    company = Company(name=name, isin=isin)
    company_id, possible_companies = get_company(company)

    if company_id is None and possible_companies:
        unification_info.append(
            common.Utils.unification_info.GPWUnificationInfo(company=company,
                                                             possible_matches=possible_companies,
                                                             value=value,
                                                             end_date=str(end_date))
        )
    else:
        if company_id is None and not possible_companies:
            company_id = insert_company(company)

        try:
            insert_market_value(company_id, value, end_date)
        except IntegrityError:
            add_overlapping_info(overlapping_info, company_id, name, value, end_date)


def add_overlapping_info(overlapping_info: {}, company_id, name, value, end_date):
    existing = get_existing_data_for_market_values(company_id, end_date, value)
    if existing:

        if not overlapping_info:
            overlapping_info['table_name'] = 'MarketValues'
            overlapping_info['columns'] = ['CompanyID', 'Company Name', 'Period end', 'Market value']
            overlapping_info['values'] = []
            overlapping_info['exists'] = []

        existing = list(existing)
        existing[2] = str(existing[2])
        overlapping_info['values'].append([company_id, name, str(end_date), value])
        overlapping_info['exists'].append(existing)


def copy_and_remove_name_from_overlapping_info(overlapping: {}):
    def remove_name(l):
        l.pop(1)
        return l

    overlapping_copy = copy.deepcopy(overlapping)

    overlapping_copy['columns'].pop(1)
    overlapping_copy['values'] = list(map(remove_name, overlapping_copy['values']))

    return overlapping_copy
