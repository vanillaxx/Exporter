import sqlite3


def with_connection(func):
    """ create a database connection to a SQLite database """

    def with_connection_(*args, **kwargs):
        database_path = 'exporter.db'
        connection = None
        try:
            connection = sqlite3.connect(database_path)
            res = func(connection, *args, **kwargs)
        except sqlite3.DatabaseError as e:
            print(e)
        finally:
            if connection:
                connection.close()
        return res

    return with_connection_


@with_connection
def set_up_database_tables(connection):
    with connection:
        connection.execute("PRAGMA foreign_keys = 1")

        # creating tables
        set_up_ekd_section_table(connection)
        set_up_ekd_class_table(connection)
        set_up_company_table(connection)
        set_up_equity_liabilities_table(connection)
        set_up_assets_table(connection)
        set_up_assets_categories_table(connection)
        set_up_equity_liabilities_categories_table(connection)
        set_up_stock_quotes_table(connection)
        set_up_financial_ratios_table(connection)
        set_up_du_pont_table(connection)


def set_up_company_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS Company
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name VARCHAR,
        ISIN VARCHAR UNIQUE,
        Ticker VARCHAR UNIQUE,
        Bloomberg VARCHAR,
        EKD_SectionID INTEGER,
        EKD_ClassID INTEGER,
        FOREIGN KEY(EKD_SectionID) REFERENCES EKD_Section(ID),
        FOREIGN KEY(EKD_ClassID) REFERENCES EKD_Class(ID)
        );''')


def set_up_equity_liabilities_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS EquityLiabilities
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CompanyID INTEGER,
        Date DATE,
        'Share capital' REAL,
        'Called up share capital' REAL,
        'Treasury shares' REAL,
        'Supplementary capital' REAL,
        'Valuation and exchange differences' REAL,
        'Other capitals' REAL,
        'Retained earnings / accumulated losses' REAL,
        'Non-current liabilities from derivatives' REAL,
        'Non-current loans and borrowings' REAL,
        'Non-current liabilities from bonds' REAL,
        'Non-current liabilities from finance leases' REAL,
        'Non-current trade payables' REAL,
        'Long-term provision for employee benefits' REAL,
        'Deferred tax liabilities' REAL,
        'Non-current provision' REAL,
        'Other non-current liabilities' REAL,
        'Non-current accruals (liability)' REAL,
        'Liabilities from derivatives' REAL,
        'Financial liabilities (loans and borrowings)' REAL,
        'Bond liabilities' REAL,
        'Liabilities from finance leases' REAL,
        'Trade payables' REAL,
        'Employee benefits' REAL,
        'Current tax liabilities' REAL,
        'Provisions' REAL,
        'Other liabilities' REAL,
        'Accruals (liability)' REAL,
        FOREIGN KEY(CompanyID) REFERENCES Company(ID)
        );''')


def set_up_assets_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS Assets
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CompanyID INTEGER,
            Date DATE,
            'Property, plant and equipment' REAL,
            'Exploration for and evaluation of mineral resources' REAL,
            'Intangible assets' REAL,
            'Goodwill' REAL,
            'Investment property' REAL,
            'Investment in affiliates' REAL,
            'Non-current financial assets' REAL,
            'Non-current loans and receivables' REAL,
            'Deferred income tax' REAL,
            'Non-current deferred charges and accruals' REAL,
            'Non-current derivative instruments' REAL,
            'Other non-current assets' REAL,
            'Inventories' REAL,
            'Current intangible assets' REAL,
            'Biological assets' REAL,
            'Trade receivables' REAL,
            'Loans and other receivables' REAL,
            'Financial assets' REAL,
            'Cash and cash equivalents' REAL,
            'Accruals' REAL,
            'Assets from current tax' REAL,
            'Derivative instruments' REAL,
            'Other assets' REAL,
            FOREIGN KEY(CompanyID) REFERENCES Company(ID)
            );''')


def set_up_assets_categories_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS AssetsCategories
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CompanyID INTEGER,
            Date DATE,
            'Non-current assets' REAL,
            'Current assets' REAL,
            'Assets held for sale and discontinuing operations' REAL,
            'Called up capital' REAL,
            'Own shares' REAL,
            FOREIGN KEY(CompanyID) REFERENCES Company(ID)
            );''')


def set_up_equity_liabilities_categories_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS EquityLiabilitiesCategories
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CompanyID INTEGER,
            Date DATE,
            'Equity shareholders of the parent' REAL,
            'Non-controlling interests' REAL,
            'Non-current liabilities' REAL,
            'Current liabilities' REAL,
            'Liabilities related to assets held for sale and discontinued operations' REAL,
            FOREIGN KEY(CompanyID) REFERENCES Company(ID)
            );''')


def set_up_ekd_section_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS EKD_Section
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Value INTEGER UNIQUE
            );''')


def set_up_ekd_class_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS EKD_Class
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Value INTEGER UNIQUE 
            );''')


def set_up_financial_ratios_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS FinancialRatios
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CompanyID INTEGER,
        PeriodStart DATE,
        PeriodEnd DATE,
        'Gross profit margin on sales' REAL,
        'Operating profit margin' REAL,
        'Gross profit margin' REAL,
        'Net profit margin' REAL,
        'Return on equity (ROE)' REAL,
        'Return on assets (ROA)' REAL,
        'Working capital ratio' REAL,
        'Current ratio' REAL,
        'Quick ratio' REAL,
        'Cash ratio'REAL,
        'Receivables turnover' REAL,
        'Inventory turnover' REAL,
        'The operating cycle' REAL,
        'Rotation commitments' REAL,
        'Cash conversion cycle' REAL,
        'Rotation assets' REAL,
        'Rotation of assets' REAL,
        'Assets ratio' REAL,
        'Debt ratio' REAL,
        'Debt service ratio' REAL,
        'Rate debt security' REAL,
        FOREIGN KEY(CompanyID) REFERENCES Company(ID)
        );''')


def set_up_du_pont_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS DuPontIndicators
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CompanyID INTEGER,
        PeriodStart DATE,
        PeriodEnd DATE,
        'Return on equity (ROE)' REAL,
        'Return on assets (ROA)' REAL,
        'Leverage (EM)' REAL,
        'Net profit margin' REAL,
        'Asset utilization (AU)' REAL,
        'Load gross profit' REAL,
        'Load operating profit' REAL,
        'Operating profit margin' REAL,
        'EBITDA margin' REAL,
        FOREIGN KEY(CompanyID) REFERENCES Company(ID)
        );''')


def set_up_stock_quotes_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS StockQuotes
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CompanyID INTEGER NOT NULL,
        EndDate DATE NOT NULL,
        Stock REAL NOT NULL,
        Change REAL,
        Open REAL,
        High REAL,
        Low REAL,
        Volume INTEGER,
        Turnover INTEGER,
        FOREIGN KEY(CompanyID) REFERENCES Company(ID)
        );''')


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
                (CompanyID, EndDate, Stock, Change, Open, High, Low, Volume, Turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    with connection:
        connection.execute(command, values)


@with_connection
def get_company_id_from_name(connection, company_name):
    company_name = company_name.upper()
    c = connection.cursor()
    c.execute("SELECT ID FROM Company WHERE Name Like ?", (company_name,))
    return c.fetchone()[0]


@with_connection
def get_company_id_from_ticker(connection, ticker):
    company_ticker = ticker.upper()
    c = connection.cursor()
    c.execute("SELECT ID FROM Company WHERE Ticker Like ?", (company_ticker,))
    company = c.fetchone()
    if not company:
        return None
    return company[0]


def insert_ekd_section(ekd_section):
    insert_value(table_name='EKD_Section', column='Value', value=ekd_section)


def insert_ekd_class(ekd_class):
    insert_value(table_name='EKD_Class', column='Value', value=ekd_class)


def insert_company(company_name, isin, company_ticker, company_bloomberg, ekd_section, ekd_class):
    section_id = get_ekd_section_id_from_value(ekd_section=ekd_section)
    class_id = get_ekd_class_id_from_value(ekd_class=ekd_class)
    insert_values(table_name='Company',
                  columns=['Name', 'ISIN', 'Ticker', 'Bloomberg', 'EKD_SectionID', 'EKD_ClassID'],
                  values=[company_name, isin, company_ticker, company_bloomberg, section_id, class_id])


def insert_company(company_name, company_ticker,):
    insert_values(table_name='Company',
                  columns=['Name', 'Ticker'],
                  values=[company_name, company_ticker,])


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


set_up_database_tables()
