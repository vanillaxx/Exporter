# Generated by Django 3.0.8 on 2020-07-16 21:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EKD_Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Value', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EKD_Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Value', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('ISIN', models.CharField(max_length=255)),
                ('Ticker', models.CharField(max_length=255)),
                ('Bloomberg', models.CharField(max_length=255)),
                ('EKD_ClassID', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='export.EKD_Class')),
                ('EKD_SectionID', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='export.EKD_Section')),
            ],
        ),
        migrations.CreateModel(
            name='Assets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField()),
                ('Property_plant_and_equipment', models.DecimalField(db_column='Property, plant and equipment', decimal_places=4, max_digits=15)),
                ('Exploration_for_and_evaluation_of_mineral_resources', models.DecimalField(db_column='Exploration for and evaluation of mineral resources', decimal_places=4, max_digits=15)),
                ('Intangible_assets', models.DecimalField(db_column='Intangible assets', decimal_places=4, max_digits=15)),
                ('Goodwill', models.DecimalField(db_column='Goodwill', decimal_places=4, max_digits=15)),
                ('Investment_property', models.DecimalField(db_column='Investment property', decimal_places=4, max_digits=15)),
                ('Investment_in_affiliates', models.DecimalField(db_column='Investment in affiliates', decimal_places=4, max_digits=15)),
                ('Non_current_financial_assets', models.DecimalField(db_column='Non-current financial assets', decimal_places=4, max_digits=15)),
                ('Non_current_loans_and_receivables', models.DecimalField(db_column='Non-current loans and receivables', decimal_places=4, max_digits=15)),
                ('Deferred_income_tax', models.DecimalField(db_column='Deferred income tax', decimal_places=4, max_digits=15)),
                ('Non_current_deferred_charges_and_accruals', models.DecimalField(db_column='Non-current deferred charges and accruals', decimal_places=4, max_digits=15)),
                ('Non_current_derivative_instruments', models.DecimalField(db_column='Non-current derivative instruments', decimal_places=4, max_digits=15)),
                ('Other_non_current_assets', models.DecimalField(db_column='Other non-current assets', decimal_places=4, max_digits=15)),
                ('Inventories', models.DecimalField(db_column='Inventories', decimal_places=4, max_digits=15)),
                ('Current_intangible_assets', models.DecimalField(db_column='Current intangible assets', decimal_places=4, max_digits=15)),
                ('Biological_assets', models.DecimalField(db_column='Biological assets', decimal_places=4, max_digits=15)),
                ('Trade_receivables', models.DecimalField(db_column='Trade receivables', decimal_places=4, max_digits=15)),
                ('Loans_and_other_receivables', models.DecimalField(db_column='Loans and other receivables', decimal_places=4, max_digits=15)),
                ('Financial_assets', models.DecimalField(db_column='Financial assets', decimal_places=4, max_digits=15)),
                ('Cash_and_cash_equivalents', models.DecimalField(db_column='Cash and cash equivalents', decimal_places=4, max_digits=15)),
                ('Accruals', models.DecimalField(db_column='Accruals', decimal_places=4, max_digits=15)),
                ('Assets_from_current_tax', models.DecimalField(db_column='Assets from current tax', decimal_places=4, max_digits=15)),
                ('Derivative_instruments', models.DecimalField(db_column='Derivative instruments', decimal_places=4, max_digits=15)),
                ('Other_assets', models.DecimalField(db_column='Other assets', decimal_places=4, max_digits=15)),
                ('CompanyID', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='export.Company')),
            ],
        ),
    ]
