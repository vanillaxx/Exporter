import copy
from sqlite3 import IntegrityError

from common.DAL.db_queries_insert import insert_market_value, insert_company, replace_values, insert_values
from common.DAL.db_queries_get import get_company, get_existing_data_for_market_values
from common.Utils.company_unification import Company
import common.Utils.unification_info


def save_value_to_database(name, isin, value, end_date, overlapping_info: {}, unification_info: [],
                           save: bool, override: bool):
    company = Company(name=name, isin=isin)
    company_id, possible_companies = get_company(company, save or override)

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

        table_name = 'MarketValues'
        columns = ['CompanyID', 'Period end', 'Market value']
        values = [company_id, str(end_date), value]

        if save:
            insert_values(table_name=table_name, columns=columns, values=values)
        elif override:
            replace_values(table_name=table_name, columns=columns, values=values)
        else:
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


def df_with_new_indexes(df):
    rows_number = len(df)
    new_indexes = range(1, rows_number + 1)
    old_indexes = df.index.values
    return df.rename(index=dict(zip(old_indexes, new_indexes)))


def check_if_data_correct(warnings: [], row_index, page_num, company_name, company_isin, market_value, multiplier):
    market_value_error = False
    try:
        market_value = float(market_value)
    except ValueError:
        market_value_error = True

    if ((not company_name or company_name.isdigit()) and not company_isin) or market_value_error:
        warnings.append(f'Row {row_index} on page {page_num}: '
                        f'read incorrect values (name:{company_name}, market value: {market_value})')
        return None
    elif not market_value_error:
        return market_value * multiplier
    else:
        return None
