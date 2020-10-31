from bootstrap_modal_forms.generic import BSModalFormView
from django import forms
from django.core.exceptions import ValidationError

from .models import *
from bootstrap_datepicker_plus import DatePickerInput
from bootstrap_modal_forms.forms import BSModalModelForm, BSModalForm


class MergeForm(BSModalForm):
    merge_from = Company.objects.all().order_by('name')
    merge_to = Company.objects.all().order_by('name')
    chosen_from = forms.ModelChoiceField(queryset=merge_from)
    chosen_to = forms.ModelChoiceField(queryset=merge_to)

    def clean(self):
        cleaned_data = super(MergeForm, self).clean()
        if cleaned_data.get('chosen_from') == cleaned_data.get('chosen_to'):
            raise ValidationError("Please, select different companies!")


class CompanyModelForm(BSModalModelForm):
    class Meta:
        model = Company
        fields = ['name', 'isin', 'ticker', 'bloomberg', 'ekd_section_id', 'ekd_class_id']


class AssetsModelForm(BSModalModelForm):
    class Meta:
        model = Assets
        fields = ['company_id', 'date', 'property_plant_and_equipment',
                  'exploration_for_and_evaluation_of_mineral_resources', 'intangible_assets', 'goodwill',
                  'investment_property', 'investment_in_affiliates', 'non_current_financial_assets',
                  'non_current_loans_and_receivables', 'deferred_income_tax',
                  'non_current_deferred_charges_and_accruals', 'non_current_derivative_instruments',
                  'other_non_current_assets', 'inventories', 'current_intangible_assets',
                  'biological_assets', 'trade_receivables', 'loans_and_other_receivables',
                  'financial_assets', 'cash_and_cash_equivalents', 'accruals',
                  'assets_from_current_tax', 'derivative_instruments', 'other_assets']


class AssetsCategoryModelForm(BSModalModelForm):
    class Meta:
        model = AssetsCategories
        fields = ['company_id', 'date', 'non_current_assets', 'current_assets',
                  'assets_held_for_sale_and_discontinuing_operations', 'called_up_capital', 'own_shares']


class DuPointIndicatorModelForm(BSModalModelForm):
    class Meta:
        model = DuPontIndicators
        fields = ['company_id', 'period_start', 'period_end', 'return_on_equity_roe_field',
                  'return_on_assets_roa_field', 'leverage_em_field', 'net_profit_margin',
                  'asset_utilization_au_field', 'load_gross_profit', 'load_operating_profit', 'operating_profit_margin',
                  'ebitda_margin']


class EkdClassModelForm(BSModalModelForm):
    class Meta:
        model = EkdClass
        fields = ['value']


class EkdSectionModelForm(BSModalModelForm):
    class Meta:
        model = EkdSection
        fields = ['value']


class EquityLiabilitiesModelForm(BSModalModelForm):
    class Meta:
        model = EquityLiabilities
        fields = ['company_id', 'date', 'share_capital', 'called_up_share_capital', 'treasury_shares',
                  'supplementary_capital', 'valuation_and_exchange_differences', 'other_capitals',
                  'retained_earnings_accumulated_losses', 'non_current_liabilities_from_derivatives',
                  'non_current_loans_and_borrowings', 'non_current_liabilities_from_bonds',
                  'non_current_liabilities_from_finance_leases', 'non_current_trade_payables',
                  'long_term_provision_for_employee_benefits', 'deferred_tax_liabilities',
                  'non_current_provision', 'other_non_current_liabilities', 'non_current_accruals_liability_field',
                  'liabilities_from_derivatives', 'financial_liabilities_loans_and_borrowings_field',
                  'bond_liabilities', 'liabilities_from_finance_leases', 'trade_payables', 'employee_benefits',
                  'current_tax_liabilities', 'provisions', 'other_liabilities', 'accruals_liability_field']


class EquityLiabilitiesCategoryModelForm(BSModalModelForm):
    class Meta:
        model = EquityLiabilitiesCategories
        fields = ['company_id', 'date', 'equity_shareholders_of_the_parent', 'non_controlling_interests',
                  'non_current_liabilities', 'current_liabilities',
                  'liabilities_related_to_assets_held_for_sale_and_discontinued_operations']


class FinancialRatiosModelForm(BSModalModelForm):
    class Meta:
        model = FinancialRatios
        fields = ['company_id', 'period_start', 'period_end', 'gross_profit_margin_on_sales',
                  'operating_profit_margin', 'gross_profit_margin', 'net_profit_margin',
                  'return_on_equity_roe_field', 'return_on_assets_roa_field', 'working_capital_ratio',
                  'current_ratio', 'quick_ratio', 'cash_ratio', 'receivables_turnover', 'inventory_turnover',
                  'the_operating_cycle', 'rotation_commitments', 'cash_conversion_cycle', 'rotation_assets',
                  'rotation_of_assets', 'assets_ratio', 'debt_ratio', 'debt_service_ratio', 'rate_debt_security']


class MarketValuesModelForm(BSModalModelForm):
    class Meta:
        model = MarketValues
        fields = ['company_id', 'period_end', 'market_value']


class StockQuotesModelForm(BSModalModelForm):
    class Meta:
        model = StockQuotes
        fields = ['company_id', 'date', 'stock', 'change', 'open', 'high', 'low', 'volume', 'turnover',
                  'interval']


class ExportForm(forms.Form):
    file_name = forms.CharField(label='File name:', max_length=100)
    company_choices = Company.objects.all().order_by('name')
    chosen_companies = forms.ModelMultipleChoiceField(queryset=company_choices)
    date_ranges_count = forms.CharField(widget=forms.HiddenInput())
    choices_i = [('d', 'Daily'),
                 ('w', 'Weekly'),
                 ('m', 'Monthly'),
                 ('q', 'Quarterly'),
                 ('y', 'Yearly')]
    choices_i_gpw = choices_i[2:]
    choices_i_gpw.insert(2, ('hy', 'Half-Yearly'))
    choices_i_ratios = choices_i[3:]
    choices_i_balance = choices_i_gpw[1:]

    chosen_interval_balance = forms.ChoiceField(choices=choices_i_balance, initial='q', widget=forms.RadioSelect, required=False)
    chosen_interval_ratios = forms.ChoiceField(choices=choices_i_ratios, initial='q', widget=forms.RadioSelect, required=False)
    chosen_interval_stooq = forms.ChoiceField(choices=choices_i, initial='d', widget=forms.RadioSelect, required=False)
    chosen_interval_gpw = forms.ChoiceField(choices=choices_i_gpw, initial=choices_i_gpw[0], widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        date_ranges = kwargs.pop('count', 0)

        super(ExportForm, self).__init__(*args, **kwargs)
        self.fields['date_ranges_count'].initial = date_ranges

        for index in range(int(date_ranges) + 1):
            self.fields['start_date_{index}'.format(index=index)] = forms.DateField(label='To: ',
                                                                                    widget=DatePickerInput(
                                                                                        format='%d/%m/%Y',
                                                                                        attrs={'type': 'date',
                                                                                               'class': 'datepicker'}
                                                                                    ))
            self.fields['end_date_{index}'.format(index=index)] = forms.DateField(label='To: ',
                                                                                  widget=DatePickerInput(
                                                                                      format='%d/%m/%Y',
                                                                                      attrs={'type': 'date',
                                                                                             'class': 'datepicker'}
                                                                                  ))


class ExportDatabaseForm(forms.Form):
    folder = forms.CharField(label='Folder name:', max_length=100, required=True)
    delete = forms.BooleanField(required=False)

    folder_sheet = 'Folder where database file will be saved'
    delete_sheet = 'Delete all data from database after export'


class ImportDatabaseForm(forms.Form):
    file = forms.CharField(label='File name:', max_length=100, required=True)

    file_sheet = 'File with database to be imported'


class NotoriaImportForm(forms.Form):
    file_path = forms.CharField(label='Path to files:', max_length=100)
    choices_bs = [('YS', 'Yearly'),
                  ('QS', 'Quarterly')]
    choices_fr = [('YS', 'Yearly'),
                  ('QS', 'Quarterly')]
    choices_dp = [('YS', 'Yearly'),
                  ('QS', 'Quarterly')]

    chosen_sheets_bs = forms.MultipleChoiceField(choices=choices_bs, widget=forms.CheckboxSelectMultiple,
                                                 required=False)
    chosen_sheets_fr = forms.MultipleChoiceField(choices=choices_fr, widget=forms.CheckboxSelectMultiple,
                                                 required=False)
    chosen_sheets_dp = forms.MultipleChoiceField(choices=choices_dp, widget=forms.CheckboxSelectMultiple,
                                                 required=False)

    bs_sheet = 'Balance sheet'
    fr_sheet = 'Financial ratios'
    dp_sheet = 'DuPont Indicators'


class StooqImportForm(forms.Form):
    ticker = forms.CharField(label='Ticker of the company', max_length=20, required=False)
    company_choices = Company.objects.filter(ticker__isnull=False)
    company = forms.ModelChoiceField(queryset=company_choices, required=False)
    date_from = forms.DateTimeField(required=False, widget=DatePickerInput(format='%d.%m.%Y',
                                                                            attrs={'type': 'date',
                                                                                    'class': 'datepicker'}
                                                                            ))
    date_to = forms.DateTimeField(required=False, widget=DatePickerInput(
                                                                        format='%d.%m.%Y',
                                                                        attrs={'type': 'date',
                                                                                'class': 'datepicker'}
                                                                        ))

    choices_interval = [('d', 'Daily'),
                        ('w', 'Weekly'),
                        ('m', 'Monthly'),
                        ('q', 'Quarterly'),
                        ('y', 'Yearly')]

    interval = forms.ChoiceField(choices=choices_interval, initial='d', widget=forms.RadioSelect, required=True)

    ticker_sheet = 'Ticker'
    company_sheet = 'Company'
    date_from_sheet = 'From'
    date_to_sheet = 'To'
    interval_sheet = 'Interval'

    date_sheet = 'Date'
    date = forms.DateTimeField(required=False, widget=DatePickerInput(
                                                                    format='%d.%m.%Y',
                                                                    attrs={'type': 'date',
                                                                            'class': 'datepicker'}
                                                                    ))


class GpwImportForm(forms.Form):
    choices = [('yearbook_excel', 'GPW Yearbook Excel'),
               ('yearbook_pdf', 'GPW Yearbook PDF'),
               ('statistics_excel', 'GPW Statistic Bulletin Excel'),
               ('statistics_pdf', 'GPW Statistic Bulletin PDF')]

    file_type = forms.ChoiceField(label='Type of file', choices=choices, widget=forms.RadioSelect)
    path = forms.CharField(label='Path to file')
