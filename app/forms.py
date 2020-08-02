from django import forms
from .models import *
from bootstrap_datepicker_plus import DatePickerInput
from bootstrap_daterangepicker import widgets, fields


class NotoriaExportForm(forms.Form):
    file_name = forms.CharField(label='File name:', max_length=100)
    notoria_choices = [('-da', 'Detailed assets'),
                       ('-ca', 'Assets categories'),
                       ('-fa', 'Full assets'),
                       ('-de', 'Detailed equity and liabilities'),
                       ('-ce', 'Equity and liabilities categories'),
                       ('-fe', 'Full equity and liabilities'),
                       ('-f', 'Financial ratios'),
                       ('-d', 'DuPont Indicators')
                       ]
    company_choices = Company.objects.all()
    chosen_data = forms.ChoiceField(choices=notoria_choices)
    chosen_companies = forms.ModelMultipleChoiceField(queryset=company_choices)
    start_date = forms.DateField(label='From:',
                                 widget=DatePickerInput(
                                     format='%d/%m/%Y', attrs={'type': 'date'}
                                 ))

    end_date = forms.DateField(label='To: ',
                               widget=DatePickerInput(
                                   format='%d/%m/%Y', attrs={'type': 'date'}
                               ))
    date_ranges_count = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        date_ranges = kwargs.pop('count', 0)

        super(NotoriaExportForm, self).__init__(*args, **kwargs)
        self.fields['date_ranges_count'].initial = date_ranges

        for index in range(int(date_ranges)):
            if index != 0:
                self.fields['start_date_{index}'.format(index=index)] = forms.DateField()
                self.fields['end_date_{index}'.format(index=index)] = forms.DateField()


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
    gpw_sheet = 'GPW Capitalization'

    period_end = forms.DateField()


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
