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
    # start_date = forms.DateField(label='From:',
    #                              widget=DatePickerInput(
    #                                  format='%d/%m/%Y', attrs={'type': 'date'}
    #                              ))
    #
    # end_date = forms.DateField(label='To: ',
    #                            widget=DatePickerInput(
    #                                format='%d/%m/%Y', attrs={'type': 'date'}
    #                            ))
    date_ranges_count = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        date_ranges = kwargs.pop('count', 0)

        super(NotoriaExportForm, self).__init__(*args, **kwargs)
        self.fields['date_ranges_count'].initial = date_ranges

        for index in range(int(date_ranges) + 1):
            print(index)
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
            # if index != 0:
            # self.fields['start_date_{index}'.format(index=index)] = forms.DateField()
            # self.fields['end_date_{index}'.format(index=index)] = forms.DateField()


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


class StooqImportForm(forms.Form):
    ticker = forms.CharField(label='Ticker of the company', max_length=20, required=False)
    company_choices = Company.objects.all()
    company = forms.ModelChoiceField(queryset=company_choices, required=False)
    date_from = forms.DateTimeField(input_formats=['%d.%m.%Y'], required=False)
    date_to = forms.DateTimeField(input_formats=['%d.%m.%Y'], required=False)

    choices_interval = [('d', 'Daily'),
                        ('w', 'Weekly'),
                        ('m', 'Monthly'),
                        ('q', 'Quarterly'),
                        ('y', 'Yearly')]

    interval = forms.ChoiceField(choices=choices_interval, widget=forms.RadioSelect, required=False)

    ticker_sheet = 'Ticker'
    company_sheet = 'Company'
    date_from_sheet = 'From'
    date_to_sheet = 'To'
    interval_sheet = 'Interval'

    date_sheet = 'Date'
    date = forms.DateTimeField(input_formats=['%d.%m.%Y'], required=False)


class GpwImportForm(forms.Form):
    choices = [('yearbook_excel', 'GPW Yearbook Excel'),
               ('yearbook_pdf', 'GPW Yearbook PDF'),
               ('statistics_excel', 'GPW Statistic Bulletin Excel'),
               ('statistics_pdf', 'GPW Statistic Bulletin PDF')]

    file_type = forms.ChoiceField(label='Type of file', choices=choices, widget=forms.RadioSelect)
    path = forms.CharField(label='Path to file')
