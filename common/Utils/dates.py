from datetime import date, datetime
import calendar
import locale
import re

yearly_patterns = [
    r'Rok (?P<year>\d{4})',
    r'Year (?P<year>\d{4})',
    r'(?P<year>^\d{4}$)',
    r'(?P<year>^\d{4})',
    r'(?P<year>\d{4}$)',
    r'\((?P<year>\d{4})\)',
    r'(?:Statystyki roczne GPW|WSE annual statistics) - (?P<year>\d{4})'
]
halfyearly_patterns = [
    r'(?P<half>I|II) półrocze(?: )+(?P<year>\d{4})',
    r'(?P<half>1st|2nd) Half(?:-year)? (?P<year>\d{4})',
    r'(?P<year>\d{4})(?: )+H(?P<half>1|2)',
    r'(?:Biuletyn Półroczny GPW|WSE Halfyearly Bulletin) \((?P<half>1|2)/(?P<year>\d{4})\)'
]
quarterly_patterns = [
    r'(?P<quarter>I|II|III|IV) (?:kwartał|kw\.) (?P<year>\d{4})',
    r'kw\. (?P<quarter>I|II|III|IV) (?P<year>\d{4})',
    r'(?P<quarter>1st|2nd|3rd|4th) Quarter (?P<year>\d{4})',
    r'Q(?P<quarter>1|2|3|4)(?:,)? (?P<year>\d{4})',
    r'(?P<quarter>1|2|3|4) Q (?P<year>\d{4})',
    r'(?:Biuletyn Kwartalny GPW|WSE Quarterly Bulletin) \((?P<quarter>1|2|3|4)/(?P<year>\d{4})\)',
    r'(?:Statystyki kwartalne GPW|WSE quarterly statistics) - (?P<quarter>1|2|3|4)/(?P<year>\d{4})'
]
monthly_patterns = [
    r'(?P<date>(?:\()?(?:january|february|march|april|may|june|july|august|september|november|december)'
    r'(?:\))?(?:,)? \d{4})',
    r'(?P<pl_date>(?:\()?(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|listopad|grudzień)'
    r'(?:\))?(?:,)? \d{4})',
    r'(?:biuletyn gpw|wse bulletin) \((?P<month>\d{1,2})/(?P<year>\d{4})\) '
]


def find_date_in_yearly_statistics_pdf(page, text):
    def get_date(m):
        year = int(m.group('year'))
        month = 12
        day = 31
        return date(year, month, day)

    for match in filter(bool, (re.search(pattern, text) for pattern in yearly_patterns)):
        if match:
            return get_date(match)

    match = __search_for_year_using_page_dict(page)
    if match:
        return get_date(match)
    else:
        return None


def __search_for_year_using_page_dict(page):
    page_dict = page.getText('dict')

    for block in page_dict['blocks']:
        for lines in block['lines']:
            for spans in lines['spans']:
                text = spans['text']
                match = re.match(r'(?P<year>\d{4}$)', text.strip())
                if match:
                    return match
    return None


def find_date_in_yearly_statistics(text):
    for match in filter(bool, (re.search(pattern, text) for pattern in yearly_patterns)):
        if match:
            year = int(match.group('year'))
            month = 12
            day = 31
            return date(year, month, day)
    return None


def find_date_in_halfyearly_statistics(text):
    first_half = ['I', '1', '1st']
    second_half = ['II', '2', '2nd']

    for match in filter(bool, (re.search(pattern, text) for pattern in halfyearly_patterns)):
        if match:
            year = int(match.group('year'))
            half = match.group('half')
            if half in first_half:
                month = 6
            elif half in second_half:
                month = 12
            else:
                continue
            day = calendar.monthrange(year, month)[1]
            return date(year, month, day)
    return None


def find_date_in_quarterly_statistics(text):
    first = ['I', '1', '1st']
    second = ['II', '2', '2nd']
    third = ['III', '3', '3rd']
    fourth = ['IV', '4', '4th']

    for match in filter(bool, (re.search(pattern, text) for pattern in quarterly_patterns)):
        if match:
            year = int(match.group('year'))
            quarter = match.group('quarter')
            if quarter in first:
                month = 3
            elif quarter in second:
                month = 6
            elif quarter in third:
                month = 9
            elif quarter in fourth:
                month = 12
            else:
                continue
            day = calendar.monthrange(year, month)[1]
            return date(year, month, day)
    return None


def find_date_in_monthly_statistics(text):
    text = text.lower()
    for match in filter(bool, (re.search(pattern, text) for pattern in monthly_patterns)):
        if match:
            groupdict = match.groupdict()
            if 'date' in groupdict or 'pl_date' in groupdict:
                if 'pl_date' in groupdict:
                    locale.setlocale(locale.LC_TIME, 'pl_PL')
                    month_year = re.sub(r'[,()]', '', match.group('pl_date').strip().replace('ń', 'ñ'))
                else:
                    month_year = re.sub(r'[,()]', '', match.group('date').strip())
                try:
                    date_time = datetime.strptime(month_year, '%B %Y')
                except ValueError:
                    continue
                year = date_time.year
                month = date_time.month
            elif 'month' in groupdict and 'year' in groupdict:
                month = int(match.group('month'))
                if month < 1 or month > 12:
                    continue
                year = int(match.group('year'))
            day = calendar.monthrange(year, month)[1]
            return date(year, month, day)
    return None


