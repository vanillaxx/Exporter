# Generated by Django 3.0.8 on 2020-10-28 19:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assets',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('date', models.DateField(blank=True, db_column='Date', null=True)),
                ('property_plant_and_equipment', models.FloatField(blank=True, db_column='Property, plant and equipment', null=True)),
                ('exploration_for_and_evaluation_of_mineral_resources', models.FloatField(blank=True, db_column='Exploration for and evaluation of mineral resources', null=True)),
                ('intangible_assets', models.FloatField(blank=True, db_column='Intangible assets', null=True)),
                ('goodwill', models.FloatField(blank=True, db_column='Goodwill', null=True)),
                ('investment_property', models.FloatField(blank=True, db_column='Investment property', null=True)),
                ('investment_in_affiliates', models.FloatField(blank=True, db_column='Investment in affiliates', null=True)),
                ('non_current_financial_assets', models.FloatField(blank=True, db_column='Non-current financial assets', null=True)),
                ('non_current_loans_and_receivables', models.FloatField(blank=True, db_column='Non-current loans and receivables', null=True)),
                ('deferred_income_tax', models.FloatField(blank=True, db_column='Deferred income tax', null=True)),
                ('non_current_deferred_charges_and_accruals', models.FloatField(blank=True, db_column='Non-current deferred charges and accruals', null=True)),
                ('non_current_derivative_instruments', models.FloatField(blank=True, db_column='Non-current derivative instruments', null=True)),
                ('other_non_current_assets', models.FloatField(blank=True, db_column='Other non-current assets', null=True)),
                ('inventories', models.FloatField(blank=True, db_column='Inventories', null=True)),
                ('current_intangible_assets', models.FloatField(blank=True, db_column='Current intangible assets', null=True)),
                ('biological_assets', models.FloatField(blank=True, db_column='Biological assets', null=True)),
                ('trade_receivables', models.FloatField(blank=True, db_column='Trade receivables', null=True)),
                ('loans_and_other_receivables', models.FloatField(blank=True, db_column='Loans and other receivables', null=True)),
                ('financial_assets', models.FloatField(blank=True, db_column='Financial assets', null=True)),
                ('cash_and_cash_equivalents', models.FloatField(blank=True, db_column='Cash and cash equivalents', null=True)),
                ('accruals', models.FloatField(blank=True, db_column='Accruals', null=True)),
                ('assets_from_current_tax', models.FloatField(blank=True, db_column='Assets from current tax', null=True)),
                ('derivative_instruments', models.FloatField(blank=True, db_column='Derivative instruments', null=True)),
                ('other_assets', models.FloatField(blank=True, db_column='Other assets', null=True)),
            ],
            options={
                'db_table': 'Assets',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AssetsCategories',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('date', models.DateField(blank=True, db_column='Date', null=True)),
                ('non_current_assets', models.FloatField(blank=True, db_column='Non-current assets', null=True)),
                ('current_assets', models.FloatField(blank=True, db_column='Current assets', null=True)),
                ('assets_held_for_sale_and_discontinuing_operations', models.FloatField(blank=True, db_column='Assets held for sale and discontinuing operations', null=True)),
                ('called_up_capital', models.FloatField(blank=True, db_column='Called up capital', null=True)),
                ('own_shares', models.FloatField(blank=True, db_column='Own shares', null=True)),
            ],
            options={
                'db_table': 'AssetsCategories',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, db_column='Name', max_length=255, null=True)),
                ('isin', models.CharField(blank=True, db_column='ISIN', max_length=255, null=True, unique=True)),
                ('ticker', models.CharField(blank=True, db_column='Ticker', max_length=255, null=True, unique=True)),
                ('bloomberg', models.CharField(blank=True, db_column='Bloomberg', max_length=255, null=True)),
            ],
            options={
                'db_table': 'Company',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DuPontIndicators',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('period_start', models.DateField(blank=True, db_column='Period start', null=True)),
                ('period_end', models.DateField(blank=True, db_column='Period end', null=True)),
                ('return_on_equity_roe_field', models.FloatField(blank=True, db_column='Return on equity (ROE)', null=True)),
                ('return_on_assets_roa_field', models.FloatField(blank=True, db_column='Return on assets (ROA)', null=True)),
                ('leverage_em_field', models.FloatField(blank=True, db_column='Leverage (EM)', null=True)),
                ('net_profit_margin', models.FloatField(blank=True, db_column='Net profit margin', null=True)),
                ('asset_utilization_au_field', models.FloatField(blank=True, db_column='Asset utilization (AU)', null=True)),
                ('load_gross_profit', models.FloatField(blank=True, db_column='Load gross profit', null=True)),
                ('load_operating_profit', models.FloatField(blank=True, db_column='Load operating profit', null=True)),
                ('operating_profit_margin', models.FloatField(blank=True, db_column='Operating profit margin', null=True)),
                ('ebitda_margin', models.FloatField(blank=True, db_column='EBITDA margin', null=True)),
            ],
            options={
                'db_table': 'DuPontIndicators',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EkdClass',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('value', models.IntegerField(blank=True, db_column='Value', null=True, unique=True)),
            ],
            options={
                'db_table': 'EKDClass',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EkdSection',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('value', models.IntegerField(blank=True, db_column='Value', null=True, unique=True)),
            ],
            options={
                'db_table': 'EKDSection',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EquityLiabilities',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('date', models.DateField(blank=True, db_column='Date', null=True)),
                ('share_capital', models.FloatField(blank=True, db_column='Share capital', null=True)),
                ('called_up_share_capital', models.FloatField(blank=True, db_column='Called up share capital', null=True)),
                ('treasury_shares', models.FloatField(blank=True, db_column='Treasury shares', null=True)),
                ('supplementary_capital', models.FloatField(blank=True, db_column='Supplementary capital', null=True)),
                ('valuation_and_exchange_differences', models.FloatField(blank=True, db_column='Valuation and exchange differences', null=True)),
                ('other_capitals', models.FloatField(blank=True, db_column='Other capitals', null=True)),
                ('retained_earnings_accumulated_losses', models.FloatField(blank=True, db_column='Retained earnings / accumulated losses', null=True)),
                ('non_current_liabilities_from_derivatives', models.FloatField(blank=True, db_column='Non-current liabilities from derivatives', null=True)),
                ('non_current_loans_and_borrowings', models.FloatField(blank=True, db_column='Non-current loans and borrowings', null=True)),
                ('non_current_liabilities_from_bonds', models.FloatField(blank=True, db_column='Non-current liabilities from bonds', null=True)),
                ('non_current_liabilities_from_finance_leases', models.FloatField(blank=True, db_column='Non-current liabilities from finance leases', null=True)),
                ('non_current_trade_payables', models.FloatField(blank=True, db_column='Non-current trade payables', null=True)),
                ('long_term_provision_for_employee_benefits', models.FloatField(blank=True, db_column='Long-term provision for employee benefits', null=True)),
                ('deferred_tax_liabilities', models.FloatField(blank=True, db_column='Deferred tax liabilities', null=True)),
                ('non_current_provision', models.FloatField(blank=True, db_column='Non-current provision', null=True)),
                ('other_non_current_liabilities', models.FloatField(blank=True, db_column='Other non-current liabilities', null=True)),
                ('non_current_accruals_liability_field', models.FloatField(blank=True, db_column='Non-current accruals (liability)', null=True)),
                ('liabilities_from_derivatives', models.FloatField(blank=True, db_column='Liabilities from derivatives', null=True)),
                ('financial_liabilities_loans_and_borrowings_field', models.FloatField(blank=True, db_column='Financial liabilities (loans and borrowings)', null=True)),
                ('bond_liabilities', models.FloatField(blank=True, db_column='Bond liabilities', null=True)),
                ('liabilities_from_finance_leases', models.FloatField(blank=True, db_column='Liabilities from finance leases', null=True)),
                ('trade_payables', models.FloatField(blank=True, db_column='Trade payables', null=True)),
                ('employee_benefits', models.FloatField(blank=True, db_column='Employee benefits', null=True)),
                ('current_tax_liabilities', models.FloatField(blank=True, db_column='Current tax liabilities', null=True)),
                ('provisions', models.FloatField(blank=True, db_column='Provisions', null=True)),
                ('other_liabilities', models.FloatField(blank=True, db_column='Other liabilities', null=True)),
                ('accruals_liability_field', models.FloatField(blank=True, db_column='Accruals (liability)', null=True)),
            ],
            options={
                'db_table': 'EquityLiabilities',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EquityLiabilitiesCategories',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('date', models.DateField(blank=True, db_column='Date', null=True)),
                ('equity_shareholders_of_the_parent', models.FloatField(blank=True, db_column='Equity shareholders of the parent', null=True)),
                ('non_controlling_interests', models.FloatField(blank=True, db_column='Non-controlling interests', null=True)),
                ('non_current_liabilities', models.FloatField(blank=True, db_column='Non-current liabilities', null=True)),
                ('current_liabilities', models.FloatField(blank=True, db_column='Current liabilities', null=True)),
                ('liabilities_related_to_assets_held_for_sale_and_discontinued_operations', models.FloatField(blank=True, db_column='Liabilities related to assets held for sale and discontinued operations', null=True)),
            ],
            options={
                'db_table': 'EquityLiabilitiesCategories',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='FinancialRatios',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('period_start', models.DateField(blank=True, db_column='Period start', null=True)),
                ('period_end', models.DateField(blank=True, db_column='Period end', null=True)),
                ('gross_profit_margin_on_sales', models.FloatField(blank=True, db_column='Gross profit margin on sales', null=True)),
                ('operating_profit_margin', models.FloatField(blank=True, db_column='Operating profit margin', null=True)),
                ('gross_profit_margin', models.FloatField(blank=True, db_column='Gross profit margin', null=True)),
                ('net_profit_margin', models.FloatField(blank=True, db_column='Net profit margin', null=True)),
                ('return_on_equity_roe_field', models.FloatField(blank=True, db_column='Return on equity (ROE)', null=True)),
                ('return_on_assets_roa_field', models.FloatField(blank=True, db_column='Return on assets (ROA)', null=True)),
                ('working_capital_ratio', models.FloatField(blank=True, db_column='Working capital ratio', null=True)),
                ('current_ratio', models.FloatField(blank=True, db_column='Current ratio', null=True)),
                ('quick_ratio', models.FloatField(blank=True, db_column='Quick ratio', null=True)),
                ('cash_ratio', models.FloatField(blank=True, db_column='Cash ratio', null=True)),
                ('receivables_turnover', models.FloatField(blank=True, db_column='Receivables turnover', null=True)),
                ('inventory_turnover', models.FloatField(blank=True, db_column='Inventory turnover', null=True)),
                ('the_operating_cycle', models.FloatField(blank=True, db_column='The operating cycle', null=True)),
                ('rotation_commitments', models.FloatField(blank=True, db_column='Rotation commitments', null=True)),
                ('cash_conversion_cycle', models.FloatField(blank=True, db_column='Cash conversion cycle', null=True)),
                ('rotation_assets', models.FloatField(blank=True, db_column='Rotation assets', null=True)),
                ('rotation_of_assets', models.FloatField(blank=True, db_column='Rotation of assets', null=True)),
                ('assets_ratio', models.FloatField(blank=True, db_column='Assets ratio', null=True)),
                ('debt_ratio', models.FloatField(blank=True, db_column='Debt ratio', null=True)),
                ('debt_service_ratio', models.FloatField(blank=True, db_column='Debt service ratio', null=True)),
                ('rate_debt_security', models.FloatField(blank=True, db_column='Rate debt security', null=True)),
            ],
            options={
                'db_table': 'FinancialRatios',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Interval',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('shortcut', models.CharField(blank=True, db_column='Shortcut', max_length=10, unique=True)),
                ('fullname', models.CharField(blank=True, db_column='FullName', max_length=255)),
            ],
            options={
                'db_table': 'Interval',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='StockQuotes',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('date', models.DateField(db_column='Date')),
                ('stock', models.FloatField(db_column='Stock')),
                ('change', models.FloatField(blank=True, db_column='Change', null=True)),
                ('open', models.FloatField(blank=True, db_column='Open', null=True)),
                ('high', models.FloatField(blank=True, db_column='High', null=True)),
                ('low', models.FloatField(blank=True, db_column='Low', null=True)),
                ('volume', models.IntegerField(blank=True, db_column='Volume', null=True)),
                ('turnover', models.IntegerField(blank=True, db_column='Turnover', null=True)),
                ('company_id', models.ForeignKey(db_column='CompanyID', on_delete=django.db.models.deletion.CASCADE, to='app.Company')),
                ('interval', models.ForeignKey(db_column='Interval', on_delete=django.db.models.deletion.DO_NOTHING, to='app.Interval')),
            ],
            options={
                'db_table': 'StockQuotes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MarketValues',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('period_end', models.DateField(db_column='Period end')),
                ('market_value', models.FloatField(db_column='Market value')),
                ('company_id', models.ForeignKey(db_column='CompanyID', on_delete=django.db.models.deletion.CASCADE, to='app.Company')),
            ],
            options={
                'db_table': 'MarketValues',
                'managed': True,
            },
        ),
        migrations.AddConstraint(
            model_name='interval',
            constraint=models.UniqueConstraint(fields=('shortcut',), name='interval_shortcut_unique'),
        ),
        migrations.AddField(
            model_name='financialratios',
            name='company_id',
            field=models.ForeignKey(blank=True, db_column='CompanyID', on_delete=django.db.models.deletion.CASCADE, to='app.Company'),
        ),
        migrations.AddField(
            model_name='equityliabilitiescategories',
            name='company_id',
            field=models.ForeignKey(blank=True, db_column='CompanyID', on_delete=django.db.models.deletion.CASCADE, to='app.Company'),
        ),
        migrations.AddField(
            model_name='equityliabilities',
            name='company_id',
            field=models.ForeignKey(blank=True, db_column='CompanyID', on_delete=django.db.models.deletion.CASCADE, to='app.Company'),
        ),
        migrations.AddField(
            model_name='dupontindicators',
            name='company_id',
            field=models.ForeignKey(blank=True, db_column='CompanyID', on_delete=django.db.models.deletion.CASCADE, to='app.Company'),
        ),
        migrations.AddField(
            model_name='company',
            name='ekd_class_id',
            field=models.ForeignKey(blank=True, db_column='EKDClassID', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.EkdClass'),
        ),
        migrations.AddField(
            model_name='company',
            name='ekd_section_id',
            field=models.ForeignKey(blank=True, db_column='EKDSectionID', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.EkdSection'),
        ),
        migrations.AddField(
            model_name='assetscategories',
            name='company_id',
            field=models.ForeignKey(blank=True, db_column='CompanyID', on_delete=django.db.models.deletion.CASCADE, to='app.Company'),
        ),
        migrations.AddField(
            model_name='assets',
            name='company_id',
            field=models.ForeignKey(blank=True, db_column='CompanyID', on_delete=django.db.models.deletion.CASCADE, to='app.Company'),
        ),
        migrations.AddConstraint(
            model_name='stockquotes',
            constraint=models.UniqueConstraint(fields=('company_id', 'date', 'interval'), name='stock_company_date_interval_unique'),
        ),
        migrations.AddConstraint(
            model_name='financialratios',
            constraint=models.UniqueConstraint(fields=('period_start', 'period_end', 'company_id'), name='financial_ratios_company_date_unique'),
        ),
        migrations.AddConstraint(
            model_name='equityliabilitiescategories',
            constraint=models.UniqueConstraint(fields=('company_id', 'date'), name='equity_liabilities_categories_company_date_unique'),
        ),
        migrations.AddConstraint(
            model_name='equityliabilities',
            constraint=models.UniqueConstraint(fields=('date', 'company_id'), name='equity_liabilities_company_date_unique'),
        ),
        migrations.AddConstraint(
            model_name='dupontindicators',
            constraint=models.UniqueConstraint(fields=('period_start', 'period_end', 'company_id'), name='dupont_indicators_company_date_unique'),
        ),
        migrations.AddConstraint(
            model_name='assetscategories',
            constraint=models.UniqueConstraint(fields=('company_id', 'date'), name='assets_categories_company_date_unique'),
        ),
        migrations.AddConstraint(
            model_name='assets',
            constraint=models.UniqueConstraint(fields=('company_id', 'date'), name='assets_company_date_unique'),
        ),
    ]