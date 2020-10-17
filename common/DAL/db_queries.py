from common.DAL.db_utils import with_connection
from common.Utils.Errors import CompanyNotFoundError


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
def merge_assets(connection, merge_from, merge_to):
    values = merge_to, merge_from
    command = 'UPDATE OR IGNORE Assets SET CompanyId = (?) WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def merge_assets_categories(connection, merge_from, merge_to):
    values = merge_to, merge_from
    command = 'UPDATE OR IGNORE AssetsCategories SET CompanyId = (?) WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def merge_equity_liabilities(connection, merge_from, merge_to):
    values = merge_to, merge_from
    command = 'UPDATE OR IGNORE EquityLiabilities SET CompanyId = (?) WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def merge_equity_liabilities_categories(connection, merge_from, merge_to):
    values = merge_to, merge_from
    command = 'UPDATE OR IGNORE EquityLiabilitiesCategories SET CompanyId = (?) WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def merge_financial_ratios(connection, merge_from, merge_to):
    values = merge_to, merge_from
    command = 'UPDATE OR IGNORE FinancialRatios SET CompanyId = (?) WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def merge_dupont_indicators(connection, merge_from, merge_to):
    values = merge_to, merge_from
    command = 'UPDATE OR IGNORE DuPontIndicators SET CompanyId = (?) WHERE CompanyID = (?) '
    with connection:
        connection.execute(command, values)


@with_connection
def replace_values(connection, table_name, columns, values):
    values = tuple(values)
    columns = tuple(columns)
    command = 'REPLACE INTO {table} {columns} VALUES ({seq}) '.format(table=table_name,
                                                                      columns=tuple(columns),
                                                                      seq=','.join(['?'] * len(columns)))
    with connection:
        connection.execute(command, values)


@with_connection
def insert_values_without_ignore(connection, table_name, columns, values):
    values = tuple(values)
    columns = tuple(columns)
    command = 'INSERT INTO %s%s VALUES %s ' % (table_name, columns, values)
    with connection:
        connection.execute(command)


@with_connection
def insert_values(connection, table_name, columns, values):
    values = tuple(values)
    columns = tuple(columns)
    command = 'INSERT OR IGNORE INTO %s%s VALUES %s ' % (table_name, columns, values)
    with connection:
        connection.execute(command)


@with_connection
def insert_value(connection, table_name, column, value):
    command = 'INSERT OR IGNORE INTO %s(%s) VALUES (%s) ' % (table_name, column, value)
    with connection:
        connection.execute(command)


@with_connection
def insert_stock_quotes(connection, values):
    command = '''INSERT INTO StockQuotes
                (CompanyID, 'Period end', Stock, Change, Open, High, Low, Volume, Turnover, Interval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    with connection:
        connection.execute(command, values)


@with_connection
def insert_market_value(connection, market_value, end_date, company_name, company_isin=None):
    # TODO updating information about company
    company_id = get_company_id_from_isin(company_isin) or get_company_id_from_name(company_name)
    data = (company_id, end_date, market_value)
    if company_id:
        command = '''INSERT INTO MarketValues(CompanyID, "Period end", MarketValue) VALUES (?, ?, ?)'''
        with connection:
            connection.execute(command, data)
    else:
        raise CompanyNotFoundError(name=company_name, isin=company_isin)


def insert_ekd_section(ekd_section):
    insert_value(table_name='EKDSection', column='Value', value=ekd_section)


def insert_ekd_class(ekd_class):
    insert_value(table_name='EKDClass', column='Value', value=ekd_class)


def insert_full_company(company_name, isin, company_ticker, company_bloomberg, ekd_section, ekd_class):
    section_id = get_ekd_section_id_from_value(ekd_section=ekd_section)
    class_id = get_ekd_class_id_from_value(ekd_class=ekd_class)
    insert_values(table_name='Company',
                  columns=['Name', 'ISIN', 'Ticker', 'Bloomberg', 'EKDSectionID', 'EKDClassID'],
                  values=[company_name, isin, company_ticker, company_bloomberg, section_id, class_id])


@with_connection
def insert_company(connection, company_name=None, company_ticker=None, company_isin=None):
    values = company_name, company_ticker, company_isin
    command = '''INSERT INTO Company(Name, Ticker, ISIN) VALUES (?, ?, ?)'''
    with connection:
        connection.execute(command, values)


@with_connection
def get_company_id_from_name(connection, company_name):
    company_name = company_name.upper()
    c = connection.cursor()
    c.execute("SELECT ID FROM Company WHERE Name Like ?", (company_name,))
    company = c.fetchone()
    if not company:
        return None
    return company[0]


@with_connection
def get_company_id(connection, company_name, company_ticker, company_isin):
    company_name = company_name.upper()
    c = connection.cursor()
    query = '''SELECT ID FROM Company
              WHERE Name Like ?
              OR Ticker Like ?
              OR ISIN Like ?'''
    c.execute(query, (company_name, company_ticker, company_isin))
    company = c.fetchone()
    if not company:
        return None
    return company[0]


@with_connection
def get_company_id_from_ticker(connection, ticker):
    company_ticker = ticker.upper()
    c = connection.cursor()
    c.execute("SELECT ID FROM Company WHERE Ticker Like ?", (company_ticker,))
    company = c.fetchone()
    if not company:
        return None
    return company[0]


@with_connection
def get_company_id_from_isin(connection, company_isin):
    c = connection.cursor()
    c.execute('''SELECT C.ID
                FROM Company C
                WHERE ISIN = ? ''', (company_isin,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        return result


@with_connection
def get_ekd_section_id_from_value(connection, ekd_section):
    c = connection.cursor()
    c.execute("SELECT ID FROM EKDSection WHERE Value Like (?)", (int(ekd_section),))
    return c.fetchone()[0]


@with_connection
def get_ekd_class_id_from_value(connection, ekd_class):
    c = connection.cursor()
    c.execute("SELECT ID FROM EKDClass WHERE Value Like (?)", (int(ekd_class),))
    return c.fetchone()[0]


@with_connection
def get_interval_id_from_shortcut(connection, shortcut):
    c = connection.cursor()
    c.execute("SELECT ID FROM Interval WHERE Shortcut Like ?", (shortcut,))
    interval = c.fetchone()
    if not interval:
        return None
    return interval[0]


@with_connection
def get_assets_for_companies(connection, company_ids, start_date, end_date):
    c = connection.cursor()
    query = '''SELECT C.Name, "Date", "Property, plant and equipment" +
                "Exploration for and evaluation of mineral resources" + "Intangible assets" +
                 Goodwill + "Investment property" + "Investment in affiliates" +
                 "Non-current financial assets" + "Non-current loans and receivables" +
                 "Deferred income tax" + "Non-current deferred charges and accruals" +
                 "Non-current derivative instruments" + "Other non-current assets" +
                 Inventories + "Current intangible assets" + "Biological assets" +
                 "Trade receivables" + "Loans and other receivables" + "Financial assets" +
                "Cash and cash equivalents" + Accruals + "Assets from current tax" +
                "Derivative instruments" + "Other assets" AS Sum,
                "Property, plant and equipment", "Exploration for and evaluation of mineral resources",
                "Intangible assets", Goodwill, "Investment property", "Investment in affiliates",
                "Non-current financial assets", "Non-current loans and receivables",
                "Deferred income tax", "Non-current deferred charges and accruals",
                "Non-current derivative instruments", "Other non-current assets",
                 Inventories, "Current intangible assets", "Biological assets", "Trade receivables",
                 "Loans and other receivables", "Financial assets", "Cash and cash equivalents",
                 Accruals, "Assets from current tax", "Derivative instruments", "Other assets"
                FROM Assets A 
                JOIN Company C ON C.ID = A.CompanyID
                WHERE C.ID IN ({seq}) 
                AND A.Date BETWEEN ? AND ?
                ORDER BY C.Name, A.Date '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_equity_liabilities_for_companies(connection, company_ids, start_date, end_date):
    c = connection.cursor()
    query = '''SELECT C.Name, "Date",
    "Share capital" + "Called up share capital" +
                "Treasury shares" + "Supplementary capital" + "Valuation and exchange differences" +
                "Other capitals" + "Retained earnings / accumulated losses" +
                "Non-current liabilities from derivatives" + "Non-current loans and borrowings" +
                "Non-current liabilities from bonds" + "Non-current liabilities from finance leases" +
                "Non-current trade payables" + "Long-term provision for employee benefits" +
                "Deferred tax liabilities" + "Non-current provision" + "Other non-current liabilities" +
                "Non-current accruals (liability)" + "Liabilities from derivatives" +
                "Financial liabilities (loans and borrowings)" + "Bond liabilities" +
                "Liabilities from finance leases" + "Trade payables" + "Employee benefits" +
                "Current tax liabilities" + Provisions + "Other liabilities" + "Accruals (liability)" AS Sum,
                "Share capital", "Called up share capital",
                "Treasury shares", "Supplementary capital", "Valuation and exchange differences",
                "Other capitals", "Retained earnings / accumulated losses",
                "Non-current liabilities from derivatives", "Non-current loans and borrowings",
                "Non-current liabilities from bonds", "Non-current liabilities from finance leases",
                "Non-current trade payables", "Long-term provision for employee benefits",
                "Deferred tax liabilities", "Non-current provision", "Other non-current liabilities",
                "Non-current accruals (liability)", "Liabilities from derivatives",
                "Financial liabilities (loans and borrowings)", "Bond liabilities",
                "Liabilities from finance leases", "Trade payables", "Employee benefits",
                "Current tax liabilities", Provisions, "Other liabilities", "Accruals (liability)"
              FROM EquityLiabilities E 
              JOIN Company C ON C.ID = E.CompanyID
                WHERE C.ID IN ({seq}) 
                AND E.Date BETWEEN ? AND ?
                ORDER BY C.Name, E.Date '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_assets_equity_liabilities_for_companies(connection, company_ids, start_date, end_date):
    c = connection.cursor()
    query = '''SELECT C.Name, E."Date",
                "Property, plant and equipment" +
                "Exploration for and evaluation of mineral resources" + "Intangible assets" +
                 Goodwill + "Investment property" + "Investment in affiliates" +
                 "Non-current financial assets" + "Non-current loans and receivables" +
                 "Deferred income tax" + "Non-current deferred charges and accruals" +
                 "Non-current derivative instruments" + "Other non-current assets" +
                 Inventories + "Current intangible assets" + "Biological assets" +
                 "Trade receivables" + "Loans and other receivables" + "Financial assets" +
                "Cash and cash equivalents" + Accruals + "Assets from current tax" +
                "Derivative instruments" + "Other assets" AS Sum,
                "Share capital", "Called up share capital", "Treasury shares",
                "Supplementary capital", "Valuation and exchange differences", "Other capitals",
                "Retained earnings / accumulated losses", "Non-current liabilities from derivatives",
                "Non-current loans and borrowings", "Non-current liabilities from bonds",
                "Non-current liabilities from finance leases", "Non-current trade payables",
                "Long-term provision for employee benefits", "Deferred tax liabilities", "Non-current provision",
                "Other non-current liabilities", "Non-current accruals (liability)", "Liabilities from derivatives",
                "Financial liabilities (loans and borrowings)", "Bond liabilities", "Liabilities from finance leases",
                "Trade payables", "Employee benefits", "Current tax liabilities", Provisions, "Other liabilities",
                "Accruals (liability)", "Property, plant and equipment", "Exploration for and evaluation of mineral resources",
                "Intangible assets", Goodwill, "Investment property", "Investment in affiliates", "Non-current financial assets",
                "Non-current loans and receivables", "Deferred income tax", "Non-current deferred charges and accruals",
                "Non-current derivative instruments", "Other non-current assets", Inventories, "Current intangible assets",
                "Biological assets", "Trade receivables", "Loans and other receivables", "Financial assets",
                "Cash and cash equivalents", Accruals, "Assets from current tax", "Derivative instruments", "Other assets"
                FROM EquityLiabilities E 
                JOIN main.Assets A ON A.CompanyID = E.CompanyID AND A.Date = E.Date
                JOIN Company C ON C.ID = E.CompanyID
                WHERE C.ID IN ({seq}) 
                AND E.Date BETWEEN ? AND ?
                ORDER BY C.Name, E.Date '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_assets_categories_for_companies(connection, company_ids, start_date, end_date):
    c = connection.cursor()
    query = '''SELECT C.Name, "Date", "Non-current assets" + "Current assets" +
                "Assets held for sale and discontinuing operations" +
                "Called up capital" + "Own shares" AS Sum,
                "Non-current assets", "Current assets",
                "Assets held for sale and discontinuing operations",
                "Called up capital", "Own shares"
                FROM AssetsCategories AC 
                JOIN Company C ON C.ID = AC.CompanyID
                WHERE C.ID IN ({seq}) 
                AND AC.Date BETWEEN ? AND ?
                ORDER BY C.Name, AC.Date '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_equity_liabilities_categories_for_companies(connection, company_ids, start_date, end_date):
    c = connection.cursor()
    query = '''SELECT C.Name, "Date", 
                "Equity shareholders of the parent" + "Non-controlling interests" +
                "Non-current liabilities" + "Current liabilities" + 
                "Liabilities related to assets held for sale and discontinued operations" AS Sum,
                "Equity shareholders of the parent", "Non-controlling interests",
                "Non-current liabilities", "Current liabilities", 
                "Liabilities related to assets held for sale and discontinued operations"
                FROM EquityLiabilitiesCategories EC 
                JOIN Company C ON C.ID = EC.CompanyID
                WHERE C.ID IN ({seq}) 
                AND EC.Date BETWEEN ? AND ?
                ORDER BY C.Name, EC.Date '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_full_assets_for_companies(connection, company_ids, start_date, end_date):
    c = connection.cursor()
    query = '''SELECT C.Name, A."Date", "Property, plant and equipment" +
                "Exploration for and evaluation of mineral resources" + "Intangible assets" +
                 Goodwill + "Investment property" + "Investment in affiliates" +
                 "Non-current financial assets" + "Non-current loans and receivables" +
                 "Deferred income tax" + "Non-current deferred charges and accruals" +
                 "Non-current derivative instruments" + "Other non-current assets" +
                 Inventories + "Current intangible assets" + "Biological assets" +
                 "Trade receivables" + "Loans and other receivables" + "Financial assets" +
                "Cash and cash equivalents" + Accruals + "Assets from current tax" +
                "Derivative instruments" + "Other assets" AS Sum,
                AC."Non-current assets", "Property, plant and equipment",
                "Exploration for and evaluation of mineral resources",
                "Intangible assets", Goodwill, "Investment property", "Investment in affiliates",
                "Non-current financial assets", "Non-current loans and receivables",
                "Deferred income tax", "Non-current deferred charges and accruals",
                "Non-current derivative instruments", "Other non-current assets", AC."Current assets",
                 Inventories, "Current intangible assets",
                "Biological assets", "Trade receivables", "Loans and other receivables", "Financial assets",
                "Cash and cash equivalents", Accruals, "Assets from current tax", "Derivative instruments",
                "Other assets", AC."Assets held for sale and discontinuing operations",
                AC."Called up capital", AC."Own shares"
                FROM Assets A 
                JOIN AssetsCategories AC
                ON AC.CompanyID = A.CompanyID AND AC.Date = A.Date
                JOIN Company C ON C.ID = A.CompanyID
                WHERE C.ID IN ({seq}) 
                AND AC.Date BETWEEN ? AND ?
                ORDER BY C.Name, AC.Date '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_du_pont_indicators_for_companies(connection, company_ids, start_date, end_date):
    c = connection.cursor()
    query = '''SELECT C.Name, "Period start", "Period end", "Return on equity (ROE)",
                "Return on assets (ROA)", "Leverage (EM)", "Net profit margin",
                "Asset utilization (AU)", "Load gross profit", "Load operating profit",
                "Operating profit margin", "EBITDA margin"
              FROM DuPontIndicators D
              JOIN Company C ON C.ID = D.CompanyID
                WHERE C.ID IN ({seq}) 
                AND D."Period start" >= ?
                AND D."Period end" <= ?
                ORDER BY C.Name, D."Period start" '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_financial_ratios_for_companies(connection, company_ids, start_date, end_date):
    c = connection.cursor()
    query = '''SELECT C.Name, "Period start", "Period end",
                "Gross profit margin on sales", "Operating profit margin",
                "Gross profit margin", "Net profit margin", "Return on equity (ROE)",
                "Return on assets (ROA)", "Working capital ratio", "Current ratio",
                "Quick ratio","Cash ratio", "Receivables turnover", "Inventory turnover",
                "The operating cycle", "Rotation commitments", "Cash conversion cycle",
                "Rotation assets", "Rotation of assets", "Assets ratio", "Debt ratio",
                "Debt service ratio", "Rate debt security"
              FROM FinancialRatios F
              JOIN Company C ON C.ID = F.CompanyID
                WHERE C.ID IN ({seq}) 
                AND F."Period start" >= ?
                AND F."Period end" <= ?
                ORDER BY C.Name, F."Period start" '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_full_equities_for_companies(connection, company_ids, start_date, end_date):
    c = connection.cursor()
    query = '''SELECT C.Name, E."Date",
    "Share capital" + "Called up share capital" +
                "Treasury shares" + "Supplementary capital" + "Valuation and exchange differences" +
                "Other capitals" + "Retained earnings / accumulated losses" +
                "Non-current liabilities from derivatives" + "Non-current loans and borrowings" +
                "Non-current liabilities from bonds" + "Non-current liabilities from finance leases" +
                "Non-current trade payables" + "Long-term provision for employee benefits" +
                "Deferred tax liabilities" + "Non-current provision" + "Other non-current liabilities" +
                "Non-current accruals (liability)" + "Liabilities from derivatives" +
                "Financial liabilities (loans and borrowings)" + "Bond liabilities" +
                "Liabilities from finance leases" + "Trade payables" + "Employee benefits" +
                "Current tax liabilities" + Provisions + "Other liabilities" + "Accruals (liability)" AS Sum,
                ELC."Equity shareholders of the parent", "Share capital", "Called up share capital",
                "Treasury shares", "Supplementary capital", "Valuation and exchange differences",
                "Other capitals", "Retained earnings / accumulated losses",
                ELC."Non-controlling interests", ELC."Non-current liabilities",
                "Non-current liabilities from derivatives", "Non-current loans and borrowings",
                "Non-current liabilities from bonds", "Non-current liabilities from finance leases",
                "Non-current trade payables", "Long-term provision for employee benefits",
                "Deferred tax liabilities", "Non-current provision", "Other non-current liabilities",
                "Non-current accruals (liability)", ELC."Current liabilities", "Liabilities from derivatives",
                "Financial liabilities (loans and borrowings)", "Bond liabilities",
                "Liabilities from finance leases", "Trade payables", "Employee benefits",
                "Current tax liabilities", Provisions, "Other liabilities", "Accruals (liability)",
                ELC."Liabilities related to assets held for sale and discontinued operations"
              FROM EquityLiabilities E 
              JOIN EquityLiabilitiesCategories ELC
              ON ELC.CompanyID = E.CompanyID AND ELC.Date = E.Date
              JOIN Company C ON C.ID = E.CompanyID
                WHERE C.ID IN ({seq}) 
                AND E.Date BETWEEN ? AND ?
                ORDER BY C.Name, E.Date '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def export_stock_quotes(connection, company_ids, start_date, end_date, interval):
    interval_id = get_interval_id_from_shortcut(interval)
    c = connection.cursor()
    query = '''SELECT C.Name, "Period end", Stock, Change, "Open", High, Low, Volume, Turnover
                FROM StockQuotes SQ 
                JOIN Company C ON C.ID = SQ.CompanyID
                WHERE C.ID IN ({seq}) 
                AND SQ."Period end" BETWEEN ? AND ?
                AND Interval = ?
                ORDER BY C.Name, SQ."Period end" '''.format(seq=','.join(['?'] * len(company_ids)))
    company_ids.extend([start_date, end_date, interval_id])
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_market_values_for_companies(connection, company_ids, start_date, end_date, months=None):
    c = connection.cursor()
    if months is not None:
        query = '''SELECT C.Name, MarketValue, "Period end"
                     FROM MarketValues MV
                     JOIN Company C ON C.ID = MV.CompanyID
                     WHERE C.ID IN ({seq}) 
                     AND MV."Period end" BETWEEN ? AND ?
                     AND strftime('%m',  MV."Period end") IN ({months_seq})
                     ORDER BY C.Name, MV."Period end" '''.format(seq=','.join(['?'] * len(company_ids)),
                                                                 months_seq=','.join(['?'] * len(months)))
        company_ids.extend([start_date, end_date])
        company_ids.extend(months)
    else:
        query = '''SELECT C.Name, MarketValue, "Period end"
                             FROM MarketValues MV
                             JOIN Company C ON C.ID = MV.CompanyID
                             WHERE C.ID IN ({seq}) 
                             AND MV."Period end" BETWEEN ? AND ?
                             ORDER BY C.Name, MV."Period end" '''.format(seq=','.join(['?'] * len(company_ids)))
        company_ids.extend([start_date, end_date])

    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_all_companies(connection):
    c = connection.cursor()
    c.execute("SELECT Name, Name FROM Company ")
    return c.fetchall()


@with_connection
def get_existing_data_balance_sheet(connection, overlapping_data):
    c = connection.cursor()
    table_name = overlapping_data["table_name"]
    query = ''''''
    values = overlapping_data["values"]
    dates = tuple(map(lambda x: x[1], values))
    company_id = values[0][0]
    if table_name == "Assets":
        query = '''SELECT CompanyID, "Date",
                "Property, plant and equipment", "Exploration for and evaluation of mineral resources",
                "Intangible assets", Goodwill, "Investment property", "Investment in affiliates",
                "Non-current financial assets", "Non-current loans and receivables",
                "Deferred income tax", "Non-current deferred charges and accruals",
                "Non-current derivative instruments", "Other non-current assets",
                 Inventories, "Current intangible assets", "Biological assets", "Trade receivables",
                 "Loans and other receivables", "Financial assets", "Cash and cash equivalents",
                 Accruals, "Assets from current tax", "Derivative instruments", "Other assets"
                FROM Assets 
                WHERE CompanyID = {company_id} AND Date IN {dates} '''.format(company_id=company_id, dates=dates)
    elif table_name == "AssetsCategories":
        query = '''SELECT CompanyID, "Date", "Non-current assets" + "Current assets" +
                "Assets held for sale and discontinuing operations" +
                "Called up capital" + "Own shares" AS Sum,
                "Non-current assets", "Current assets",
                "Assets held for sale and discontinuing operations",
                "Called up capital", "Own shares"
                 FROM AssetsCategories
                WHERE CompanyID = {company_id} AND Date IN {dates} '''.format(company_id=company_id, dates=dates)
    elif table_name == "EquityLiabilitiesCategories":
        query = '''SELECT CompanyID, "Date", 
                "Equity shareholders of the parent" + "Non-controlling interests" +
                "Non-current liabilities" + "Current liabilities" + 
                "Liabilities related to assets held for sale and discontinued operations" AS Sum,
                "Equity shareholders of the parent", "Non-controlling interests",
                "Non-current liabilities", "Current liabilities", 
                "Liabilities related to assets held for sale and discontinued operations"
                FROM EquityLiabilitiesCategories
                WHERE CompanyID = {company_id} AND Date IN {dates} '''.format(company_id=company_id, dates=dates)
    elif table_name == "EquityLiabilities":
        query = '''SELECT CompanyID, "Date",
                "Share capital", "Called up share capital",
                "Treasury shares", "Supplementary capital", "Valuation and exchange differences",
                "Other capitals", "Retained earnings / accumulated losses",
                "Non-current liabilities from derivatives", "Non-current loans and borrowings",
                "Non-current liabilities from bonds", "Non-current liabilities from finance leases",
                "Non-current trade payables", "Long-term provision for employee benefits",
                "Deferred tax liabilities", "Non-current provision", "Other non-current liabilities",
                "Non-current accruals (liability)", "Liabilities from derivatives",
                "Financial liabilities (loans and borrowings)", "Bond liabilities",
                "Liabilities from finance leases", "Trade payables", "Employee benefits",
                "Current tax liabilities", Provisions, "Other liabilities", "Accruals (liability)"
              FROM EquityLiabilities E
              WHERE CompanyID = {company_id} AND Date IN {dates}'''.format(company_id=company_id, dates=dates)
    c.execute(query)
    return c.fetchall()


@with_connection
def get_existing_data_stock_quotes(connection, overlapping_data):
    c = connection.cursor()
    results = []

    for data in overlapping_data["values"]:
        query = '''SELECT CompanyID, "Period end", Stock, Change, Open, High, Low,
              Volume, Turnover, Interval FROM StockQuotes
              WHERE CompanyID = {company} AND "Period end" = ? AND Interval = {interval}''' \
            .format(company=data[0], interval=data[9])
        result = c.execute(query, (data[1],)).fetchall()
        if len(result) > 0:
            results.append(result[0])

    return results


@with_connection
def get_existing_data_ratios(connection, overlapping_data):
    c = connection.cursor()
    date_condition_template = ""
    values = overlapping_data["values"]
    values_length = (len(values))
    for i in range(values_length - 1):
        date_condition_template += ' ( "Period start" = "{start}" AND "Period end" = "{end}" ) OR'.format(start=values[i][1], end=values[i][2])
    date_condition_template += ' ( "Period start" = "{start}" AND "Period end" = "{end}" )'.format(start=values[values_length - 1][1],
                                                                                           end=values[values_length - 1][2])
    query = '''SELECT * FROM {table}  
              WHERE{date_condition}'''.format(table=overlapping_data["table_name"],
                                               date_condition=date_condition_template)
    c.execute(query)
    return c.fetchall()