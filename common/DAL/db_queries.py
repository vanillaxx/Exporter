from common.DAL.db_utils import with_connection
from common.Utils.Errors import CompanyNotFoundError


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
    c.execute('''SELECT C.Name, "Date", "Property, plant and equipment" + "Exploration for and evaluation of mineral resources" +
                "Intangible assets" + Goodwill + "Investment property" + "Investment in affiliates" + "Non-current financial assets" +
                "Non-current loans and receivables" + "Deferred income tax" + "Non-current deferred charges and accruals" +
                "Non-current derivative instruments" + "Other non-current assets" + Inventories + "Current intangible assets" +
                "Biological assets" + "Trade receivables" + "Loans and other receivables" + "Financial assets" +
                "Cash and cash equivalents" + Accruals + "Assets from current tax" + "Derivative instruments" + "Other assets",
                "Property, plant and equipment", "Exploration for and evaluation of mineral resources",
                "Intangible assets", Goodwill, "Investment property", "Investment in affiliates", "Non-current financial assets",
                "Non-current loans and receivables", "Deferred income tax", "Non-current deferred charges and accruals",
                "Non-current derivative instruments", "Other non-current assets", Inventories, "Current intangible assets",
                "Biological assets", "Trade receivables", "Loans and other receivables", "Financial assets",
                "Cash and cash equivalents", Accruals, "Assets from current tax", "Derivative instruments", "Other assets"
                FROM Assets A 
                JOIN Company C ON C.ID = A.CompanyID
                WHERE Name = ? ''', (company_name,))
    return c.fetchall()


@with_connection
def get_equity_liabilities_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, "Date", "Share capital", "Called up share capital", "Treasury shares", "Supplementary capital", "Valuation and exchange differences", "Other capitals", "Retained earnings / accumulated losses", "Non-current liabilities from derivatives", "Non-current loans and borrowings", "Non-current liabilities from bonds", "Non-current liabilities from finance leases", "Non-current trade payables", "Long-term provision for employee benefits", "Deferred tax liabilities", "Non-current provision", "Other non-current liabilities", "Non-current accruals (liability)", "Liabilities from derivatives", "Financial liabilities (loans and borrowings)", "Bond liabilities", "Liabilities from finance leases", "Trade payables", "Employee benefits", "Current tax liabilities", Provisions, "Other liabilities", "Accruals (liability)"
              FROM EquityLiabilities E 
              JOIN Company C ON C.ID = E.CompanyID
              WHERE Name = ? ''', (company_name,))
    return c.fetchall()


@with_connection
def get_assets_equity_liabilities_for_company(connection, company_name):
    c = connection.cursor()
    c.execute('''SELECT C.Name, E."Date", "Share capital", "Called up share capital", "Treasury shares",
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
                WHERE Name = ? ''', (company_name,))
    return c.fetchall()


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
