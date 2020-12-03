class CompanyNotFoundError(Exception):
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


class ParseError(Exception):
    def __init__(self, source, details=''):
        self.source = source
        self.details = details

    def __str__(self):
        message = 'Cannot parse data. Not compatible with convention. Source: ' + self.source + '.'
        return message + ' ' + self.details if self.details else message


class UniqueError(Exception):
    def __init__(self, *overlapping_data):
        self.overlapping_data = overlapping_data

    def __str__(self):
        return 'Data for such company and dates already exists.\n'


class DatabaseImportError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'Error occurred while importing database: {}'.format(str(self.error))


class DateError(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return f'Cannot parse date in file {self.path}. ' \
            f'Enter end date of the period for which the data was collected (e.g. 31.12.2018 for 2019 Yearbook).'
