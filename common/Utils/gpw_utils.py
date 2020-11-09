from sqlite3 import IntegrityError

from common.DAL.db_queries_insert import insert_market_value, insert_company
from common.DAL.db_queries_get import get_company, get_existing_data_for_market_values
from common.Utils.company_unification import Company
from common.Utils.unification_info import GPWUnificationInfo


def save_value_to_database(name, isin, value, end_date, overlapping_info: {}, unification_info: []):
    company = Company(name=name, isin=isin)
    company_id, possible_companies = get_company(company)

    if company_id is None and possible_companies:
        unification_info.append(
            GPWUnificationInfo(company=company,
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
    if not overlapping_info:
        overlapping_info['table_name'] = 'MarketValues'
        overlapping_info['columns'] = ['CompanyID', 'Company Name', 'Period end', 'Market value']
        overlapping_info['values'] = []
        overlapping_info['exists'] = []

    existing = get_existing_data_for_market_values(company_id, end_date, value)
    if existing:
        existing = list(existing)
        existing[2] = str(existing[2])
        overlapping_info['values'].append([company_id, name, str(end_date), value])
        overlapping_info['exists'].append(existing)
