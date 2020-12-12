import json
import re
import string
import unicodedata
from fuzzywuzzy import fuzz


class Company:
    def __init__(self, name, ticker=None, bloomberg=None, isin=None, ekd_class=None, ekd_section=None, *args, **kwargs):
        self.name = name
        self.ticker = ticker
        self.isin = isin
        self.bloomberg = bloomberg
        self.ekd_class = ekd_class
        self.ekd_section = ekd_section

    def standardise(self):
        if self.name is not None:
            self.name = standardise(self.name)
        if self.ticker is not None:
            self.ticker = self.ticker.upper()
        if self.isin is not None:
            self.isin = self.isin.upper()
        if self.bloomberg is not None:
            self.bloomberg = self.bloomberg.upper()

    def get_possible_matches(self, companies):
        return [(json.dumps((id, name)), name) for (id, name, ticker, isin, bloomberg) in companies
                if self.is_similar(Company(name=name, ticker=ticker, isin=isin, bloomberg=bloomberg))]

    def is_similar(self, company):
        tuples_to_compare = [(self.name, company.name),
                             get_acronym_of_longer_name(self.name, company.name),
                             (self.name, company.bloomberg),
                             (self.bloomberg, company.name)]

        if self.ticker and company.ticker and self.ticker != company.ticker:
            return False

        if self.isin and company.isin and self.isin != company.isin:
            return False

        return any(compare_names(names_tuple) for names_tuple in tuples_to_compare)

    def __str__(self):
        return f'company: {self.name} {self.isin} {self.ticker} {self.bloomberg}'


def compare_names(names_tuple):
    name1 = names_tuple[0]
    name2 = names_tuple[1]
    if not name1 or not name2:
        return False
    if len(name1) < 3 < len(name2) or len(name2) < 3 < len(name1):
        return False

    similarity_threshold = 85
    return fuzz.partial_ratio(name1, name2) >= similarity_threshold


def get_acronym_of_longer_name(name1: str, name2: str):
    if name1 is None or name2 is None:
        return None, None

    if len(name1) >= len(name2):
        acronym, name = get_acronym(name1), name2
    else:
        acronym, name = get_acronym(name2), name1

    if len(acronym) >= 3:
        return acronym, name
    else:
        return None, None


def get_acronym(name: str):
    return ''.join([word[0] for word in strip_punctuation_marks(name).split()])


def standardise(name: str):
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)
    name = name.upper()
    name = strip_legal_terms(name)

    if not name:
        name = None

    return name


def strip_legal_terms(name: str):
    terms = ['SPÓŁKA AKCYJNA', 'SPÓŁKA Z O.O.', 'SPÓŁKA Z O. O.', 'SP. Z O.O.', 'SP. Z O. O.',
             'S.A.', 'S.P.A.', 'S.P.A', 'PLC']
    terms.extend(list(map(strip_accents, terms)))
    terms.extend(list(map(strip_punctuation_marks, terms)))
    terms = set(terms)

    terms = list(map(lambda s: s.replace('.', '\\.'), terms))
    middle_terms = terms.copy()
    middle_terms.remove('SPA')

    end_term_pattern = re.compile(f" ({'|'.join(terms)})$")
    middle_term_pattern = re.compile(f" ({'|'.join(middle_terms)}) ")

    name = re.sub(middle_term_pattern, ' ', name, 1)
    name = re.sub(end_term_pattern, '', name, 1)

    name = re.sub(r'\s+', ' ', name)
    name = name.strip()

    return name


def strip_accents(name: str):
    name = name.replace('Ł', 'L').replace('ł', 'l')
    return str(unicodedata.normalize('NFD', name)
               .encode('ascii', 'ignore')
               .decode('utf-8'))


def strip_punctuation_marks(name: str):
    return name.translate(str.maketrans('', '', string.punctuation))
