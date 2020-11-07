from common.DAL.db_utils import with_connection
from common.Utils.Errors import CompanyNotFoundError, DatabaseImportError
from common.Utils.company_unification import Company

@with_connection
def exactly_same_dupont_indicators(connection, columns, values):
    c = connection.cursor()
    conditions = [j for i in zip(columns, values) for j in i]
    condition = ' AND '.join([''' "{}" = {} '''] * (len(values) - 3))
    condition = condition.format(*conditions[6:])
    query = '''SELECT 1 FROM DuPontIndicators
               WHERE CompanyID = {company_id}
               AND "Period start" = '{start}'
               AND "Period end" = '{end}'
               AND {condition}'''.format(company_id=values[0],
                                         start=values[1],
                                         end=values[2],
                                         condition=condition)
    c.execute(query)
    return c.fetchall()

@with_connection
def exactly_same_financial_ratios(connection, columns, values):
    c = connection.cursor()
    conditions = [j for i in zip(columns, values) for j in i]
    condition = ' AND '.join([''' "{}" = {} '''] * (len(values) - 3))
    condition = condition.format(*conditions[6:])
    query = '''SELECT 1 FROM FinancialRatios
               WHERE CompanyID = {company_id}
               AND "Period start" = '{start}'
               AND "Period end" = '{end}'
               AND {condition}'''.format(company_id=values[0],
                                         start=values[1],
                                         end=values[2],
                                         condition=condition)
    c.execute(query)
    return c.fetchall()

@with_connection
def exactly_same_equity_liabilities_categories(connection, columns, values):
    c = connection.cursor()
    conditions = [j for i in zip(columns, values) for j in i]
    condition = ' AND '.join([''' "{}" = {} '''] * (len(values) - 2))
    condition = condition.format(*conditions[4:])
    query = '''SELECT 1 FROM EquityLiabilitiesCategories
               WHERE CompanyID = {company_id}
               AND Date = '{date}'
               AND {condition}'''.format(company_id=values[0],
                                         date=values[1],
                                         condition=condition)
    c.execute(query)
    return c.fetchall()


@with_connection
def exactly_same_equity_liabilities(connection, columns, values):
    c = connection.cursor()
    conditions = [j for i in zip(columns, values) for j in i]
    condition = ' AND '.join([''' "{}" = {} '''] * (len(values) - 2))
    condition = condition.format(*conditions[4:])
    query = '''SELECT 1 FROM EquityLiabilities
               WHERE CompanyID = {company_id}
               AND Date = '{date}'
               AND {condition}'''.format(company_id=values[0],
                                         date=values[1],
                                         condition=condition)
    c.execute(query)
    return c.fetchall()


@with_connection
def exactly_same_assets_categories(connection, columns, values):
    c = connection.cursor()
    conditions = [j for i in zip(columns, values) for j in i]
    condition = ' AND '.join([''' "{}" = {} '''] * (len(values) - 2))
    condition = condition.format(*conditions[4:])
    query = '''SELECT 1 FROM AssetsCategories
               WHERE CompanyID = {company_id}
               AND Date = '{date}'
               AND {condition}'''.format(company_id=values[0],
                                         date=values[1],
                                         condition=condition)
    c.execute(query)
    return c.fetchall()


@with_connection
def exactly_same_assets(connection, columns, values):
    c = connection.cursor()
    conditions = [j for i in zip(columns, values) for j in i]
    condition = ' AND '.join([''' "{}" = {} '''] * (len(values) - 2))
    condition = condition.format(*conditions[4:])
    query = '''SELECT 1 FROM Assets A
               WHERE CompanyID = {company_id}
               AND Date = '{date}'
               AND {condition}'''.format(company_id=values[0],
                                         date=values[1],
                                         condition=condition)
    c.execute(query)
    return c.fetchall()


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
def merge_stock_quotes(connection, merge_from, merge_to):
    values = merge_to, merge_from
    command = 'UPDATE OR IGNORE StockQuotes SET CompanyId = (?) WHERE CompanyID = (?) '
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
                (CompanyID, Date, Stock, Change, Open, High, Low, Volume, Turnover, Interval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    with connection:
        connection.execute(command, values)


@with_connection
def insert_market_value(connection, company_id, market_value, end_date):
    # TODO updating information about company
    data = (company_id, end_date, market_value)
    command = '''INSERT INTO MarketValues(CompanyID, "Period end", "Market value") VALUES (?, ?, ?)'''
    with connection:
        connection.execute(command, data)


def insert_ekd_section(ekd_section):
    insert_value(table_name='EKDSection', column='Value', value=ekd_section)


def insert_ekd_class(ekd_class):
    insert_value(table_name='EKDClass', column='Value', value=ekd_class)


@with_connection
def insert_company(connection, company: Company):
    if company.ekd_section is not None and company.ekd_class is not None:
        company.ekd_section = get_ekd_section_id_from_value(ekd_section=company.ekd_section)
        company.ekd_class = get_ekd_class_id_from_value(ekd_class=company.ekd_class)

    company.standardise()

    values = company.name, company.ticker, company.isin, company.bloomberg, company.ekd_section, company.ekd_class
    command = '''INSERT INTO Company(Name, Ticker, ISIN, Bloomberg, EKDSectionID, EKDClassID) 
                 VALUES (?, ?, ?, ?, ?, ?)'''

    with connection:
        cursor = connection.cursor()
        cursor.execute(command, values)
        company_id = cursor.lastrowid

    return company_id


def get_company(company: Company):
    company.standardise()

    company_id = get_company_id(company.name, company.ticker, company.isin)
    possible_companies = []

    if company_id is None:
        companies = get_all_companies_info()
        possible_companies = company.get_possible_matches(companies)

    return company_id, possible_companies


@with_connection
def get_company_id(connection, company_name, company_ticker, company_isin):
    c = connection.cursor()
    query = '''SELECT ID FROM Company
              WHERE Name = ?
              OR Ticker = ?
              OR ISIN = ?'''
    c.execute(query, (company_name, company_ticker, company_isin))
    company = c.fetchone()
    if not company:
        return None
    return company[0]


@with_connection
def get_all_companies_info(connection):
    c = connection.cursor()
    c.execute("SELECT ID, Name, Ticker, Bloomberg FROM Company ")
    return c.fetchall()


@with_connection
def get_ekd_section_id_from_value(connection, ekd_section):
    c = connection.cursor()
    c.execute("SELECT ID FROM EKDSection WHERE Value = (?)", (int(ekd_section),))
    return c.fetchone()[0]


@with_connection
def get_ekd_class_id_from_value(connection, ekd_class):
    c = connection.cursor()
    c.execute("SELECT ID FROM EKDClass WHERE Value = (?)", (int(ekd_class),))
    return c.fetchone()[0]


@with_connection
def get_interval_id_from_shortcut(connection, shortcut):
    c = connection.cursor()
    c.execute("SELECT ID FROM Interval WHERE Shortcut = ?", (shortcut,))
    interval = c.fetchone()
    if not interval:
        return None
    return interval[0]


@with_connection
def get_assets_for_companies(connection, company_ids, start_date, end_date, months):
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
                AND strftime('%m',  A.Date) IN ({months_seq}) 
                ORDER BY C.Name, A.Date '''.format(seq=','.join(['?'] * len(company_ids)),
                                                   months_seq=','.join(['?'] * len(months)))
    company_ids.extend([start_date, end_date])
    company_ids.extend(months)
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_equity_liabilities_for_companies(connection, company_ids, start_date, end_date, months):
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
                AND strftime('%m',  E.Date) IN ({months_seq}) 
                ORDER BY C.Name, E.Date '''.format(seq=','.join(['?'] * len(company_ids)),
                                                   months_seq=','.join(['?'] * len(months)))
    company_ids.extend([start_date, end_date])
    company_ids.extend(months)
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_assets_equity_liabilities_for_companies(connection, company_ids, start_date, end_date, months):
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
                AND strftime('%m',  E.Date) IN ({months_seq}) 
                ORDER BY C.Name, E.Date '''.format(seq=','.join(['?'] * len(company_ids)),
                                                   months_seq=','.join(['?'] * len(months)))
    company_ids.extend([start_date, end_date])
    company_ids.extend(months)
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_assets_categories_for_companies(connection, company_ids, start_date, end_date, months):
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
                AND strftime('%m',  AC.Date) IN ({months_seq}) 
                ORDER BY C.Name, AC.Date '''.format(seq=','.join(['?'] * len(company_ids)),
                                                    months_seq=','.join(['?'] * len(months)))
    company_ids.extend([start_date, end_date])
    company_ids.extend(months)
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_equity_liabilities_categories_for_companies(connection, company_ids, start_date, end_date, months):
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
                AND strftime('%m',  EC.Date) IN ({months_seq}) 
                ORDER BY C.Name, EC.Date '''.format(seq=','.join(['?'] * len(company_ids)),
                                                    months_seq=','.join(['?'] * len(months)))
    company_ids.extend([start_date, end_date])
    company_ids.extend(months)
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_full_assets_for_companies(connection, company_ids, start_date, end_date, months):
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
                AND strftime('%m',  AC.Date) IN ({months_seq}) 
                ORDER BY C.Name, AC.Date '''.format(seq=','.join(['?'] * len(company_ids)),
                                                    months_seq=','.join(['?'] * len(months)))
    company_ids.extend([start_date, end_date])
    company_ids.extend(months)
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_du_pont_indicators_for_companies(connection, company_ids, start_date, end_date, months):
    c = connection.cursor()
    months_condition = ' OR '.join(['''( strftime('%m',  D.'Period start') = ?
                                    AND strftime('%m',  D.'Period end') = ? )'''] * len(months))
    query = '''SELECT C.Name, "Period start", "Period end", "Return on equity (ROE)",
                "Return on assets (ROA)", "Leverage (EM)", "Net profit margin",
                "Asset utilization (AU)", "Load gross profit", "Load operating profit",
                "Operating profit margin", "EBITDA margin"
              FROM DuPontIndicators D
              JOIN Company C ON C.ID = D.CompanyID
                WHERE C.ID IN ({seq}) 
                AND D."Period start" >= ?
                AND D."Period end" <= ?
                AND {months_condition}
                ORDER BY C.Name, D."Period start" '''.format(seq=','.join(['?'] * len(company_ids)),
                                                             months_condition=months_condition)
    company_ids.extend([start_date, end_date])
    months_list = [month for pair in months for month in pair]
    company_ids.extend(months_list)
    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_financial_ratios_for_companies(connection, company_ids, start_date, end_date, months):
    c = connection.cursor()
    months_condition = ' OR '.join(['''( strftime('%m',  D.'Period start') = ?
                                    AND strftime('%m',  D.'Period end') = ? )'''] * len(months))
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
                AND {months_condition} 
                ORDER BY C.Name, F."Period start" '''.format(seq=','.join(['?'] * len(company_ids)),
                                                             months_condition=months_condition)
    company_ids.extend([start_date, end_date])
    months_list = [month for pair in months for month in pair]
    company_ids.extend(months_list)
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
    query = '''SELECT C.Name, Date, Stock, Change, "Open", High, Low, Volume, Turnover
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
        query = '''SELECT C.Name, "Market value", "Period end"
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
        query = '''SELECT C.Name, "Market value", "Period end"
                             FROM MarketValues MV
                             JOIN Company C ON C.ID = MV.CompanyID
                             WHERE C.ID IN ({seq}) 
                             AND MV."Period end" BETWEEN ? AND ?
                             ORDER BY C.Name, MV."Period end" '''.format(seq=','.join(['?'] * len(company_ids)))
        company_ids.extend([start_date, end_date])

    c.execute(query, tuple(company_ids))
    return c.fetchall(), list(map(lambda x: x[0], c.description))



@with_connection
def get_existing_data_balance_sheet(connection, overlapping_data):
    c = connection.cursor()
    table_name = overlapping_data["table_name"]
    query = ''''''
    values = overlapping_data["values"]
    if len(values) == 1:
        dates = "('{}')".format(values[0][1])
    else:
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
        query = '''SELECT CompanyID, "Date",
                "Non-current assets", "Current assets",
                "Assets held for sale and discontinuing operations",
                "Called up capital", "Own shares"
                 FROM AssetsCategories
                WHERE CompanyID = {company_id} AND Date IN {dates} '''.format(company_id=company_id, dates=dates)
    elif table_name == "EquityLiabilitiesCategories":
        query = '''SELECT CompanyID, "Date",
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
        query = '''SELECT CompanyID, Date, Stock, Change, Open, High, Low,
              Volume, Turnover, Interval FROM StockQuotes
              WHERE CompanyID = {company} AND Date = ? AND Interval = {interval}''' \
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
        date_condition_template += ' ( "Period start" = "{start}" AND "Period end" = "{end}" ) OR'.format(
            start=values[i][1], end=values[i][2])
    date_condition_template += ' ( "Period start" = "{start}" AND "Period end" = "{end}" )'.format(
        start=values[values_length - 1][1],
        end=values[values_length - 1][2])
    query = '''SELECT * FROM {table}  
              WHERE{date_condition}'''.format(table=overlapping_data["table_name"],
                                              date_condition=date_condition_template)
    c.execute(query)
    return c.fetchall()


@with_connection
def merge_database(connection, path):
    try:
        connection.execute('ATTACH DATABASE ? AS to_import', (path,))

        connection.execute('''INSERT INTO main.EKDClass(ID, Value) SELECT ID, Value FROM to_import.EKDClass;''')
        connection.commit()
        connection.execute('''INSERT INTO main.EKDSection(ID, Value) SELECT ID, Value FROM to_import.EKDSection;''')
        connection.commit()

        connection.execute('''INSERT INTO main.Company(ID, Name, ISIN, Ticker, Bloomberg, EKDSectionID, EKDClassID)
                        SELECT ID, Name, ISIN, Ticker, Bloomberg, EKDSectionID, EKDClassID FROM to_import.Company;''')
        connection.commit()

        connection.execute('''INSERT INTO main.StockQuotes(ID, CompanyID, Date, Stock, Change, Open,
                        High, Low, Volume, Turnover, Interval)
                        SELECT ID, CompanyID, Date, Stock, Change, Open,
                        High, Low, Volume, Turnover, Interval FROM to_import.StockQuotes;''')
        connection.commit()
        connection.execute('''INSERT INTO main.Assets(ID, CompanyID, Date, "Property, plant and equipment", 
                        "Exploration for and evaluation of mineral resources", "Intangible assets", Goodwill,
                        "Investment property", "Investment in affiliates", "Non-current financial assets", 
                        "Non-current loans and receivables", "Deferred income tax",
                        "Non-current deferred charges and accruals", "Non-current derivative instruments",
                        "Other non-current assets", Inventories, "Current intangible assets", "Biological assets", 
                        "Trade receivables", "Loans and other receivables",
                        "Financial assets", "Cash and cash equivalents", Accruals, "Assets from current tax",
                        "Derivative instruments", "Other assets")
                        SELECT ID, CompanyID, Date, "Property, plant and equipment", 
                        "Exploration for and evaluation of mineral resources", "Intangible assets", Goodwill,
                        "Investment property", "Investment in affiliates", "Non-current financial assets", 
                        "Non-current loans and receivables", "Deferred income tax",
                        "Non-current deferred charges and accruals", "Non-current derivative instruments",
                        "Other non-current assets", Inventories, "Current intangible assets", "Biological assets", 
                        "Trade receivables", "Loans and other receivables",
                        "Financial assets", "Cash and cash equivalents", Accruals, "Assets from current tax",
                        "Derivative instruments", "Other assets" FROM to_import.Assets;''')
        connection.commit()
        connection.execute('''INSERT INTO main.AssetsCategories(ID, CompanyID, "Non-current assets", "Current assets",
                        "Assets held for sale and discontinuing operations", "Called up capital", "Own shares")
                        SELECT ID, CompanyID, "Non-current assets", "Current assets",
                        "Assets held for sale and discontinuing operations", "Called up capital", "Own shares"
                         FROM to_import.AssetsCategories;''')
        connection.commit()
        connection.execute('''INSERT INTO main.DuPontIndicators(ID, CompanyID, "Period start", "Period end",
                        "Return on equity (ROE)", "Return on assets (ROA)", "Leverage (EM)", "Net profit margin",
                        "Asset utilization (AU)", "Load gross profit", "Load operating profit",
                        "Operating profit margin", "EBITDA margin")
                        SELECT ID, CompanyID, "Period start", "Period end",
                        "Return on equity (ROE)", "Return on assets (ROA)", "Leverage (EM)", "Net profit margin",
                        "Asset utilization (AU)", "Load gross profit", "Load operating profit",
                        "Operating profit margin", "EBITDA margin" FROM to_import.DuPontIndicators;''')
        connection.commit()
        connection.execute('''INSERT INTO main.EquityLiabilities(ID, CompanyID, Date, "Share capital",
                        "Called up share capital", "Treasury shares", "Supplementary capital",
                        "Valuation and exchange differences", "Retained earnings / accumulated losses",
                        "Non-current liabilities from derivatives", "Non-current loans and borrowings",
                        "Non-current liabilities from bonds", "Non-current liabilities from finance leases",
                        "Non-current trade payables", "Long-term provision for employee benefits",
                        "Deferred tax liabilities", "Non-current provision", "Other non-current liabilities",
                        "Non-current accruals (liability)", "Liabilities from derivatives",
                        "Financial liabilities (loans and borrowings)", "Bond liabilities",
                        "Liabilities from finance leases", "Trade payables", "Employee benefits",
                        "Current tax liabilities", Provisions, "Other liabilities", "Accruals (liability)")
                        SELECT ID, CompanyID, Date, "Share capital",
                        "Called up share capital", "Treasury shares", "Supplementary capital",
                        "Valuation and exchange differences", "Retained earnings / accumulated losses",
                        "Non-current liabilities from derivatives", "Non-current loans and borrowings",
                        "Non-current liabilities from bonds", "Non-current liabilities from finance leases",
                        "Non-current trade payables", "Long-term provision for employee benefits",
                        "Deferred tax liabilities", "Non-current provision", "Other non-current liabilities",
                        "Non-current accruals (liability)", "Liabilities from derivatives",
                        "Financial liabilities (loans and borrowings)", "Bond liabilities",
                        "Liabilities from finance leases", "Trade payables", "Employee benefits",
                        "Current tax liabilities", Provisions, "Other liabilities", "Accruals (liability)"
                        FROM to_import.EquityLiabilities;''')
        connection.commit()
        connection.execute('''INSERT INTO main.EquityLiabilitiesCategories(ID, CompanyID, Date, 
                        "Equity shareholders of the parent", "Non-controlling interests", "Non-current liabilities",
                        "Current liabilities",
                        "Liabilities related to assets held for sale and discontinued operations")
                        SELECT ID, CompanyID, Date, 
                        "Equity shareholders of the parent", "Non-controlling interests", "Non-current liabilities",
                        "Current liabilities",
                        "Liabilities related to assets held for sale and discontinued operations"
                        FROM to_import.EquityLiabilitiesCategories;''')
        connection.commit()
        connection.execute('''INSERT INTO main.FinancialRatios(ID, CompanyID, "Period start", "Period end",
                        "Gross profit margin on sales", "Operating profit margin","Gross profit margin",
                        "Net profit margin", "Return on equity (ROE)", "Return on assets (ROA)",
                        "Working capital ratio", "Current ratio", "Quick ratio", "Cash ratio",
                        "Receivables turnover", "Inventory turnover", "The operating cycle", "Rotation commitments",
                        "Cash conversion cycle", "Rotation assets", "Rotation of assets", "Assets ratio",
                        "Debt ratio", "Debt service ratio", "Rate debt security")
                        SELECT ID, CompanyID, "Period start", "Period end",
                        "Gross profit margin on sales", "Operating profit margin","Gross profit margin",
                        "Net profit margin", "Return on equity (ROE)", "Return on assets (ROA)",
                        "Working capital ratio", "Current ratio", "Quick ratio", "Cash ratio",
                        "Receivables turnover", "Inventory turnover", "The operating cycle", "Rotation commitments",
                        "Cash conversion cycle", "Rotation assets", "Rotation of assets", "Assets ratio",
                        "Debt ratio", "Debt service ratio", "Rate debt security" FROM to_import.FinancialRatios;''')
        connection.commit()
        connection.execute('''INSERT INTO main.MarketValues(ID, CompanyID, "Period end", "Market value")
                        SELECT ID, CompanyID, "Period end", "Market value" FROM to_import.MarketValues;''')
        connection.commit()
    except Exception as e:
        raise DatabaseImportError(e)



@with_connection
def get_existing_data_financial_ratios(connection, company_id, overlapping_dates):
    c = connection.cursor()
    dates_condition = ' OR '.join(['''( "Period start" = '%s' AND "Period end" = '%s' )'''] * len(overlapping_dates))
    overlapping_dates = [date for row in overlapping_dates for date in row]
    dates_condition = dates_condition % tuple(overlapping_dates)
    query = '''SELECT C.ID, "Period start", "Period end", "Gross profit margin on sales", "Operating profit margin",
                      "Gross profit margin", "Net profit margin", "Return on equity (ROE)", "Return on assets (ROA)",
                      "Working capital ratio", "Current ratio", "Quick ratio", "Cash ratio", "Receivables turnover",
                      "Inventory turnover", "The operating cycle", "Rotation commitments", "Cash conversion cycle",
                      "Rotation assets", "Rotation of assets", "Assets ratio", "Debt ratio", "Debt service ratio",
                      "Rate debt security" 
                FROM FinancialRatios FR
                JOIN Company C on FR.CompanyID = C.ID
                WHERE FR.CompanyID = {company_id}
                AND ( {dates_condition} )
                ORDER BY FR."Period start", FR."Period end"'''.format(company_id=company_id, dates_condition=dates_condition)
    c.execute(query)
    return c.fetchall()


@with_connection
def get_existing_data_dupont_indicators(connection, company_id, overlapping_dates):
    c = connection.cursor()
    dates_condition = ' OR '.join(['''( "Period start" = '%s' AND "Period end" = '%s' )'''] * len(overlapping_dates))
    overlapping_dates = [date for row in overlapping_dates for date in row]
    dates_condition = dates_condition % tuple(overlapping_dates)

    query = '''SELECT C.ID, "Period start" timestamp, "Period end" timestamp, "Return on equity (ROE)", "Return on assets (ROA)",
               "Leverage (EM)", "Net profit margin", "Asset utilization (AU)", "Load gross profit",
               "Load operating profit", "Operating profit margin", "EBITDA margin"
               FROM DuPontIndicators DP  
               JOIN Company C ON C.ID = DP.CompanyID
               WHERE DP.CompanyID = {company_id}
               AND ( {dates_condition} )
               ORDER BY DP."Period start", DP."Period end"'''.format(company_id=company_id, dates_condition=dates_condition)
    c.execute(query)
    return c.fetchall()