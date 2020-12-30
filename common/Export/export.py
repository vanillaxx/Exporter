import sys
import common.DAL.db_queries_get as db_queries
from common.Export.save import save_to_csv
from common.Utils.export_status import ExportStatus


def get_data_with_percentage_values(data, description, add_description=True):
    if add_description:
        csv_list = [description]
    else:
        csv_list = []
    for row in data:
        skip = 3
        fresh_row = []
        sum = row[2]
        for value in row:
            if skip > 0:
                skip = skip - 1
                fresh_row.append(value)
            else:
                if sum != 0 and sum is not None:
                    fresh_row.append(value / sum)
                else:
                    fresh_row.append(0.0)
        csv_list.append(fresh_row)
    return csv_list


def put_percentage_data_to_csv(data, description, file_name, add_description=True):
    if data:
        csv_list = get_data_with_percentage_values(data, description, add_description)
        save_to_csv(csv_list, file_name)
    status = get_status(data)
    return status


def put_data_to_csv(data, description, file_name, add_description=True):
    if data:
        if add_description:
            csv_list = [description]
        else:
            csv_list = []
        for row in data:
            csv_list.append(row)
        save_to_csv(csv_list, file_name)
    status = get_status(data)
    return status


def get_status(data):
    if data:
        return ExportStatus.SUCCESS
    else:
        return ExportStatus.FAILURE


def export_detailed_assets(company_ids, start_date, end_date, file_name, interval, add_description=True):
    months = {
        'q': ['03', '06', '09', '12'],
        'hy': ['06', '12'],
        'y': ['12']
    }
    data, description = db_queries.get_assets_for_companies(company_ids, start_date, end_date, months[interval])
    return put_percentage_data_to_csv(data, description, file_name, add_description)


def export_detailed_equities(company_ids, start_date, end_date, file_name, interval, add_description=True):
    months = {
        'q': ['03', '06', '09', '12'],
        'hy': ['06', '12'],
        'y': ['12']
    }
    data, description = db_queries.get_equity_liabilities_for_companies(company_ids, start_date, end_date,
                                                                        months[interval])
    return put_percentage_data_to_csv(data, description, file_name, add_description)


def export_assets_categories(company_ids, start_date, end_date, file_name, interval, add_description=True):
    months = {
        'q': ['03', '06', '09', '12'],
        'hy': ['06', '12'],
        'y': ['12']
    }
    data, description = db_queries.get_assets_categories_for_companies(company_ids, start_date, end_date,
                                                                       months[interval])
    return put_percentage_data_to_csv(data, description, file_name, add_description)


def export_equities_categories(company_ids, start_date, end_date, file_name, interval, add_description=True):
    months = {
        'q': ['03', '06', '09', '12'],
        'hy': ['06', '12'],
        'y': ['12']
    }
    data, description = db_queries.get_equity_liabilities_categories_for_companies(company_ids, start_date, end_date
                                                                                   , months[interval])
    return put_percentage_data_to_csv(data, description, file_name, add_description)


def export_full_assets(company_ids, start_date, end_date, file_name, interval, add_description=True):
    months = {
        'q': ['03', '06', '09', '12'],
        'hy': ['06', '12'],
        'y': ['12']
    }
    data, description = db_queries.get_full_assets_for_companies(company_ids, start_date, end_date, months[interval])
    return put_percentage_data_to_csv(data, description, file_name, add_description)


def export_full_equities(company_ids, start_date, end_date, file_name, interval, add_description=True):
    months = {
        'q': ['03', '06', '09', '12'],
        'hy': ['06', '12'],
        'y': ['12']
    }
    data, description = db_queries.get_full_equities_for_companies(company_ids, start_date, end_date, months[interval])
    return put_percentage_data_to_csv(data, description, file_name, add_description)


def export_financial_ratios(company_ids, start_date, end_date, file_name, interval, add_description=True):
    months = {
        'q': [('01', '03'), ('04', '06'), ('07', '09'), ('10', '12')],
        'y': [('01', '12')]
    }
    data, description = db_queries.get_financial_ratios_for_companies(company_ids, start_date, end_date,
                                                                      months[interval])
    return put_data_to_csv(data, description, file_name, add_description)


def export_du_pont_indicators(company_ids, start_date, end_date, file_name, interval, add_description=True):
    months = {
        'q': [('01', '03'), ('04', '06'), ('07', '09'), ('10', '12')],
        'y': [('01', '12')]
    }

    data, description = db_queries.get_du_pont_indicators_for_companies(company_ids, start_date, end_date,
                                                                        months[interval])
    return put_data_to_csv(data, description, file_name, add_description)


def export_stock_quotes(company_ids, start_date, end_date, file_name, interval, add_description=True):
    data, description = db_queries.export_stock_quotes(company_ids, start_date, end_date, interval)
    return put_data_to_csv(data, description, file_name, add_description)


def export_market_values(company_ids, start_date, end_date, file_name, interval, add_description=True):
    intervals = {
        'm': None,
        'q': ['03', '06', '09', '12'],
        'hy': ['06', '12'],
        'y': ['12']
    }
    data, description = db_queries.get_market_values_for_companies(company_ids, start_date, end_date,
                                                                   intervals[interval])
    return put_data_to_csv(data, description, file_name, add_description)


functions = {'-da': export_detailed_assets,
             '-de': export_detailed_equities,
             '-ca': export_assets_categories,
             '-ce': export_equities_categories,
             '-fa': export_full_assets,
             '-fe': export_full_equities,
             '-f': export_financial_ratios,
             '-d': export_du_pont_indicators,
             '-s': export_stock_quotes,
             '-mv': export_market_values
             }