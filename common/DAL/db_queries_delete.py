from common.DAL.db_utils import with_connection

@with_connection
def delete_company(connection, company_id):
    values = company_id,
    command = 'DELETE FROM Company WHERE ID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def delete_from_assets(connection, company_id):
    values = company_id,
    command = 'DELETE FROM Assets WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def delete_from_assets_categories(connection, company_id):
    values = company_id,
    command = 'DELETE FROM AssetsCategories WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def delete_from_equity_liabilities(connection, company_id):
    values = company_id,
    command = 'DELETE FROM EquityLiabilities WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def delete_from_equity_liabilities_categories(connection, company_id):
    values = company_id,
    command = 'DELETE FROM EquityLiabilitiesCategories WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def delete_from_financial_ratios(connection, company_id):
    values = company_id,
    command = 'DELETE FROM FinancialRatios WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def delete_from_dupont_indicators(connection, company_id):
    values = company_id,
    command = 'DELETE FROM DuPontIndicators WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def delete_from_stock_quotes(connection, company_id):
    values = company_id,
    command = 'DELETE FROM StockQuotes WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)
