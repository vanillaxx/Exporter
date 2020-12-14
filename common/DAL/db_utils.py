import sqlite3
import os
from pathlib import Path


def with_connection(func):
    """ create a database connection to a SQLite database """

    def with_connection_(*args, **kwargs):
        database_path = 'exporter.db'
        connection = None
        res = None
        try:
            connection = sqlite3.connect(database_path)
            res = func(connection, *args, **kwargs)
        except sqlite3.DatabaseError as e:
            raise e
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
        set_up_interval_table(connection)
        set_up_stock_quotes_table(connection)
        set_up_financial_ratios_table(connection)
        set_up_du_pont_table(connection)
        set_up_market_values_table(connection)


def set_up_company_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS Company
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name VARCHAR,
        ISIN VARCHAR UNIQUE,
        Ticker VARCHAR UNIQUE,
        Bloomberg VARCHAR,
        EKDSectionID INTEGER,
        EKDClassID INTEGER,
        FOREIGN KEY(EKDSectionID) REFERENCES EKDSection(ID),
        FOREIGN KEY(EKDClassID) REFERENCES EKDClass(ID)
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
    connection.execute('''CREATE TABLE IF NOT EXISTS EKDSection
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Value INTEGER UNIQUE
            );''')


def set_up_ekd_class_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS EKDClass
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Value INTEGER UNIQUE 
            );''')


def set_up_financial_ratios_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS FinancialRatios
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CompanyID INTEGER,
        'Period start' DATE,
        'Period end' DATE,
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
        'Period start' DATE,
        'Period end' DATE,
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
        Date DATE NOT NULL,
        Stock REAL NOT NULL,
        Change REAL,
        Open REAL,
        High REAL,
        Low REAL,
        Volume INTEGER,
        Turnover INTEGER,
        Interval INTEGER NOT NULL,
        FOREIGN KEY(CompanyID) REFERENCES Company(ID),
        FOREIGN KEY(Interval) REFERENCES Interval(ID)
        );''')


def set_up_interval_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS Interval
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Shortcut CHAR UNIQUE NOT NULL,
        FullName VARCHAR NOT NULL
        );''')

    try:
        connection.execute('INSERT OR IGNORE INTO Interval (Shortcut, FullName) VALUES (\'d\', \'daily\')')
        connection.execute('INSERT OR IGNORE INTO Interval (Shortcut, FullName) VALUES (\'w\', \'weekly\')')
        connection.execute('INSERT OR IGNORE INTO Interval (Shortcut, FullName) VALUES (\'m\', \'monthly\')')
        connection.execute('INSERT OR IGNORE INTO Interval (Shortcut, FullName) VALUES (\'q\', \'quaterly\')')
        connection.execute('INSERT OR IGNORE INTO Interval (Shortcut, FullName) VALUES (\'y\', \'yearly\')')
    except:
        pass


def set_up_market_values_table(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS MarketValues
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CompanyID INTEGER NOT NULL,
        'Period end' DATE,
        'Market value' REAL NOT NULL,
        UNIQUE(CompanyID, 'Period end'), 
        FOREIGN KEY(CompanyID) REFERENCES Company(ID)
        );''')


def company_table_exists():
    path = Path(os.getcwd())

    if path.name == 'scripts':
        path = path.parent

    path_str = os.path.join(path, 'exporter.db')

    try:
        conn = sqlite3.connect(path_str)
        c = conn.cursor()

        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Company' ''')

        if c.fetchone()[0] == 1:
            return True

        return False
    except sqlite3.OperationalError:
        return False


# set_up_database_tables()
