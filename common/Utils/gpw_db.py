from common.DAL.db_queries import insert_market_value, insert_company, get_company
from common.Utils.company_unification import Company
from common.Utils.unification_info import GPWUnificationInfo


def save_value_to_database(name, isin, value, end_date, unification_info):
    company = Company(name=name, isin=isin)
    company_id, possible_companies = get_company(company)

    if company_id is None and not possible_companies:
        company_id = insert_company(company)
        insert_market_value(company_id, value, end_date)

    elif possible_companies:
        unification_info.append(
            GPWUnificationInfo(company=company,
                               possible_matches=possible_companies,
                               value=value,
                               end_date=str(end_date))
        )
    else:
        insert_market_value(company_id, value, end_date)
