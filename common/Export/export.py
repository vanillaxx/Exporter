import sys
import common.DAL.db_queries as db_queries
from Export.save import save_to_csv


def get_data_with_percentage_values(data, description):
    csv_list = [description]
    for row in data:
        skip = 3
        fresh_row = []
        sum = row[2]
        for value in row:
            if skip > 0:
                skip = skip - 1
                fresh_row.append(value)
            else:
                fresh_row.append(value / sum)
        csv_list.append(fresh_row)
    return csv_list


def put_percentage_data_to_csv(data, description, file_name):
    if data:
        csv_list = get_data_with_percentage_values(data, description)
        save_to_csv(csv_list, file_name)
        print("Data saved to %s" % file_name)
    else:
        print("There is no data for such a company")


def put_data_to_csv(data, description, file_name):
    if data:
        csv_list = [description]
        for row in data:
            csv_list.append(row)
        save_to_csv(csv_list, file_name)
        print("Data saved to %s" % file_name)
    else:
        print("There is no data for such a company")


def export_detailed_assets(company_name, file_name):
    data, description = db_queries.get_assets_for_company(company_name)
    put_percentage_data_to_csv(data, description, file_name)


def export_detailed_equities(company_name, file_name):
    data, description = db_queries.get_equity_liabilities_for_company(company_name)
    put_percentage_data_to_csv(data, description, file_name)


def export_assets_categories(company_name, file_name):
    data, description = db_queries.get_assets_categories_for_company(company_name)
    put_percentage_data_to_csv(data, description, file_name)


def export_equities_categories(company_name, file_name):
    data, description = db_queries.get_equity_liabilities_categories_for_company(company_name)
    put_percentage_data_to_csv(data, description, file_name)


def export_full_assets(company_name, file_name):
    data, description = db_queries.get_full_assets_for_company(company_name)
    put_percentage_data_to_csv(data, description, file_name)


def export_full_equities(company_name, file_name):
    data, description = db_queries.get_full_equities_for_company(company_name)
    put_percentage_data_to_csv(data, description, file_name)


def export_financial_ratios(company_name, file_name):
    data, description = db_queries.get_financial_ratios_for_company(company_name)
    put_data_to_csv(data, description, file_name)


def export_du_pont_indicators(company_name, file_name):
    data, description = db_queries.get_du_pont_indicators_for_company(company_name)
    put_data_to_csv(data, description, file_name)


def export_stock_quotes(company_name, file_name):
    data, description = db_queries.export_stock_quotes(company_name)
    put_data_to_csv(data, description, file_name)


def export_market_values(company_id, file_name):
    data, description = db_queries.get_market_values_for_company(company_id)
    put_data_to_csv(data, description, file_name)


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

    functions = {'-da': export_detailed_assets,
                 '-de': export_detailed_equities,
                 '-ca': export_assets_categories,
                 '-ce': export_equities_categories,
                 '-fa': export_full_assets,
                 '-fe': export_full_equities,
                 '-f': export_financial_ratios,
                 '-d': export_du_pont_indicators,
                 '-v': export_market_values,
                 '-s': export_stock_quotes
                 }

    if len(sys.argv) == 3 and sys.argv[1] in functions:
        functions[sys.argv[1]](sys.argv[2], 'default.csv')
    else:
        print(help)
