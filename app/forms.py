from django import forms
from .models import *


class NotoriaExportForm(forms.Form):
    file_name = forms.CharField(label='File name:', max_length=100)
    notoria_choices = [('-da', 'Detailed assets'),
                       ('-ca', 'Assets categories'),
                       ('-fa', 'Full assets'),
                       ('-de', 'Detailed equity and liabilities'),
                       ('-ce', 'Equity and liabilities categories'),
                       ('-fe', 'Full equity and liabilities'),
                       ]
    company_choices = Company.objects.all()
    chosen_data = forms.ChoiceField(choices=notoria_choices)
    chosen_companies = forms.ModelMultipleChoiceField(queryset=company_choices)


class NotoriaImportForm(forms.Form):
    file_path = forms.CharField(label='Path to files:', max_length=100)
    choices_bs = [('yearly_bs', 'Yearly'),
                  ('quarterly_bs', 'Quarterly')]
    choices_fr = [('yearly_fr', 'Yearly'),
                  ('quarterly_fr', 'Quarterly')]
    choices_dp = [('yearly_bs', 'Yearly'),
                  ('quarterly_dp', 'Quarterly')]

    chosen_sheets_bs = forms.ChoiceField(choices=choices_bs, widget=forms.CheckboxSelectMultiple)
    chosen_sheets_fr = forms.ChoiceField(choices=choices_fr, widget=forms.CheckboxSelectMultiple)
    chosen_sheets_dp = forms.ChoiceField(choices=choices_dp, widget=forms.CheckboxSelectMultiple)

    bs_sheet = 'Balance sheet'
    fr_sheet = 'Financial ratios'
    dp_sheet = 'DuPont Indicators'


class StooqOneCompanyImportForm(forms.Form):
    file_path = forms.CharField(label='Path to files:', max_length=100)
    choices_bs = [('yearly_bs', 'Yearly'),
                  ('quarterly_bs', 'Quarterly')]
    choices_fr = [('yearly_fr', 'Yearly'),
                  ('quarterly_fr', 'Quarterly')]
    choices_dp = [('yearly_bs', 'Yearly'),
                  ('quarterly_dp', 'Quarterly')]

    chosen_sheets_bs = forms.ChoiceField(choices=choices_bs, widget=forms.CheckboxSelectMultiple)
    chosen_sheets_fr = forms.ChoiceField(choices=choices_fr, widget=forms.CheckboxSelectMultiple)
    chosen_sheets_dp = forms.ChoiceField(choices=choices_dp, widget=forms.CheckboxSelectMultiple)

    bs_sheet = 'Balance sheet'
    fr_sheet = 'Financial ratios'
    dp_sheet = 'DuPont Indicators'


class StooqAllCompaniesImportForm(forms.Form):
    file_path = forms.CharField(label='Path to files:', max_length=100)
    choices_bs = [('yearly_bs', 'Yearly'),
                  ('quarterly_bs', 'Quarterly')]
    choices_fr = [('yearly_fr', 'Yearly'),
                  ('quarterly_fr', 'Quarterly')]
    choices_dp = [('yearly_bs', 'Yearly'),
                  ('quarterly_dp', 'Quarterly')]

    chosen_sheets_bs = forms.ChoiceField(choices=choices_bs, widget=forms.CheckboxSelectMultiple)
    chosen_sheets_fr = forms.ChoiceField(choices=choices_fr, widget=forms.CheckboxSelectMultiple)
    chosen_sheets_dp = forms.ChoiceField(choices=choices_dp, widget=forms.CheckboxSelectMultiple)

    bs_sheet = 'Balance sheet'
    fr_sheet = 'Financial ratios'
    dp_sheet = 'DuPont Indicators'


class GpwImportForm(forms.Form):
    choices = [('yearbook_excel', 'GPW Yearbook Excel'),
               ('yearbook_pdf', 'GPW Yearbook PDF'),
               ('statistics_excel', 'GPW Statistic Bulletin Excel'),
               ('statistics_pdf', 'GPW Statistic Bulletin PDF')]

    file_type = forms.ChoiceField(label='Type of file', choices=choices, widget=forms.RadioSelect)
    path = forms.CharField(label='Path to file')
