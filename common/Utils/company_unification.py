import re
import string
import unicodedata
from fuzzywuzzy import fuzz
from cleanco import prepare_terms, basename


class Company:
    def __init__(self, name, ticker, bloomberg, isin=None):
        self.name = name
        self.ticker = ticker
        self.isin = isin
        self.bloomberg = bloomberg

    def standardise(self):
        if self.name is not None:
            self.name = standardise(self.name)
        if self.ticker is not None:
            self.ticker = self.ticker.upper()
        if self.isin is not None:
            self.isin = self.isin.upper()
        if self.bloomberg is not None:
            self.bloomberg = self.bloomberg.upper()

    def is_similar(self, company):
        tuples_to_compare = [(self.name, company.name),
                             get_acronym_of_longer_name(self.name, company.name),
                             (self.name, company.bloomberg),
                             (self.bloomberg, company.name)]

        return any(compare_names(names_tuple) for names_tuple in tuples_to_compare)


def compare_names(names_tuple):
    name1 = names_tuple[0]
    name2 = names_tuple[1]
    if name1 is None or name2 is None:
        return False

    similarity_threshold = 85
    return max(fuzz.partial_ratio(name1, name2), fuzz.token_set_ratio(name1, name2)) >= similarity_threshold


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

    return name


def strip_legal_terms(name: str):
    terms = prepare_terms()
    additional_terms = ['SPÓŁKA AKCYJNA', 'SPÓŁKA Z O.O.', 'SPÓŁKA Z O. O.', 'SP. Z O.O.', 'SP. Z O. O.']
    additional_terms.extend(list(map(strip_accents, additional_terms)))
    additional_terms.extend(list(map(strip_punctuation_marks, additional_terms)))
    additional_terms = set(additional_terms)

    name = basename(name, terms, prefix=True, middle=True, suffix=True)
    for term in additional_terms:
        name = name.replace(term, '')

    return name


def strip_accents(name: str):
    name = name.replace('Ł', 'L').replace('ł', 'l')
    return str(unicodedata.normalize('NFD', name)
               .encode('ascii', 'ignore')
               .decode('utf-8'))


def strip_punctuation_marks(name: str):
    return name.translate(str.maketrans('', '', string.punctuation))

