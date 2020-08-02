from django.db import models

# Create your models here.


class Assets(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    companyid = models.ForeignKey('Company', models.DO_NOTHING, db_column='CompanyID', blank=True,
                                  null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    property_plant_and_equipment = models.FloatField(db_column='Property, plant and equipment', blank=True,
                                                     null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    exploration_for_and_evaluation_of_mineral_resources = models.FloatField(
        db_column='Exploration for and evaluation of mineral resources', blank=True,
        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    intangible_assets = models.FloatField(db_column='Intangible assets', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    goodwill = models.FloatField(db_column='Goodwill', blank=True, null=True)  # Field name made lowercase.
    investment_property = models.FloatField(db_column='Investment property', blank=True,
                                            null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    investment_in_affiliates = models.FloatField(db_column='Investment in affiliates', blank=True,
                                                 null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_financial_assets = models.FloatField(db_column='Non-current financial assets', blank=True,
                                                     null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_loans_and_receivables = models.FloatField(db_column='Non-current loans and receivables', blank=True,
                                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    deferred_income_tax = models.FloatField(db_column='Deferred income tax', blank=True,
                                            null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_deferred_charges_and_accruals = models.FloatField(db_column='Non-current deferred charges and accruals',
                                                                  blank=True,
                                                                  null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_derivative_instruments = models.FloatField(db_column='Non-current derivative instruments', blank=True,
                                                           null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    other_non_current_assets = models.FloatField(db_column='Other non-current assets', blank=True,
                                                 null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    inventories = models.FloatField(db_column='Inventories', blank=True, null=True)  # Field name made lowercase.
    current_intangible_assets = models.FloatField(db_column='Current intangible assets', blank=True,
                                                  null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    biological_assets = models.FloatField(db_column='Biological assets', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    trade_receivables = models.FloatField(db_column='Trade receivables', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    loans_and_other_receivables = models.FloatField(db_column='Loans and other receivables', blank=True,
                                                    null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    financial_assets = models.FloatField(db_column='Financial assets', blank=True,
                                         null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    cash_and_cash_equivalents = models.FloatField(db_column='Cash and cash equivalents', blank=True,
                                                  null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    accruals = models.FloatField(db_column='Accruals', blank=True, null=True)  # Field name made lowercase.
    assets_from_current_tax = models.FloatField(db_column='Assets from current tax', blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    derivative_instruments = models.FloatField(db_column='Derivative instruments', blank=True,
                                               null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    other_assets = models.FloatField(db_column='Other assets', blank=True,
                                     null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'Assets'


class AssetsCategories(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    companyid = models.ForeignKey('Company', models.DO_NOTHING, db_column='CompanyID', blank=True,
                                  null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    non_current_assets = models.FloatField(db_column='Non-current assets', blank=True,
                                           null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    current_assets = models.FloatField(db_column='Current assets', blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    assets_held_for_sale_and_discontinuing_operations = models.FloatField(
        db_column='Assets held for sale and discontinuing operations', blank=True,
        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    called_up_capital = models.FloatField(db_column='Called up capital', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    own_shares = models.FloatField(db_column='Own shares', blank=True,
                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'AssetsCategories'


class EkdClass(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    value = models.IntegerField(db_column='Value', unique=True, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'EKD_Class'


class EkdSection(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    value = models.IntegerField(db_column='Value', unique=True, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'EKD_Section'


class Company(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    name = models.CharField(db_column='Name', blank=True, null=True, max_length=255)  # Field name made lowercase.
    isin = models.CharField(db_column='ISIN', unique=True, blank=True, null=True,
                            max_length=255)  # Field name made lowercase.
    ticker = models.CharField(db_column='Ticker', unique=True, blank=True, null=True,
                              max_length=255)  # Field name made lowercase.
    bloomberg = models.CharField(db_column='Bloomberg', blank=True, null=True,
                                 max_length=255)  # Field name made lowercase.
    ekd_sectionid = models.ForeignKey('EkdSection', models.DO_NOTHING, db_column='EKD_SectionID', blank=True,
                                      null=True)  # Field name made lowercase.
    ekd_classid = models.ForeignKey('EkdClass', models.DO_NOTHING, db_column='EKD_ClassID', blank=True,
                                    null=True)  # Field name made lowercase.

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'Company'


class DuPontIndicators(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    companyid = models.ForeignKey(Company, models.DO_NOTHING, db_column='CompanyID', blank=True,
                                  null=True)  # Field name made lowercase.
    periodstart = models.DateField(db_column='PeriodStart', blank=True, null=True)  # Field name made lowercase.
    periodend = models.DateField(db_column='PeriodEnd', blank=True, null=True)  # Field name made lowercase.
    return_on_equity_roe_field = models.FloatField(db_column='Return on equity (ROE)', blank=True,
                                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    return_on_assets_roa_field = models.FloatField(db_column='Return on assets (ROA)', blank=True,
                                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    leverage_em_field = models.FloatField(db_column='Leverage (EM)', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    net_profit_margin = models.FloatField(db_column='Net profit margin', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    asset_utilization_au_field = models.FloatField(db_column='Asset utilization (AU)', blank=True,
                                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    load_gross_profit = models.FloatField(db_column='Load gross profit', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    load_operating_profit = models.FloatField(db_column='Load operating profit', blank=True,
                                              null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    operating_profit_margin = models.FloatField(db_column='Operating profit margin', blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    ebitda_margin = models.FloatField(db_column='EBITDA margin', blank=True,
                                      null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'DuPontIndicators'


class EquityLiabilities(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    companyid = models.ForeignKey(Company, models.DO_NOTHING, db_column='CompanyID', blank=True,
                                  null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    share_capital = models.FloatField(db_column='Share capital', blank=True,
                                      null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    called_up_share_capital = models.FloatField(db_column='Called up share capital', blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    treasury_shares = models.FloatField(db_column='Treasury shares', blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    supplementary_capital = models.FloatField(db_column='Supplementary capital', blank=True,
                                              null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    valuation_and_exchange_differences = models.FloatField(db_column='Valuation and exchange differences', blank=True,
                                                           null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    other_capitals = models.FloatField(db_column='Other capitals', blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    retained_earnings_accumulated_losses = models.FloatField(db_column='Retained earnings / accumulated losses',
                                                             blank=True,
                                                             null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_liabilities_from_derivatives = models.FloatField(db_column='Non-current liabilities from derivatives',
                                                                 blank=True,
                                                                 null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_loans_and_borrowings = models.FloatField(db_column='Non-current loans and borrowings', blank=True,
                                                         null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_liabilities_from_bonds = models.FloatField(db_column='Non-current liabilities from bonds', blank=True,
                                                           null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_liabilities_from_finance_leases = models.FloatField(
        db_column='Non-current liabilities from finance leases', blank=True,
        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_trade_payables = models.FloatField(db_column='Non-current trade payables', blank=True,
                                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    long_term_provision_for_employee_benefits = models.FloatField(db_column='Long-term provision for employee benefits',
                                                                  blank=True,
                                                                  null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    deferred_tax_liabilities = models.FloatField(db_column='Deferred tax liabilities', blank=True,
                                                 null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_provision = models.FloatField(db_column='Non-current provision', blank=True,
                                              null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    other_non_current_liabilities = models.FloatField(db_column='Other non-current liabilities', blank=True,
                                                      null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_accruals_liability_field = models.FloatField(db_column='Non-current accruals (liability)', blank=True,
                                                             null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    liabilities_from_derivatives = models.FloatField(db_column='Liabilities from derivatives', blank=True,
                                                     null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    financial_liabilities_loans_and_borrowings_field = models.FloatField(
        db_column='Financial liabilities (loans and borrowings)', blank=True,
        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    bond_liabilities = models.FloatField(db_column='Bond liabilities', blank=True,
                                         null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    liabilities_from_finance_leases = models.FloatField(db_column='Liabilities from finance leases', blank=True,
                                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    trade_payables = models.FloatField(db_column='Trade payables', blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    employee_benefits = models.FloatField(db_column='Employee benefits', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    current_tax_liabilities = models.FloatField(db_column='Current tax liabilities', blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    provisions = models.FloatField(db_column='Provisions', blank=True, null=True)  # Field name made lowercase.
    other_liabilities = models.FloatField(db_column='Other liabilities', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    accruals_liability_field = models.FloatField(db_column='Accruals (liability)', blank=True,
                                                 null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'EquityLiabilities'


class EquityLiabilitiesCategories(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    companyid = models.ForeignKey(Company, models.DO_NOTHING, db_column='CompanyID', blank=True,
                                  null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    equity_shareholders_of_the_parent = models.FloatField(db_column='Equity shareholders of the parent', blank=True,
                                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_controlling_interests = models.FloatField(db_column='Non-controlling interests', blank=True,
                                                  null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    non_current_liabilities = models.FloatField(db_column='Non-current liabilities', blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    current_liabilities = models.FloatField(db_column='Current liabilities', blank=True,
                                            null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    liabilities_related_to_assets_held_for_sale_and_discontinued_operations = models.FloatField(
        db_column='Liabilities related to assets held for sale and discontinued operations', blank=True,
        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'EquityLiabilitiesCategories'


class FinancialRatios(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    companyid = models.ForeignKey(Company, models.DO_NOTHING, db_column='CompanyID', blank=True,
                                  null=True)  # Field name made lowercase.
    periodstart = models.DateField(db_column='PeriodStart', blank=True, null=True)  # Field name made lowercase.
    periodend = models.DateField(db_column='PeriodEnd', blank=True, null=True)  # Field name made lowercase.
    gross_profit_margin_on_sales = models.FloatField(db_column='Gross profit margin on sales', blank=True,
                                                     null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    operating_profit_margin = models.FloatField(db_column='Operating profit margin', blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gross_profit_margin = models.FloatField(db_column='Gross profit margin', blank=True,
                                            null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    net_profit_margin = models.FloatField(db_column='Net profit margin', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    return_on_equity_roe_field = models.FloatField(db_column='Return on equity (ROE)', blank=True,
                                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    return_on_assets_roa_field = models.FloatField(db_column='Return on assets (ROA)', blank=True,
                                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    working_capital_ratio = models.FloatField(db_column='Working capital ratio', blank=True,
                                              null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    current_ratio = models.FloatField(db_column='Current ratio', blank=True,
                                      null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    quick_ratio = models.FloatField(db_column='Quick ratio', blank=True,
                                    null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    cash_ratio = models.FloatField(db_column='Cash ratio', blank=True,
                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    receivables_turnover = models.FloatField(db_column='Receivables turnover', blank=True,
                                             null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    inventory_turnover = models.FloatField(db_column='Inventory turnover', blank=True,
                                           null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    the_operating_cycle = models.FloatField(db_column='The operating cycle', blank=True,
                                            null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    rotation_commitments = models.FloatField(db_column='Rotation commitments', blank=True,
                                             null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    cash_conversion_cycle = models.FloatField(db_column='Cash conversion cycle', blank=True,
                                              null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    rotation_assets = models.FloatField(db_column='Rotation assets', blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    rotation_of_assets = models.FloatField(db_column='Rotation of assets', blank=True,
                                           null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    assets_ratio = models.FloatField(db_column='Assets ratio', blank=True,
                                     null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    debt_ratio = models.FloatField(db_column='Debt ratio', blank=True,
                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    debt_service_ratio = models.FloatField(db_column='Debt service ratio', blank=True,
                                           null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    rate_debt_security = models.FloatField(db_column='Rate debt security', blank=True,
                                           null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'FinancialRatios'


class MarketValues(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    companyid = models.ForeignKey(Company, models.DO_NOTHING, db_column='CompanyID')  # Field name made lowercase.
    periodend = models.DateField(db_column='PeriodEnd')  # Field name made lowercase.
    marketvalue = models.FloatField(db_column='MarketValue')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MarketValues'


class Interval(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    shortcut = models.CharField(db_column='Shortcut', unique=True, blank=True, null=False, max_length=10)  # Field name made lowercase.
    fullname = models.CharField(db_column='FullName', blank=True, null=False, max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Interval'


class StockQuotes(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    companyid = models.ForeignKey(Company, models.DO_NOTHING, db_column='CompanyID')  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate')  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate')  # Field name made lowercase.
    stock = models.FloatField(db_column='Stock')  # Field name made lowercase.
    change = models.FloatField(db_column='Change', blank=True, null=True)  # Field name made lowercase.
    open = models.FloatField(db_column='Open', blank=True, null=True)  # Field name made lowercase.
    high = models.FloatField(db_column='High', blank=True, null=True)  # Field name made lowercase.
    low = models.FloatField(db_column='Low', blank=True, null=True)  # Field name made lowercase.
    volume = models.IntegerField(db_column='Volume', blank=True, null=True)  # Field name made lowercase.
    turnover = models.IntegerField(db_column='Turnover', blank=True, null=True)  # Field name made lowercase.
    interval = models.ForeignKey(Interval, models.DO_NOTHING, db_column='Interval')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'StockQuotes'
