import sys
import common.DAL.db_queries as db_queries
from common.Export.save import save_to_csv


def get_data_with_percentage_values(data, description, add_description=True, columns_to_add=None):
    if add_description:
        csv_list = [description]
    else:
        csv_list = []
    for index, row in enumerate(data):
        skip = 3
        fresh_row = []
        sum = row[2]
        for value in row:
            if skip > 0:
                skip = skip - 1
                fresh_row.append(value)
            else:
                fresh_row.append(value / sum)
        if columns_to_add is not None:
            for column in columns_to_add:
                fresh_row.append(column[index])
        csv_list.append(fresh_row)
    return csv_list


def put_percentage_data_to_csv(data, description, file_name, add_description=True):
    if data:
        csv_list = get_data_with_percentage_values(data, description, add_description)
        save_to_csv(csv_list, file_name)
        print("Data saved to %s" % file_name)
    else:
        print("There is no data for such a company")


def put_data_to_csv(data, description, file_name, add_description=True):
    if data:
        if add_description:
            csv_list = [description]
        else:
            csv_list = []
        for row in data:
            csv_list.append(row)
        save_to_csv(csv_list, file_name)
        print("Data saved to %s" % file_name)
    else:
        print("There is no data for such a company")


def export_detailed_assets(company_ids, start_date, end_date, file_name, add_description=True):
    data, description = db_queries.get_assets_for_companies(company_ids, start_date, end_date)
    put_percentage_data_to_csv(data, description, file_name, add_description)


def export_detailed_equities(company_ids, start_date, end_date, file_name, add_description=True):
    data, description = db_queries.get_equity_liabilities_for_companies(company_ids, start_date, end_date)
    put_percentage_data_to_csv(data, description, file_name, add_description)


def export_assets_categories(company_ids, start_date, end_date, file_name, add_description=True):
    data, description = db_queries.get_assets_categories_for_companies(company_ids, start_date, end_date)
    put_percentage_data_to_csv(data, description, file_name, add_description)


def export_equities_categories(company_ids, start_date, end_date, file_name, add_description=True):
    data, description = db_queries.get_equity_liabilities_categories_for_companies(company_ids, start_date, end_date)
    put_percentage_data_to_csv(data, description, file_name, add_description)


def export_full_assets(company_ids, start_date, end_date, file_name, add_description=True):
    data, description = db_queries.get_full_assets_for_companies(company_ids, start_date, end_date)
    put_percentage_data_to_csv(data, description, file_name, add_description)


def export_full_equities(company_ids, start_date, end_date, file_name, add_description=True):
    data, description = db_queries.get_full_equities_for_companies(company_ids, start_date, end_date)
    put_percentage_data_to_csv(data, description, file_name, add_description)


def export_financial_ratios(company_ids, start_date, end_date, file_name, add_description=True):
    data, description = db_queries.get_financial_ratios_for_companies(company_ids, start_date, end_date)
    put_data_to_csv(data, description, file_name, add_description)


def export_du_pont_indicators(company_ids, start_date, end_date, file_name, add_description=True):
    data, description = db_queries.get_du_pont_indicators_for_companies(company_ids, start_date, end_date)
    put_data_to_csv(data, description, file_name, add_description)


def export_stock_quotes(company_ids, start_date, end_date, file_name):  # TODO interval options
    data, description = db_queries.export_stock_quotes(company_ids, start_date, end_date, 'd')
    put_data_to_csv(data, description, file_name)


def export_market_values(company_ids, start_date, end_date, file_name):
    data, description = db_queries.get_market_values_for_companies(company_ids, start_date, end_date)
    put_data_to_csv(data, description, file_name)


def export_assets_and_market_values_for_companies(company_ids, start_date, end_date, file_name, add_description=True):
    data, description = db_queries.get_assets_and_market_values_for_companies(company_ids, start_date, end_date)
    if data and data[0]:
        print(len(data))
        data, removed_columns = __remove_market_value_columns(data)
        print(data)
        print(removed_columns)
        data = get_data_with_percentage_values(data, description, True, removed_columns)
        print(data)
    put_data_to_csv(data, description, file_name, False)


def __remove_market_value_columns(data):
    columns = []
    new_data = []
    [new_data.append(list(row)) for row in data]
    for index in [len(new_data[0])-2, len(new_data[0])-2]:
        print([len(row) for row in new_data])
        column = [row.pop(index) for row in new_data]
        columns.append(column)
    return new_data, columns


functions = {'-da': export_detailed_assets,
             '-de': export_detailed_equities,
             '-ca': export_assets_categories,
             '-ce': export_equities_categories,
             '-fa': export_full_assets,
             '-fe': export_full_equities,
             '-f': export_financial_ratios,
             '-d': export_du_pont_indicators,
             '-v': export_market_values,
             '-s': export_stock_quotes,
             '-mv': export_market_values,
             '-damv': export_assets_and_market_values_for_companies
             }

if __name__ == "__main__":

    help = '''[option] [company]
    options
    -da - export detailed assets
    -ca - export assets categories
    -fa - export full assets
    -de - export detailed equities
    -ce - export equities categories
    -fe - export full equities
    -f - export financial ratio
    -d - export Du Pont indicators
    -v - export company values
    -s - export stock quotes'''

    if len(sys.argv) == 3 and sys.argv[1] in functions:
        functions[sys.argv[1]](sys.argv[2], 'default.csv')
    else:
        print(help)
