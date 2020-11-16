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
    merge_stock_quotes, merge_market_values
from common.DAL.db_queries_delete import delete_from_assets, delete_from_assets_categories, \
    delete_from_dupont_indicators, delete_from_equity_liabilities, delete_from_equity_liabilities_categories, \
    delete_from_financial_ratios, delete_company, delete_from_stock_quotes, delete_from_market_values
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
        chosen_from = valid_data.get('chosen_from')
        chosen_to = valid_data.get('chosen_to')
        chosen_from_name = chosen_from.name
        chosen_from = chosen_from.id
        chosen_to_name = chosen_to.name
        chosen_to = chosen_to.id

        merge_assets(chosen_from, chosen_to)
        merge_assets_categories(chosen_from, chosen_to)
        merge_equity_liabilities(chosen_from, chosen_to)
        merge_equity_liabilities_categories(chosen_from, chosen_to)
        merge_financial_ratios(chosen_from, chosen_to)
        merge_dupont_indicators(chosen_from, chosen_to)
        merge_stock_quotes(chosen_from, chosen_to)
        merge_market_values(chosen_from, chosen_to)

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

        overlapping_market_values_data = self.add_overlapping_market_values(chosen_from, chosen_to)

        delete_from_assets(chosen_from)
        delete_from_assets_categories(chosen_from)
        delete_from_equity_liabilities(chosen_from)
        delete_from_equity_liabilities_categories(chosen_from)
        delete_from_stock_quotes(chosen_from)
        delete_from_financial_ratios(chosen_from)
        delete_from_dupont_indicators(chosen_from)
        delete_from_market_values(chosen_from)
        delete_company(chosen_from)

        if overlapping_balance_data or overlapping_financial_ratios_data or overlapping_dupont_indicators_data \
                or overlapping_stock_quotes_data or overlapping_market_values_data:
            error_bs = []
            error_fr = []
            error_dp = []
            error_stock = []
            error_market_values = []
            overlap_bs = []
            overlap_fr = []
            overlap_dp = []
            overlap_stock = []
            overlap_market_values = []
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
            if overlapping_market_values_data:
                error_market_values = UniqueError(*overlapping_market_values_data)
                overlap_market_values = json.dumps(overlapping_market_values_data, default=str)

            return render(self.request, 'manage/home.html',
                          {"chosen_from": chosen_from_name,
                           "chosen_to": chosen_to_name,
                           "error_bs": error_bs,
                           "overlap_bs": overlap_bs,
                           "error_fr": error_fr,
                           "overlap_fr": overlap_fr,
                           "error_dp": error_dp,
                           "overlap_dp": overlap_dp,
                           "error_stock": error_stock,
                           "overlap_stock": overlap_stock,
                           'error_mv': error_market_values,
                           'overlap_mv': overlap_market_values
                           })
        else:
            messages.success(self.request, self.success_message)
            return HttpResponseRedirect(self.get_success_url())

    @staticmethod
    def add_overlapping_market_values(chosen_from, chosen_to):
        overlapping_values = MarketValues.objects.filter(company_id=chosen_from)
        overlapping_dates = overlapping_values.values_list('period_end', flat=True)
        merge_to = MarketValues.objects.filter(company_id=chosen_to, period_end__in=overlapping_dates)\
            .values_list('period_end', 'market_value')
        merge_from = overlapping_values.values_list('period_end', 'market_value')

        merge_to_unique = list(merge_to.difference(merge_from).order_by('period_end'))
        merge_from_unique = list(merge_from.difference(merge_to).order_by('period_end'))

        def add_id(t, id):
            t = list(t)
            t.insert(0, id)
            return t

        if merge_from_unique and merge_to_unique:
            merge_to_unique = list(map(lambda t: add_id(t, chosen_to), merge_to_unique))
            merge_from_unique = list(map(lambda t: add_id(t, chosen_from), merge_from_unique))

            result = {'table_name': 'MarketValues',
                      'columns': ['CompanyID', 'Period end', 'Market value'],
                      'values': merge_from_unique,
                      'exists': merge_to_unique}
            return [result]
        else:
            return []


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
        for value in values:
            listed_value = list(value)
            listed_value[0] = existing_company_id
            replace_values(table_name, columns, listed_value)

    return HttpResponse({'message': "Data replaced successfully"})
