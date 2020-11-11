from common.DAL.db_queries_get import get_ekd_section_id_from_value, get_ekd_class_id_from_value
from common.Utils.company_unification import Company
from common.DAL.db_utils import with_connection


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
