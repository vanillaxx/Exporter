import sqlite3


def with_connection(func):
    """ create a database connection to a SQLite database """

    def with_connection_(*args, **kwargs):
        database_path = 'exporter.db'
        conn = None
        try:
            conn = sqlite3.connect(database_path)
            res = func(conn, *args, **kwargs)
        except sqlite3.DatabaseError as e:
            print(e)
        finally:
            if conn:
                conn.close()
        return res

    return with_connection_


@with_connection
def set_up_database_tables(conn):
    with conn:
        conn.execute("PRAGMA foreign_keys = 1")
        conn.execute('''CREATE TABLE IF NOT EXISTS Company
        (ID INTEGER PRIMARY KEY AUTOINCREMENT, Name varchar unique);''')
        conn.execute('''CREATE TABLE IF NOT EXISTS EquityLiabilities
        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CompanyID INTEGER,
        Date TEXT,
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

        conn.execute('''CREATE TABLE IF NOT EXISTS Assets
                (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CompanyID INTEGER,
                Date TEXT,
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
                'Assets held for sale and discontinuing operations' REAL,
                'Called up capital' REAL,
                'Own shares' REAL,
                FOREIGN KEY(CompanyID) REFERENCES Company(ID)
                );''')
        #insert value for testing
        conn.execute('''INSERT INTO Company(Name) VALUES ('Agora')''')



@with_connection
def insert_values(conn, table_name, columns, values):
    values = tuple(values)
    columns = tuple(columns)
    command = 'INSERT INTO %s%s values %s ' % (table_name, columns, values)
    with conn:
        conn.execute(command)


@with_connection
def get_company_id_from_name(conn, company_name):
    company_name = company_name.upper()
    c = conn.cursor()
    c.execute("SELECT ID FROM Company WHERE Name Like ?", (company_name,))
    return c.fetchone()[0]