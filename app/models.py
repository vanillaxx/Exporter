from django.db import models

# Create your models here.


class Assets(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    company_id = models.ForeignKey('Company', models.CASCADE, db_column='CompanyID', blank=True,
                                  null=False)  
    date = models.DateField(db_column='Date', blank=True, null=True)  
    property_plant_and_equipment = models.FloatField(db_column='Property, plant and equipment', blank=True,
                                                     null=True)  
    exploration_for_and_evaluation_of_mineral_resources = models.FloatField(
        db_column='Exploration for and evaluation of mineral resources', blank=True,
        null=True)  
    intangible_assets = models.FloatField(db_column='Intangible assets', blank=True,
                                          null=True)  
    goodwill = models.FloatField(db_column='Goodwill', blank=True, null=True)  
    investment_property = models.FloatField(db_column='Investment property', blank=True,
                                            null=True)  
    investment_in_affiliates = models.FloatField(db_column='Investment in affiliates', blank=True,
                                                 null=True)  
    non_current_financial_assets = models.FloatField(db_column='Non-current financial assets', blank=True,
                                                     null=True)  
    non_current_loans_and_receivables = models.FloatField(db_column='Non-current loans and receivables', blank=True,
                                                          null=True)  
    deferred_income_tax = models.FloatField(db_column='Deferred income tax', blank=True,
                                            null=True)  
    non_current_deferred_charges_and_accruals = models.FloatField(db_column='Non-current deferred charges and accruals',
                                                                  blank=True,
                                                                  null=True)  
    non_current_derivative_instruments = models.FloatField(db_column='Non-current derivative instruments', blank=True,
                                                           null=True)  
    other_non_current_assets = models.FloatField(db_column='Other non-current assets', blank=True,
                                                 null=True)  
    inventories = models.FloatField(db_column='Inventories', blank=True, null=True)  
    current_intangible_assets = models.FloatField(db_column='Current intangible assets', blank=True,
                                                  null=True)  
    biological_assets = models.FloatField(db_column='Biological assets', blank=True,
                                          null=True)  
    trade_receivables = models.FloatField(db_column='Trade receivables', blank=True,
                                          null=True)  
    loans_and_other_receivables = models.FloatField(db_column='Loans and other receivables', blank=True,
                                                    null=True)  
    financial_assets = models.FloatField(db_column='Financial assets', blank=True,
                                         null=True)  
    cash_and_cash_equivalents = models.FloatField(db_column='Cash and cash equivalents', blank=True,
                                                  null=True)  
    accruals = models.FloatField(db_column='Accruals', blank=True, null=True)  
    assets_from_current_tax = models.FloatField(db_column='Assets from current tax', blank=True,
                                                null=True)  
    derivative_instruments = models.FloatField(db_column='Derivative instruments', blank=True,
                                               null=True)  
    other_assets = models.FloatField(db_column='Other assets', blank=True,
                                     null=True)  

    class Meta:
        managed = True
        db_table = 'Assets'
        constraints = [
            models.UniqueConstraint(fields=['company_id', 'date'], name='assets_company_date_unique')
        ]


class AssetsCategories(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    company_id = models.ForeignKey('Company', models.CASCADE, db_column='CompanyID', blank=True,
                                  null=False)  
    date = models.DateField(db_column='Date', blank=True, null=True)  
    non_current_assets = models.FloatField(db_column='Non-current assets', blank=True,
                                           null=True)  
    current_assets = models.FloatField(db_column='Current assets', blank=True,
                                       null=True)  
    assets_held_for_sale_and_discontinuing_operations = models.FloatField(
        db_column='Assets held for sale and discontinuing operations', blank=True,
        null=True)  
    called_up_capital = models.FloatField(db_column='Called up capital', blank=True,
                                          null=True)  
    own_shares = models.FloatField(db_column='Own shares', blank=True,
                                   null=True)  

    class Meta:
        managed = True
        db_table = 'AssetsCategories'
        constraints = [
            models.UniqueConstraint(fields=['company_id', 'date'], name='assets_categories_company_date_unique')
        ]


class EkdClass(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    value = models.IntegerField(db_column='Value', unique=True, blank=True, null=True)  

    def __str__(self):
        return str(self.value)

    class Meta:
        managed = True
        db_table = 'EKDClass'
        constraints = [
            models.UniqueConstraint(fields=['value'], name='ekd_class_value_unique')
        ]


class EkdSection(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    value = models.IntegerField(db_column='Value', unique=True, blank=True, null=True)  

    def __str__(self):
        return str(self.value)

    class Meta:
        managed = True
        db_table = 'EKDSection'
        constraints = [
            models.UniqueConstraint(fields=['value'], name='ekd_section_value_unique')
        ]


class Company(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    name = models.CharField(db_column='Name', blank=True, null=True, max_length=255)  
    isin = models.CharField(db_column='ISIN', unique=True, blank=True, null=True,
                            max_length=255)  
    ticker = models.CharField(db_column='Ticker', unique=True, blank=True, null=True,
                              max_length=255)  
    bloomberg = models.CharField(db_column='Bloomberg', blank=True, null=True,
                                 max_length=255)  
    ekd_section_id = models.ForeignKey('EkdSection', models.SET_NULL, db_column='EKDSectionID', blank=True,
                                      null=True)  
    ekd_class_id = models.ForeignKey('EkdClass', models.SET_NULL, db_column='EKDClassID', blank=True,
                                    null=True)  

    def __str__(self):
        if self.name:
            return self.name
        if self.ticker:
            return "Ticker: " + self.ticker
        if self.isin:
            return "ISIN: " + self.isin
        return ''

    class Meta:
        managed = True
        db_table = 'Company'
        constraints = [
            models.UniqueConstraint(fields=['name', 'isin', 'ticker'], name='company_identification_unique')
        ]


class DuPontIndicators(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    company_id = models.ForeignKey(Company, models.CASCADE, db_column='CompanyID', blank=True,
                                  null=False)  
    period_start = models.DateField(db_column='Period start', blank=True, null=True)  
    period_end = models.DateField(db_column='Period end', blank=True, null=True)  
    return_on_equity_roe_field = models.FloatField(db_column='Return on equity (ROE)', blank=True,
                                                   null=True)   
    return_on_assets_roa_field = models.FloatField(db_column='Return on assets (ROA)', blank=True,
                                                   null=True)   
    leverage_em_field = models.FloatField(db_column='Leverage (EM)', blank=True,
                                          null=True)   
    net_profit_margin = models.FloatField(db_column='Net profit margin', blank=True,
                                          null=True)  
    asset_utilization_au_field = models.FloatField(db_column='Asset utilization (AU)', blank=True,
                                                   null=True)   
    load_gross_profit = models.FloatField(db_column='Load gross profit', blank=True,
                                          null=True)  
    load_operating_profit = models.FloatField(db_column='Load operating profit', blank=True,
                                              null=True)  
    operating_profit_margin = models.FloatField(db_column='Operating profit margin', blank=True,
                                                null=True)  
    ebitda_margin = models.FloatField(db_column='EBITDA margin', blank=True,
                                      null=True)  

    class Meta:
        managed = True
        db_table = 'DuPontIndicators'
        constraints = [
            models.UniqueConstraint(fields=['period_start', 'period_end', 'company_id'], name='dupont_indicators_company_date_unique')
        ]


class EquityLiabilities(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    company_id = models.ForeignKey(Company, models.CASCADE, db_column='CompanyID', blank=True,
                                  null=False)  
    date = models.DateField(db_column='Date', blank=True, null=True)  
    share_capital = models.FloatField(db_column='Share capital', blank=True,
                                      null=True)  
    called_up_share_capital = models.FloatField(db_column='Called up share capital', blank=True,
                                                null=True)  
    treasury_shares = models.FloatField(db_column='Treasury shares', blank=True,
                                        null=True)  
    supplementary_capital = models.FloatField(db_column='Supplementary capital', blank=True,
                                              null=True)  
    valuation_and_exchange_differences = models.FloatField(db_column='Valuation and exchange differences', blank=True,
                                                           null=True)  
    other_capitals = models.FloatField(db_column='Other capitals', blank=True,
                                       null=True)  
    retained_earnings_accumulated_losses = models.FloatField(db_column='Retained earnings / accumulated losses',
                                                             blank=True,
                                                             null=True)  
    non_current_liabilities_from_derivatives = models.FloatField(db_column='Non-current liabilities from derivatives',
                                                                 blank=True,
                                                                 null=True)  
    non_current_loans_and_borrowings = models.FloatField(db_column='Non-current loans and borrowings', blank=True,
                                                         null=True)  
    non_current_liabilities_from_bonds = models.FloatField(db_column='Non-current liabilities from bonds', blank=True,
                                                           null=True)  
    non_current_liabilities_from_finance_leases = models.FloatField(
        db_column='Non-current liabilities from finance leases', blank=True,
        null=True)  
    non_current_trade_payables = models.FloatField(db_column='Non-current trade payables', blank=True,
                                                   null=True)  
    long_term_provision_for_employee_benefits = models.FloatField(db_column='Long-term provision for employee benefits',
                                                                  blank=True,
                                                                  null=True)  
    deferred_tax_liabilities = models.FloatField(db_column='Deferred tax liabilities', blank=True,
                                                 null=True)  
    non_current_provision = models.FloatField(db_column='Non-current provision', blank=True,
                                              null=True)  
    other_non_current_liabilities = models.FloatField(db_column='Other non-current liabilities', blank=True,
                                                      null=True)  
    non_current_accruals_liability_field = models.FloatField(db_column='Non-current accruals (liability)', blank=True,
                                                             null=True)   
    liabilities_from_derivatives = models.FloatField(db_column='Liabilities from derivatives', blank=True,
                                                     null=True)  
    financial_liabilities_loans_and_borrowings_field = models.FloatField(
        db_column='Financial liabilities (loans and borrowings)', blank=True,
        null=True)   
    bond_liabilities = models.FloatField(db_column='Bond liabilities', blank=True,
                                         null=True)  
    liabilities_from_finance_leases = models.FloatField(db_column='Liabilities from finance leases', blank=True,
                                                        null=True)  
    trade_payables = models.FloatField(db_column='Trade payables', blank=True,
                                       null=True)  
    employee_benefits = models.FloatField(db_column='Employee benefits', blank=True,
                                          null=True)  
    current_tax_liabilities = models.FloatField(db_column='Current tax liabilities', blank=True,
                                                null=True)  
    provisions = models.FloatField(db_column='Provisions', blank=True, null=True)  
    other_liabilities = models.FloatField(db_column='Other liabilities', blank=True,
                                          null=True)  
    accruals_liability_field = models.FloatField(db_column='Accruals (liability)', blank=True,
                                                 null=True)   

    class Meta:
        managed = True
        db_table = 'EquityLiabilities'
        constraints = [
            models.UniqueConstraint(fields=['date', 'company_id'], name='equity_liabilities_company_date_unique')
        ]


class EquityLiabilitiesCategories(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    company_id = models.ForeignKey(Company, models.CASCADE, db_column='CompanyID', blank=True,
                                  null=False)  
    date = models.DateField(db_column='Date', blank=True, null=True)  
    equity_shareholders_of_the_parent = models.FloatField(db_column='Equity shareholders of the parent', blank=True,
                                                          null=True)  
    non_controlling_interests = models.FloatField(db_column='Non-controlling interests', blank=True,
                                                  null=True)  
    non_current_liabilities = models.FloatField(db_column='Non-current liabilities', blank=True,
                                                null=True)  
    current_liabilities = models.FloatField(db_column='Current liabilities', blank=True,
                                            null=True)  
    liabilities_related_to_assets_held_for_sale_and_discontinued_operations = models.FloatField(
        db_column='Liabilities related to assets held for sale and discontinued operations', blank=True,
        null=True)  

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['company_id', 'date'],
                                    name='equity_liabilities_categories_company_date_unique')
        ]
        managed = True
        db_table = 'EquityLiabilitiesCategories'


class FinancialRatios(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    company_id = models.ForeignKey(Company, models.CASCADE, db_column='CompanyID', blank=True,
                                  null=False)  
    period_start = models.DateField(db_column='Period start', blank=True, null=True)  
    period_end = models.DateField(db_column='Period end', blank=True, null=True)  
    gross_profit_margin_on_sales = models.FloatField(db_column='Gross profit margin on sales', blank=True,
                                                     null=True)  
    operating_profit_margin = models.FloatField(db_column='Operating profit margin', blank=True,
                                                null=True)  
    gross_profit_margin = models.FloatField(db_column='Gross profit margin', blank=True,
                                            null=True)  
    net_profit_margin = models.FloatField(db_column='Net profit margin', blank=True,
                                          null=True)  
    return_on_equity_roe_field = models.FloatField(db_column='Return on equity (ROE)', blank=True,
                                                   null=True) 
    return_on_assets_roa_field = models.FloatField(db_column='Return on assets (ROA)', blank=True,
                                                   null=True) 
    working_capital_ratio = models.FloatField(db_column='Working capital ratio', blank=True,
                                              null=True)  
    current_ratio = models.FloatField(db_column='Current ratio', blank=True,
                                      null=True)  
    quick_ratio = models.FloatField(db_column='Quick ratio', blank=True,
                                    null=True)  
    cash_ratio = models.FloatField(db_column='Cash ratio', blank=True,
                                   null=True)  
    receivables_turnover = models.FloatField(db_column='Receivables turnover', blank=True,
                                             null=True)  
    inventory_turnover = models.FloatField(db_column='Inventory turnover', blank=True,
                                           null=True)  
    the_operating_cycle = models.FloatField(db_column='The operating cycle', blank=True,
                                            null=True)  
    rotation_commitments = models.FloatField(db_column='Rotation commitments', blank=True,
                                             null=True)  
    cash_conversion_cycle = models.FloatField(db_column='Cash conversion cycle', blank=True,
                                              null=True)  
    rotation_assets = models.FloatField(db_column='Rotation assets', blank=True,
                                        null=True)  
    rotation_of_assets = models.FloatField(db_column='Rotation of assets', blank=True,
                                           null=True)  
    assets_ratio = models.FloatField(db_column='Assets ratio', blank=True,
                                     null=True)  
    debt_ratio = models.FloatField(db_column='Debt ratio', blank=True,
                                   null=True)  
    debt_service_ratio = models.FloatField(db_column='Debt service ratio', blank=True,
                                           null=True)  
    rate_debt_security = models.FloatField(db_column='Rate debt security', blank=True,
                                           null=True)  

    class Meta:
        managed = True
        db_table = 'FinancialRatios'
        constraints = [
            models.UniqueConstraint(fields=['period_start', 'period_end', 'company_id'], name='financial_ratios_company_date_unique')
        ]


class MarketValues(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    company_id = models.ForeignKey(Company, models.CASCADE, db_column='CompanyID', null=False)  
    period_end = models.DateField(db_column='Period end')  
    market_value = models.FloatField(db_column='Market value')

    class Meta:
        managed = True
        db_table = 'MarketValues'
        constraints = [
            models.UniqueConstraint(fields=['company_id', 'period_end'], name='market_values_company_date_unique')
        ]


class Interval(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    shortcut = models.CharField(db_column='Shortcut', unique=True, blank=True, null=False, max_length=10)  
    fullname = models.CharField(db_column='FullName', blank=True, null=False, max_length=255)  

    def __str__(self):
        return self.fullname

    class Meta:
        managed = True
        db_table = 'Interval'
        constraints = [
            models.UniqueConstraint(fields=['shortcut'], name='interval_shortcut_unique')
        ]


class StockQuotes(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True, blank=True, null=False)  
    company_id = models.ForeignKey(Company, models.CASCADE, db_column='CompanyID', null=False)  
    date = models.DateField(db_column='Date')
    stock = models.FloatField(db_column='Stock')  
    change = models.FloatField(db_column='Change', blank=True, null=True)  
    open = models.FloatField(db_column='Open', blank=True, null=True)  
    high = models.FloatField(db_column='High', blank=True, null=True)  
    low = models.FloatField(db_column='Low', blank=True, null=True)  
    volume = models.IntegerField(db_column='Volume', blank=True, null=True)  
    turnover = models.IntegerField(db_column='Turnover', blank=True, null=True)  
    interval = models.ForeignKey(Interval, models.DO_NOTHING, db_column='Interval')  

    class Meta:
        managed = True
        db_table = 'StockQuotes'

        constraints = [
            models.UniqueConstraint(fields=['company_id', 'date', 'interval'], name='stock_company_date_interval_unique')
        ]