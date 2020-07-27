class CompanyNotFoundError(Exception):
    # TODO: consider what we should put here
    def __init__(self, name='', ticker='', isin=''):
        self.name = name
        self.ticker = ticker
        self.isin = isin

    def __str__(self):
        message = 'Company not found.'
        name_details = ' Name: ' + self.name if self.name else ''
        ticker_details = ' Ticker: ' + self.ticker if self.ticker else ''
        isin_details = ' ISIN: ' + self.isin if self.isin else ''
        return message + name_details + ticker_details + isin_details
