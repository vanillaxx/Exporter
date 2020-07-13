from DAL.db_utils import with_connection
from Utils.Errors import CompanyNotFoundError


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
    command = '''INSERT OR IGNORE INTO StockQuotes
                (CompanyID, StartDate, EndDate, Stock, Change, Open, High, Low, Volume, Turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    with connection:
        connection.execute(command, values)


def insert_ekd_section(ekd_section):
    insert_value(table_name='EKD_Section', column='Value', value=ekd_section)


def insert_ekd_class(ekd_class):
    insert_value(table_name='EKD_Class', column='Value', value=ekd_class)


def insert_full_company(company_name, isin, company_ticker, company_bloomberg, ekd_section, ekd_class):
    section_id = get_ekd_section_id_from_value(ekd_section=ekd_section)
    class_id = get_ekd_class_id_from_value(ekd_class=ekd_class)
    insert_values(table_name='Company',
                  columns=['Name', 'ISIN', 'Ticker', 'Bloomberg', 'EKD_SectionID', 'EKD_ClassID'],
                  values=[company_name, isin, company_ticker, company_bloomberg, section_id, class_id])


@with_connection
def insert_company(connection, company_name, company_ticker=None, company_isin=None):
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
    c.execute("SELECT ID FROM EKD_Section WHERE Value Like (?)", (int(ekd_section),))
    return c.fetchone()[0]


@with_connection
def get_ekd_class_id_from_value(connection, ekd_class):
    c = connection.cursor()
    c.execute("SELECT ID FROM EKD_Class WHERE Value Like (?)", (int(ekd_class),))
    return c.fetchone()[0]


@with_connection
def get_assets_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, "Date", "Property, plant and equipment" +
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
                WHERE Name = ? 
                ORDER BY A.Date ''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_equity_liabilities_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, "Date",
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
              WHERE Name = ? ''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_assets_equity_liabilities_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, E."Date",
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
                WHERE Name = ? 
                ORDER BY E.Date''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_assets_categories_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, "Date", "Non-current assets" + "Current assets" +
                "Assets held for sale and discontinuing operations" +
                "Called up capital" + "Own shares" AS Sum,
                "Non-current assets", "Current assets",
                "Assets held for sale and discontinuing operations",
                "Called up capital", "Own shares"
                FROM AssetsCategories AC 
                JOIN Company C ON C.ID = AC.CompanyID
                WHERE Name = ? 
                ORDER BY AC.Date''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_equity_liabilities_categories_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, "Date", 
                "Equity shareholders of the parent" + "Non-controlling interests" +
                "Non-current liabilities" + "Current liabilities" + 
                "Liabilities related to assets held for sale and discontinued operations" AS Sum,
                "Equity shareholders of the parent", "Non-controlling interests",
                "Non-current liabilities", "Current liabilities", 
                "Liabilities related to assets held for sale and discontinued operations"
                FROM EquityLiabilitiesCategories EC 
                JOIN Company C ON C.ID = EC.CompanyID
                WHERE Name = ? 
                ORDER BY EC.Date''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_full_assets_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, A."Date", "Property, plant and equipment" +
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
                WHERE Name = ? 
                ORDER BY A.Date''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_du_pont_indicators_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, PeriodStart, PeriodEnd, "Return on equity (ROE)",
                "Return on assets (ROA)", "Leverage (EM)", "Net profit margin",
                "Asset utilization (AU)", "Load gross profit", "Load operating profit",
                "Operating profit margin", "EBITDA margin"
              FROM DuPontIndicators D
              JOIN Company C ON C.ID = D.CompanyID
              WHERE Name = ? ''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_financial_ratios_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, PeriodStart, PeriodEnd,
                "Gross profit margin on sales", "Operating profit margin",
                "Gross profit margin", "Net profit margin", "Return on equity (ROE)",
                "Return on assets (ROA)", "Working capital ratio", "Current ratio",
                "Quick ratio","Cash ratio", "Receivables turnover", "Inventory turnover",
                "The operating cycle", "Rotation commitments", "Cash conversion cycle",
                "Rotation assets", "Rotation of assets", "Assets ratio", "Debt ratio",
                "Debt service ratio", "Rate debt security"
              FROM FinancialRatios F
              JOIN Company C ON C.ID = F.CompanyID
              WHERE Name = ? ''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def get_full_equities_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, E."Date",
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
              WHERE Name = ? ''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def export_stock_quotes(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, StartDate, EndDate, Stock, Change, "Open", High, Low, Volume, Turnover
                FROM StockQuotes SQ 
                JOIN Company C ON C.ID = SQ.CompanyID
                WHERE Name = ? 
                ORDER BY SQ.StartDate''', (company_name,))
    return c.fetchall(), list(map(lambda x: x[0], c.description))


@with_connection
def insert_market_value(connection, market_value, end_date, company_name, company_isin=None):
    # TODO updating information about company
    company_id = get_company_id_from_isin(company_isin) or get_company_id_from_name(company_name)
    data = (company_id, end_date, market_value)
    if company_id:
        command = '''INSERT INTO MarketValues(CompanyID, PeriodEnd, MarketValue) VALUES (?, ?, ?)'''
        with connection:
            connection.execute(command, data)
    else:
        raise CompanyNotFoundError
