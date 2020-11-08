from common.DAL.db_utils import with_connection
from common.Utils.Errors import DatabaseImportError


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
