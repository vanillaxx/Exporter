from django.db import models

# Create your models here.


from django import forms


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
