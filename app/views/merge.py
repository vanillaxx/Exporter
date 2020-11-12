from collections import deque
from datetime import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from common.Utils.Errors import UniqueError
from ..forms import *
from ..models import *
import json
from django.contrib import messages
from bootstrap_modal_forms.generic import BSModalFormView
from common.DAL.db_queries_get import get_existing_data_financial_ratios, get_existing_data_dupont_indicators, \
    get_existing_data_stock_quotes_merge
from common.DAL.db_queries_merge import merge_assets, merge_assets_categories, merge_dupont_indicators, \
    merge_equity_liabilities_categories, merge_equity_liabilities, merge_financial_ratios, \
    merge_stock_quotes
from common.DAL.db_queries_delete import delete_from_assets, delete_from_assets_categories,\
    delete_from_dupont_indicators, delete_from_equity_liabilities, delete_from_equity_liabilities_categories,\
    delete_from_financial_ratios, delete_company, delete_from_stock_quotes
from common.DAL.db_queries_insert import replace_values


class CompanyMergeView(SuccessMessageMixin, BSModalFormView):
    template_name = 'manage/companies/merge.html'
    form_class = MergeForm
    success_message = 'Companies were merged.'
    success_url = reverse_lazy('companies')

    def form_valid(self, form):
        if not self.request.is_ajax():
            return self.merge_companies(form.cleaned_data)
        return super().form_valid(form)

    def merge_companies(self, valid_data):
        chosen_from = valid_data.get('chosen_from').id
        chosen_to = valid_data.get('chosen_to').id
        merge_assets(chosen_from, chosen_to)
        merge_assets_categories(chosen_from, chosen_to)
        merge_equity_liabilities(chosen_from, chosen_to)
        merge_equity_liabilities_categories(chosen_from, chosen_to)
        merge_financial_ratios(chosen_from, chosen_to)
        merge_dupont_indicators(chosen_from, chosen_to)
        merge_stock_quotes(chosen_from, chosen_to)

        overlapping_assets = Assets.objects.filter(company_id=chosen_from).order_by('date')
        overlapping_assets_categories = AssetsCategories.objects.filter(company_id=chosen_from).order_by('date')
        overlapping_equity_liabilities = EquityLiabilities.objects.filter(company_id=chosen_from).order_by('date')
        overlapping_equity_liabilities_categories = EquityLiabilitiesCategories.objects.filter(
            company_id=chosen_from).order_by('date')
        overlapping_financial_ratios = FinancialRatios.objects.filter(company_id=chosen_from).order_by('period_start',
                                                                                                       'period_end')
        overlapping_dupont_indicators = DuPontIndicators.objects.filter(company_id=chosen_from).order_by('period_start',
                                                                                                         'period_end')
        overlapping_stock_quotes = StockQuotes.objects.filter(company_id=chosen_from).order_by('date', 'interval')

        overlapping_balance_data = []
        overlapping_financial_ratios_data = []
        overlapping_dupont_indicators_data = []
        overlapping_stock_quotes_data = []
        balance_was_same = False
        fr_was_same = False
        dp_was_same = False
        stock_was_same = False

        def add_overlapping_balance(model, overlapping_values, overlapping_data):
            merge_to = model.objects.filter(company_id=chosen_to,
                                                date__in=overlapping_values.values("date")
                                                ).order_by('date').values_list(flat=True)
            merge_to_values = list(map(lambda x: list(x.values())[1:], merge_to.values()))
            merge_from_values = list(
                map(lambda x: list(x.values())[1:], overlapping_values.values_list(flat=True).values()))
            index = 0
            indexes = deque()
            for f, t in zip(merge_from_values, merge_to_values):
                if f[1:] == list(t)[1:]:
                    indexes.appendleft(index)
                index += 1

            for i in indexes:
                del merge_from_values[i]
                del merge_to_values[i]

            if indexes:
                nonlocal balance_was_same
                balance_was_same = True

            if merge_from_values:
                result = {"table_name": model.objects.model._meta.db_table,
                          "columns": [f.get_attname_column()[1] for f in model._meta.get_fields() if f.name != 'id'],
                          "values": merge_from_values,
                          "exists": merge_to_values}
                overlapping_data.append(result)
            return overlapping_data

        def add_overlapping_ratios(model, overlapping_values, overlapping_data):
            overlapping_dates = overlapping_values.values_list("period_start", "period_end")
            if model is FinancialRatios:
                merge_to_values = get_existing_data_financial_ratios(chosen_to, overlapping_dates)
            elif model is DuPontIndicators:
                merge_to_values = get_existing_data_dupont_indicators(chosen_to, overlapping_dates)
            merge_to_values = list(merge_to_values)

            merge_from_values = list(
                map(lambda x: list(x.values())[1:], overlapping_values.values_list(flat=True).values()))
            index = 0
            indexes = deque()
            for f, t in zip(merge_from_values, merge_to_values):
                if f[1] == datetime.strptime(t[1], '%Y-%m-%d').date() and f[2] == datetime.strptime(t[2], '%Y-%m-%d').date():
                    if f[3:] == list(t)[3:]:
                        indexes.appendleft(index)
                index += 1

            for i in indexes:
                del merge_from_values[i]
                del merge_to_values[i]

            if indexes and model is FinancialRatios:
                nonlocal fr_was_same
                fr_was_same = True
            elif indexes and model is DuPontIndicators:
                nonlocal dp_was_same
                dp_was_same = True

            if merge_from_values:
                result = {"table_name": model.objects.model._meta.db_table,
                          "columns": [f.get_attname_column()[1] for f in model._meta.get_fields() if f.name != 'id'],
                          "values": merge_from_values,
                          "exists": merge_to_values}
                overlapping_data.append(result)
            return overlapping_data

        def add_overlapping_stock_quotes(model, overlapping_values, overlapping_data):
            overlapping_dates_intervals = overlapping_values.values_list("date", "interval")
            if model is StockQuotes:
                merge_to_values = get_existing_data_stock_quotes_merge(chosen_to, overlapping_dates_intervals)
            merge_to_values = list(merge_to_values)

            merge_from_values = list(
                map(lambda x: list(x.values())[1:], overlapping_values.values_list(flat=True).values()))
            index = 0
            indexes = deque()
            for f, t in zip(merge_from_values, merge_to_values):
                if f[1] == datetime.strptime(t[1], '%Y-%m-%d').date() and f[9] == t[9]:
                    if f[2:9] == list(t)[2:9]:
                        indexes.appendleft(index)
                index += 1

            for i in indexes:
                del merge_from_values[i]
                del merge_to_values[i]

            if indexes and model is StockQuotes:
                nonlocal stock_was_same
                stock_was_same = True

            if merge_from_values:
                result = {"table_name": model.objects.model._meta.db_table,
                          "columns": [f.get_attname_column()[1] for f in model._meta.get_fields() if f.name != 'id'],
                          "values": merge_from_values,
                          "exists": merge_to_values}
                overlapping_data.append(result)
            return overlapping_data

        if overlapping_assets:
            overlapping_balance_data = add_overlapping_balance(Assets, overlapping_assets, overlapping_balance_data)
        if overlapping_assets_categories:
            overlapping_balance_data = add_overlapping_balance(AssetsCategories, overlapping_assets_categories,
                                                            overlapping_balance_data)
        if overlapping_equity_liabilities:
            overlapping_balance_data = add_overlapping_balance(EquityLiabilities, overlapping_equity_liabilities,
                                                            overlapping_balance_data)
        if overlapping_equity_liabilities_categories:
            overlapping_balance_data = add_overlapping_balance(EquityLiabilitiesCategories,
                                                            overlapping_equity_liabilities_categories,
                                                            overlapping_balance_data)
        if overlapping_financial_ratios:
            overlapping_financial_ratios_data = add_overlapping_ratios(FinancialRatios, overlapping_financial_ratios,
                                                                     overlapping_financial_ratios_data)
        if overlapping_dupont_indicators:
            overlapping_dupont_indicators_data = add_overlapping_ratios(DuPontIndicators, overlapping_dupont_indicators,
                                                                      overlapping_dupont_indicators_data)

        if overlapping_stock_quotes:
            overlapping_stock_quotes_data = add_overlapping_stock_quotes(StockQuotes, overlapping_stock_quotes,
                                                                         overlapping_stock_quotes_data)

        if overlapping_balance_data or overlapping_financial_ratios_data or overlapping_dupont_indicators_data \
                or overlapping_stock_quotes_data:
            error_bs = []
            error_fr = []
            error_dp = []
            error_stock = []
            overlap_bs = []
            overlap_fr = []
            overlap_dp = []
            overlap_stock = []
            if overlapping_balance_data:
                error_bs = UniqueError(*overlapping_balance_data)
                overlap_bs = json.dumps(error_bs.overlapping_data, default=str)
            if overlapping_financial_ratios_data:
                error_fr = UniqueError(*overlapping_financial_ratios_data)
                overlap_fr = json.dumps(error_fr.overlapping_data, default=str)
            if overlapping_dupont_indicators_data:
                error_dp = UniqueError(*overlapping_dupont_indicators_data)
                overlap_dp = json.dumps(error_dp.overlapping_data, default=str)
            if overlapping_stock_quotes_data:
                error_stock = UniqueError(*overlapping_stock_quotes_data)
                overlap_stock = json.dumps(error_stock.overlapping_data, default=str)
            return render(self.request, 'manage/home.html',
                          {"company_to_delete_id": chosen_from,
                           "error_bs": error_bs,
                           "overlap_bs": overlap_bs,
                           "error_fr": error_fr,
                           "overlap_fr": overlap_fr,
                           "error_dp": error_dp,
                           "overlap_dp": overlap_dp,
                           "error_stock": error_stock,
                           "overlap_stock": overlap_stock
                           })
        else:
            if balance_was_same:
                delete_from_assets(chosen_from)
                delete_from_assets_categories(chosen_from)
                delete_from_equity_liabilities(chosen_from)
                delete_from_equity_liabilities_categories(chosen_from)
            if fr_was_same:
                delete_from_financial_ratios(chosen_from)
            if dp_was_same:
                delete_from_dupont_indicators(chosen_from)
            if stock_was_same:
                delete_from_stock_quotes(chosen_from)

            delete_company(chosen_from)
            messages.success(self.request, self.success_message)
            return HttpResponseRedirect(self.get_success_url())


def merge_data(request):
    data = request.POST.get('data', '')
    json_data = json.loads(data)
    for data_to_replace in json_data:
        if not data_to_replace:
            continue

        table_name = data_to_replace['table_name']
        columns = data_to_replace['columns']
        values = data_to_replace['values']
        existing_company_id = data_to_replace["exists"][0][0]
        company_to_delete_id = values[0][0]
        for value in values:
            listed_value = list(value)
            listed_value[0] = existing_company_id
            replace_values(table_name, columns, listed_value)

    errors_amount = request.POST.get('errors_amount', '')
    print(errors_amount)
    sheet = request.POST.get('sheet', '')
    if sheet == 'bs':
        delete_from_assets(company_to_delete_id)
        delete_from_assets_categories(company_to_delete_id)
        delete_from_equity_liabilities(company_to_delete_id)
        delete_from_equity_liabilities_categories(company_to_delete_id)
        delete_from_stock_quotes(company_to_delete_id)
    elif sheet == 'fr':
        delete_from_financial_ratios(company_to_delete_id)
    elif sheet == 'dp':
        delete_from_dupont_indicators(company_to_delete_id)

    if int(errors_amount) == 0:
        delete_from_assets(company_to_delete_id)
        delete_from_assets_categories(company_to_delete_id)
        delete_from_equity_liabilities(company_to_delete_id)
        delete_from_equity_liabilities_categories(company_to_delete_id)
        delete_from_stock_quotes(company_to_delete_id)
        delete_from_financial_ratios(company_to_delete_id)
        delete_from_dupont_indicators(company_to_delete_id)
        delete_company(company_to_delete_id)

    return HttpResponse({'message': "Data replaced successfully"})


def delete_data(request):
    company_to_delete_id = request.POST.get('company_to_delete_id', '')
    errors_amount = request.POST.get('errors_amount', '')
    print(errors_amount)
    sheet = request.POST.get('sheet', '')
    if sheet == 'bs':
        delete_from_assets(company_to_delete_id)
        delete_from_assets_categories(company_to_delete_id)
        delete_from_equity_liabilities(company_to_delete_id)
        delete_from_equity_liabilities_categories(company_to_delete_id)
        delete_from_stock_quotes(company_to_delete_id)
    elif sheet == 'fr':
        delete_from_financial_ratios(company_to_delete_id)
    elif sheet == 'dp':
        delete_from_dupont_indicators(company_to_delete_id)

    if int(errors_amount) == 0:
        delete_from_assets(company_to_delete_id)
        delete_from_assets_categories(company_to_delete_id)
        delete_from_equity_liabilities(company_to_delete_id)
        delete_from_equity_liabilities_categories(company_to_delete_id)
        delete_from_stock_quotes(company_to_delete_id)
        delete_from_financial_ratios(company_to_delete_id)
        delete_from_dupont_indicators(company_to_delete_id)
        delete_company(company_to_delete_id)

    return HttpResponse({'message': "Data replaced successfully."})
