from common.Utils.company_unification import strip_legal_terms, standardise, compare_names, get_acronym_of_longer_name


def test_strip_legal_terms():
    names = [
        ('AB SA', 'AB'),
        ('CCC SPÓŁKA AKCYJNA', 'CCC'),
        ('CYFROWY POLSAT SA', 'CYFROWY POLSAT')
    ]

    for name, expected in names:
        assert strip_legal_terms(name) == expected


def test_standardise():
    names = [
        ('Bank Millenium SA', 'BANK MILLENIUM'),
        ('CCC  SPÓŁKA  AKCYJNA', 'CCC'),
        (' Cyfrowy Polsat SA  ', 'CYFROWY POLSAT')
    ]

    for name, expected in names:
        assert standardise(name) == expected


def test_get_acronym_of_longer_name():
    names = [
        (('PKN ORLEN', 'Polski Koncert Naftowy ORLEN'), ('PKNO', 'PKN ORLEN')),
        (('MILLENIUM', 'CCC'), (None, None)),
        (('GRUPA APATOR', 'APATOR'), (None, None))
    ]

    for names, expected in names:
        assert get_acronym_of_longer_name(names[0], names[1]) == expected


def test_compare_names():
    name1 = 'name'
    name2 = None
    name3 = ''

    assert compare_names((name1, name2)) is False
    assert compare_names((name1, name3)) is False

