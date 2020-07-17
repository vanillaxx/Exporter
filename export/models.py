from django.db import models
from django import forms
from common.DAL.db_queries import get_all_companies

class EKD_Class(models.Model):
    Value = models.IntegerField()

    def __str__(self):
        return self.Value


class EKD_Section(models.Model):
    Value = models.IntegerField()

    def __str__(self):
        return self.Value


class Company(models.Model):
    Name = models.CharField(max_length=255)
    ISIN = models.CharField(max_length=255)
    Ticker = models.CharField(max_length=255)
    Bloomberg = models.CharField(max_length=255)
    EKD_SectionID = models.ForeignKey(EKD_Section, on_delete=models.PROTECT)
    EKD_ClassID = models.ForeignKey(EKD_Class, on_delete=models.PROTECT)

    def __str__(self):
        return self.Name


class NotoriaExportForm(forms.Form):
    file_name = forms.CharField(label='File name:', max_length=100)
    notoria_choices = [('-da', 'Detailed assets'),
               ('-ca', 'Assets categories'),
               ('-fa', 'Full assets'),
               ('-de', 'Detailed equity and liabilities'),
               ('-ce', 'Equity and liabilities categories'),
               ('-fe', 'Full equity and liabilities'),
               ]
    company_choices = get_all_companies()
    chosen_data = forms.ChoiceField(choices=notoria_choices)
    chosen_companies = forms.ChoiceField(choices=company_choices)


class Assets(models.Model):
    CompanyID = models.ForeignKey(Company, on_delete=models.PROTECT)
    Date = models.DateField()
    Property_plant_and_equipment = models.DecimalField(decimal_places=4, max_digits=15,
                                                       db_column='Property, plant and equipment')
    Exploration_for_and_evaluation_of_mineral_resources = models.DecimalField(decimal_places=4, max_digits=15,
                                                                              db_column='Exploration for and evaluation of mineral resources')
    Intangible_assets = models.DecimalField(decimal_places=4, max_digits=15, db_column='Intangible assets')
    Goodwill = models.DecimalField(decimal_places=4, max_digits=15, db_column='Goodwill')
    Investment_property = models.DecimalField(decimal_places=4, max_digits=15, db_column='Investment property')
    Investment_in_affiliates = models.DecimalField(decimal_places=4, max_digits=15,
                                                   db_column='Investment in affiliates')
    Non_current_financial_assets = models.DecimalField(decimal_places=4, max_digits=15,
                                                       db_column='Non-current financial assets')
    Non_current_loans_and_receivables = models.DecimalField(decimal_places=4, max_digits=15,
                                                            db_column='Non-current loans and receivables')
    Deferred_income_tax = models.DecimalField(decimal_places=4, max_digits=15, db_column='Deferred income tax')
    Non_current_deferred_charges_and_accruals = models.DecimalField(decimal_places=4, max_digits=15,
                                                                    db_column='Non-current deferred charges and accruals')
    Non_current_derivative_instruments = models.DecimalField(decimal_places=4, max_digits=15,
                                                             db_column='Non-current derivative instruments')
    Other_non_current_assets = models.DecimalField(decimal_places=4, max_digits=15,
                                                   db_column='Other non-current assets')
    Inventories = models.DecimalField(decimal_places=4, max_digits=15, db_column='Inventories')
    Current_intangible_assets = models.DecimalField(decimal_places=4, max_digits=15,
                                                    db_column='Current intangible assets')
    Biological_assets = models.DecimalField(decimal_places=4, max_digits=15, db_column='Biological assets')
    Trade_receivables = models.DecimalField(decimal_places=4, max_digits=15, db_column='Trade receivables')
    Loans_and_other_receivables = models.DecimalField(decimal_places=4, max_digits=15,
                                                      db_column='Loans and other receivables')
    Financial_assets = models.DecimalField(decimal_places=4, max_digits=15, db_column='Financial assets')
    Cash_and_cash_equivalents = models.DecimalField(decimal_places=4, max_digits=15,
                                                    db_column='Cash and cash equivalents')
    Accruals = models.DecimalField(decimal_places=4, max_digits=15, db_column='Accruals')
    Assets_from_current_tax = models.DecimalField(decimal_places=4, max_digits=15, db_column='Assets from current tax')
    Derivative_instruments = models.DecimalField(decimal_places=4, max_digits=15, db_column='Derivative instruments')
    Other_assets = models.DecimalField(decimal_places=4, max_digits=15, db_column='Other assets')

    def __str__(self):
        return self.CompanyID + " " + self.Date
