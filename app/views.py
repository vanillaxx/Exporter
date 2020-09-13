from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views import generic
from .forms import *
from common.Parsers import excel_parser, pdf_gpw_parser, stooq_parser, pdf_yearbook_parser, excel_yearbook_parser, \
    excel_gpw_parser
import common.Export.export as export_methods
from common.Utils.Errors import UniqueError
from .models import *
from common.DAL.db_queries import replace_values, get_existing_data_balance_sheet, get_existing_data_ratios
import json
import os.path
import uuid
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView


def index(request):
    return render(request, 'index.html')


def import_notoria(request):
    def render_overlapping_data_popup(chosen_sheet, sheet_shortcut, get_existing_data_func):
        for sheet in chosen_sheet:
            try:
                excel_parser.functions[sheet_shortcut](file_path, sheet)
            except UniqueError as e:
                existing_data = []
                for data in e.overlapping_data:
                    existing = get_existing_data_func(data)
                    existing_without_id = list(map(lambda x: x[1:], existing))
                    existing_data.append(existing_without_id)
                return existing_data, e
            return [], []

    if request.method == 'POST':
        form = NotoriaImportForm(request.POST)
        if form.is_valid():
            file_path = request.POST.get('file_path', None)
            chosen_sheets_bs = form.cleaned_data.get('chosen_sheets_bs')
            chosen_sheets_fr = form.cleaned_data.get('chosen_sheets_fr')
            chosen_sheets_dp = form.cleaned_data.get('chosen_sheets_dp')
            existing_data_bs = []
            existing_data_fr = []
            existing_data_dp = []
            error_bs = []
            error_fr = []
            error_dp = []
            overlap_bs = []
            overlap_fr = []
            overlap_dp = []
            if chosen_sheets_bs:
                existing_data_bs, error_bs = render_overlapping_data_popup(chosen_sheets_bs, 'bs',
                                                                           get_existing_data_balance_sheet)
                if error_bs:
                    overlap_bs = error_bs.overlapping_data
            if chosen_sheets_fr:
                existing_data_fr, error_fr = render_overlapping_data_popup(chosen_sheets_fr, 'fr', get_existing_data_ratios)
                if error_fr:
                    overlap_fr = error_fr.overlapping_data
            if chosen_sheets_dp:
                existing_data_dp, error_dp = render_overlapping_data_popup(chosen_sheets_dp, 'dp',
                                                                           get_existing_data_ratios)
                if error_dp:
                    overlap_dp = error_dp.overlapping_data

            if existing_data_bs or existing_data_fr or existing_data_dp:
                return render(request, 'import/notoria.html',
                              {'form': form,
                               "error_bs": error_bs,
                               "error_fr": error_fr,
                               "error_dp": error_dp,
                               "overlap_bs": json.dumps(overlap_bs),
                               "overlap_fr": json.dumps(overlap_fr),
                               "overlap_dp": json.dumps(overlap_dp),
                               "exist_bs": existing_data_bs,
                               "exist_fr": existing_data_fr,
                               "exist_dp": existing_data_dp})

            return render(request, 'manage/home.html', {'message': "Parsed notoria succsessfully"})
    else:
        form = NotoriaImportForm()

    return render(request, 'import/notoria.html', {'form': form})


def import_stooq(request):
    if request.method == 'POST':
        form = StooqImportForm(request.POST)
        if form.is_valid():
            SP = stooq_parser.StooqParser()
            ticker = form.cleaned_data.get('ticker', None)
            company = form.cleaned_data.get('company')

            date = form.cleaned_data.get('date', None)
            date_from = form.cleaned_data.get('date_from', None)
            date_to = form.cleaned_data.get('date_to', None)

            interval = form.cleaned_data.get('interval', None)

            if not company and not ticker and not date:
                return HttpResponse('Wrong form')

            if (company or ticker) and (not date_from or not date_to) and not date:
                return HttpResponse('Wrong form')

            if date_to and date_from and date_to < date_from and (company or ticker):
                return HttpResponse('Wrong form')

            if company and not ticker:
                ticker = company.ticker

            if ticker and date_from and date_to:
                SP.download_company(ticker, date_from, date_to, interval)

            if date:
                SP.download_all_companies(date)

            return render(request, 'manage/home.html', {'message': "Parsed stooq.com data successfully"})
        else:
            return HttpResponse('Wrong form')
    else:
        form = StooqImportForm()

    return render(request, 'import/stooq.html', {'form': form})


def import_gpw(request):
    parsers = {
        'yearbook_excel': excel_yearbook_parser.ExcelYearbookParser,
        'yearbook_pdf': pdf_yearbook_parser.PdfYearbookParser,
        'statistics_excel': excel_gpw_parser.ExcelGPWParser,
        'statistics_pdf': pdf_gpw_parser.PdfGPWParser
    }

    if request.method == 'POST':
        form = GpwImportForm(request.POST)
        if form.is_valid():
            path = form.cleaned_data['path']
            file_type = form.cleaned_data['file_type']
            parser = parsers[file_type]()
            parser.parse(path)
            return render(request, 'manage/home.html', {'message': "Parsed GPW file successfully"})
    else:
        form = GpwImportForm()

    return render(request, 'import/gpw.html', {'form': form})


def export(request):
    if request.method == 'POST':
        form = ExportForm(request.POST, count=request.POST.get('date_ranges_count'))
        if form.is_valid():
            file_name = request.POST.get('file_name', None)
            is_file_name_unique = True
            if not file_name.endswith(".csv"):
                file_name += ".csv"
            if os.path.isfile(file_name):
                is_file_name_unique = False
                csv_index = file_name.rfind(".csv")
                file_name = file_name[:csv_index] + str(uuid.uuid4()) + file_name[csv_index:]

            chosen_data = request.POST.get('chosen_data', None)
            chosen_companies = list(form.cleaned_data.get('chosen_companies').values_list('id', flat=True))
            chosen_interval = form.cleaned_data.get('chosen_interval', None)
            date_ranges_count = request.POST.get('date_ranges_count', None)
            for index in range(int(date_ranges_count) + 1):
                start_date = form.cleaned_data.get('start_date_{index}'.format(index=index))
                end_date = form.cleaned_data.get('end_date_{index}'.format(index=index))

                if chosen_data != '-s':
                    if index == 0:
                        export_methods.functions[chosen_data](chosen_companies, start_date, end_date, file_name)
                    else:
                        export_methods.functions[chosen_data](chosen_companies, start_date, end_date, file_name,
                                                              add_description=False)
                else:
                    if index == 0:
                        export_methods.functions['-s'](chosen_companies, start_date, end_date, file_name, chosen_interval)
                    else:
                        export_methods.functions['-s'](chosen_companies, start_date, end_date, file_name, chosen_interval,
                                                              add_description=False)
            if is_file_name_unique:
                return render(request, 'manage/home.html', {'message': "Data exported to %s" % file_name})
            else:
                return render(request, 'manage/home.html',
                              {'message': "Passed file name exists. Data exported to %s" % file_name})

    else:
        form = ExportForm()

    return render(request, 'export/export.html', {'form': form})


def manage(request):
    return render(request, 'manage/home.html')


def replace_data(request):
    data = request.POST.get('data', '')
    json_data = json.loads(data)
    for data_to_replace in json_data:
        table_name = data_to_replace['table_name']
        columns = data_to_replace['columns']
        values = data_to_replace['values']
        for value in values:
            replace_values(table_name, columns, value)
    return HttpResponse({'message': "Data replaced successfully"})


#region grid_edition_views

class CompanyView(generic.ListView):
    model = Company
    context_object_name = 'companies'
    template_name = 'manage/companies.html'


class CompanyCreateView(BSModalCreateView):
    template_name = 'manage/companies/create.html'
    form_class = CompanyModelForm
    success_message = 'Success: Company was created.'
    success_url = reverse_lazy('companies')


class CompanyUpdateView(BSModalUpdateView):
    model = Company
    template_name = 'manage/companies/update.html'
    form_class = CompanyModelForm
    success_message = 'Success: Company was updated.'
    success_url = reverse_lazy('companies')


class CompanyDeleteView(BSModalDeleteView):
    model = Company
    template_name = 'manage/companies/delete.html'
    success_message = 'Success: Company was deleted.'
    success_url = reverse_lazy('companies')


class AssetsView(generic.ListView):
    model = Assets
    context_object_name = 'assets'
    template_name = 'manage/assets.html'


class AssetsCreateView(BSModalCreateView):
    template_name = 'manage/assets/create.html'
    form_class = AssetsModelForm
    success_message = 'Success: Assets was created.'
    success_url = reverse_lazy('assets')


class AssetsUpdateView(BSModalUpdateView):
    model = Assets
    template_name = 'manage/assets/update.html'
    form_class = AssetsModelForm
    success_message = 'Success: Assets was updated.'
    success_url = reverse_lazy('assets')


class AssetsDeleteView(BSModalDeleteView):
    model = Assets
    template_name = 'manage/assets/delete.html'
    success_message = 'Success: Assets was deleted.'
    success_url = reverse_lazy('assets')


class AssetsCategoryView(generic.ListView):
    model = AssetsCategories
    context_object_name = 'assets_categories'
    template_name = 'manage/assetsCategories.html'


class AssetsCategoryCreateView(BSModalCreateView):
    template_name = 'manage/assetsCategories/create.html'
    form_class = AssetsCategoryModelForm
    success_message = 'Success: Assets category was created.'
    success_url = reverse_lazy('assets_categories')


class AssetsCategoryUpdateView(BSModalUpdateView):
    model = AssetsCategories
    template_name = 'manage/assetsCategories/update.html'
    form_class = AssetsCategoryModelForm
    success_message = 'Success: Assets category was updated.'
    success_url = reverse_lazy('assets_categories')


class AssetsCategoryDeleteView(BSModalDeleteView):
    model = AssetsCategories
    template_name = 'manage/assetsCategories/delete.html'
    success_message = 'Success: Assets category was deleted.'
    success_url = reverse_lazy('assets_categories')


class DuPontIndicatorView(generic.ListView):
    model = DuPontIndicators
    context_object_name = 'indicators'
    template_name = 'manage/duPont.html'


class DuPontIndicatorCreateView(BSModalCreateView):
    template_name = 'manage/duPont/create.html'
    form_class = DuPointIndicatorModelForm
    success_message = 'Success: DuPont indicator was created.'
    success_url = reverse_lazy('dupont')


class DuPontIndicatorUpdateView(BSModalUpdateView):
    model = DuPontIndicators
    template_name = 'manage/duPont/update.html'
    form_class = DuPointIndicatorModelForm
    success_message = 'Success: DuPont indicator was updated.'
    success_url = reverse_lazy('dupont')


class DuPontIndicatorDeleteView(BSModalDeleteView):
    model = DuPontIndicators
    template_name = 'manage/duPont/delete.html'
    success_message = 'Success: DuPont indicator was deleted.'
    success_url = reverse_lazy('dupont')


class EkdClassView(generic.ListView):
    model = EkdClass
    context_object_name = 'classes'
    template_name = 'manage/ekdClasses.html'


class EkdClassCreateView(BSModalCreateView):
    template_name = 'manage/ekdClasses/create.html'
    form_class = EkdClassModelForm
    success_message = 'Success: EKD class was created.'
    success_url = reverse_lazy('ekd_classes')


class EkdClassUpdateView(BSModalUpdateView):
    model = EkdClass
    template_name = 'manage/ekdClasses/update.html'
    form_class = EkdClassModelForm
    success_message = 'Success: EKD class was updated.'
    success_url = reverse_lazy('ekd_classes')


class EkdClassDeleteView(BSModalDeleteView):
    model = EkdClass
    template_name = 'manage/ekdClasses/delete.html'
    success_message = 'Success: EKD class was deleted.'
    success_url = reverse_lazy('ekd_classes')


class EkdSectionView(generic.ListView):
    model = EkdSection
    context_object_name = 'sections'
    template_name = 'manage/ekdSections.html'


class EkdSectionCreateView(BSModalCreateView):
    template_name = 'manage/ekdSections/create.html'
    form_class = EkdSectionModelForm
    success_message = 'Success: EKD section was created.'
    success_url = reverse_lazy('ekd_sections')


class EkdSectionUpdateView(BSModalUpdateView):
    model = EkdSection
    template_name = 'manage/ekdSections/update.html'
    form_class = EkdSectionModelForm
    success_message = 'Success: EKD section was updated.'
    success_url = reverse_lazy('ekd_sections')


class EkdSectionDeleteView(BSModalDeleteView):
    model = EkdSection
    template_name = 'manage/ekdSections/delete.html'
    success_message = 'Success: EKD section was deleted.'
    success_url = reverse_lazy('ekd_sections')


class EquityLiabilitiesView(generic.ListView):
    model = EquityLiabilities
    context_object_name = 'liabilities'
    template_name = 'manage/equityLiabilities.html'


class EquityLiabilitiesCreateView(BSModalCreateView):
    template_name = 'manage/equityLiabilities/create.html'
    form_class = EquityLiabilitiesModelForm
    success_message = 'Success: Equity Liabilities was created.'
    success_url = reverse_lazy('equity_liabilities')


class EquityLiabilitiesUpdateView(BSModalUpdateView):
    model = EquityLiabilities
    template_name = 'manage/equityLiabilities/update.html'
    form_class = EquityLiabilitiesModelForm
    success_message = 'Success: EquityLiabilities was updated.'
    success_url = reverse_lazy('equity_liabilities')


class EquityLiabilitiesDeleteView(BSModalDeleteView):
    model = EquityLiabilities
    template_name = 'manage/equityLiabilities/delete.html'
    success_message = 'Success: EquityLiabilities was deleted.'
    success_url = reverse_lazy('equity_liabilities')


class EquityLiabilitiesCategoryView(generic.ListView):
    model = EquityLiabilitiesCategories
    context_object_name = 'liabilities_categories'
    template_name = 'manage/equityLiabilitiesCategories.html'


class EquityLiabilitiesCategoryCreateView(BSModalCreateView):
    template_name = 'manage/equityLiabilitiesCategories/create.html'
    form_class = EquityLiabilitiesCategoryModelForm
    success_message = 'Success: Equity liabilities category was created.'
    success_url = reverse_lazy('equity_liabilities_categories')


class EquityLiabilitiesCategoryUpdateView(BSModalUpdateView):
    model = EquityLiabilitiesCategories
    template_name = 'manage/equityLiabilitiesCategories/update.html'
    form_class = EquityLiabilitiesCategoryModelForm
    success_message = 'Success: Equity liabilities category was updated.'
    success_url = reverse_lazy('equity_liabilities_categories')


class EquityLiabilitiesCategoryDeleteView(BSModalDeleteView):
    model = EquityLiabilitiesCategories
    template_name = 'manage/equityLiabilitiesCategories/delete.html'
    success_message = 'Success: Equity liabilities category was deleted.'
    success_url = reverse_lazy('equity_liabilities_categories')


class FinancialRatiosView(generic.ListView):
    model = FinancialRatios
    context_object_name = 'ratios'
    template_name = 'manage/financial.html'


class FinancialRatiosCreateView(BSModalCreateView):
    template_name = 'manage/financial/create.html'
    form_class = FinancialRatiosModelForm
    success_message = 'Success: Financial ratios was created.'
    success_url = reverse_lazy('financial')


class FinancialRatiosUpdateView(BSModalUpdateView):
    model = FinancialRatios
    template_name = 'manage/financial/update.html'
    form_class = FinancialRatiosModelForm
    success_message = 'Success: Financial ratios was updated.'
    success_url = reverse_lazy('financial')


class FinancialRatiosDeleteView(BSModalDeleteView):
    model = FinancialRatios
    template_name = 'manage/financial/delete.html'
    success_message = 'Success: Financial ratios was deleted.'
    success_url = reverse_lazy('financial')


class MarketValueView(generic.ListView):
    model = MarketValues
    context_object_name = 'values'
    template_name = 'manage/market.html'


class MarketValueCreateView(BSModalCreateView):
    template_name = 'manage/market/create.html'
    form_class = MarketValuesModelForm
    success_message = 'Success: Market value was created.'
    success_url = reverse_lazy('market')


class MarketValueUpdateView(BSModalUpdateView):
    model = MarketValues
    template_name = 'manage/market/update.html'
    form_class = MarketValuesModelForm
    success_message = 'Success: Market value was updated.'
    success_url = reverse_lazy('market')


class MarketValueDeleteView(BSModalDeleteView):
    model = MarketValues
    template_name = 'manage/market/delete.html'
    success_message = 'Success: Market value was deleted.'
    success_url = reverse_lazy('market')


class StockQuoteView(generic.ListView):
    model = StockQuotes
    context_object_name = 'stock'
    template_name = 'manage/stock.html'


class StockQuoteCreateView(BSModalCreateView):
    template_name = 'manage/stock/create.html'
    form_class = StockQuotesModelForm
    success_message = 'Success: Stock quote was created.'
    success_url = reverse_lazy('stock')


class StockQuoteUpdateView(BSModalUpdateView):
    model = StockQuotes
    template_name = 'manage/stock/update.html'
    form_class = StockQuotesModelForm
    success_message = 'Success: Stock quote was updated.'
    success_url = reverse_lazy('stock')


class StockQuoteDeleteView(BSModalDeleteView):
    model = StockQuotes
    template_name = 'manage/stock/delete.html'
    success_message = 'Success: Stock quote was deleted.'
    success_url = reverse_lazy('stock')

#endregion
