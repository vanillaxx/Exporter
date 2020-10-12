from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views import generic
from common.Utils.export_status import ExportStatus
from .forms import *
from common.Parsers import excel_parser, pdf_gpw_parser, stooq_parser, pdf_yearbook_parser, excel_yearbook_parser, \
    excel_gpw_parser
import common.Export.export as export_methods
from common.Utils.Errors import UniqueError, ParseError
from .models import *
from common.DAL.db_queries import replace_values, get_existing_data_balance_sheet, get_existing_data_ratios, \
    merge_assets_categories, get_existing_data_stock_quotes
import json
import os.path
import uuid
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalFormView
from common.DAL.db_queries import merge_assets, merge_assets_categories, merge_dupont_indicators, \
    merge_equity_liabilities_categories, merge_equity_liabilities, merge_financial_ratios, delete_from_assets, \
    delete_from_assets_categories, delete_from_dupont_indicators, delete_from_equity_liabilities, \
    delete_from_equity_liabilities_categories, delete_from_financial_ratios, delete_company


def index(request):
    return render(request, 'index.html')


def import_notoria(request):
    def render_overlapping_data_popup(chosen_sheet, sheet_shortcut, get_existing_data_func):
        for sheet in chosen_sheet:
            try:
                excel_parser.functions[sheet_shortcut](file_path, sheet)
            except UniqueError as e:
                for data in e.overlapping_data:
                    existing = get_existing_data_func(data)
                    data["exists"] = list(map(lambda x: list(x), existing))
                return e
            return []

    if request.method == 'POST':
        form = NotoriaImportForm(request.POST)
        if form.is_valid():
            file_path = request.POST.get('file_path', None)
            chosen_sheets_bs = form.cleaned_data.get('chosen_sheets_bs')
            chosen_sheets_fr = form.cleaned_data.get('chosen_sheets_fr')
            chosen_sheets_dp = form.cleaned_data.get('chosen_sheets_dp')
            error_bs = []
            error_fr = []
            error_dp = []
            overlap_bs = []
            overlap_fr = []
            overlap_dp = []
            if chosen_sheets_bs:
                error_bs = render_overlapping_data_popup(chosen_sheets_bs, 'bs',
                                                                           get_existing_data_balance_sheet)
                if error_bs:
                    overlap_bs = error_bs.overlapping_data

            if chosen_sheets_fr:
                error_fr = render_overlapping_data_popup(chosen_sheets_fr, 'fr',
                                                                           get_existing_data_ratios)
                if error_fr:
                    overlap_fr = error_fr.overlapping_data

            if chosen_sheets_dp:
                error_dp = render_overlapping_data_popup(chosen_sheets_dp, 'dp',
                                                                           get_existing_data_ratios)
                if error_dp:
                    overlap_dp = error_dp.overlapping_data

            if error_bs or error_fr or error_dp:
                return render(request, 'import/notoria.html',
                              {'form': form,
                               "error_bs": error_bs,
                               "error_fr": error_fr,
                               "error_dp": error_dp,
                               "overlap_bs": json.dumps(overlap_bs),
                               "overlap_fr": json.dumps(overlap_fr),
                               "overlap_dp": json.dumps(overlap_dp)})

            return render(request, 'manage/home.html', {'message': "Parsed notoria succsessfully"})
    else:
        form = NotoriaImportForm()

    return render(request, 'import/notoria.html', {'form': form})


def import_stooq(request):
    def parse_stooq_one_company(ticker_arg, date_from_arg, date_to_arg, interval_arg):
        SP = stooq_parser.StooqParser()
        try:
            SP.download_company(ticker_arg, date_from_arg, date_to_arg, interval_arg)
        except UniqueError as e:
            for data in e.overlapping_data:
                existing = get_existing_data_stock_quotes(data)
                data["exists"] = list(map(lambda x: list(x), existing))
            return e
        except ParseError as pe:
            raise pe
        return [], []

    def parse_stooq_all_companies(date_arg):
        SP = stooq_parser.StooqParser()
        try:
            SP.download_all_companies(date_arg)
        except UniqueError as e:
            for data in e.overlapping_data:
                existing = get_existing_data_stock_quotes(data)
                data["exists"] = list(map(lambda x: list(x), existing))
            return e
        except ParseError as pe:
            raise pe
        return [], []

    if request.method == 'POST':
        form = StooqImportForm(request.POST)
        if form.is_valid():
            error = []
            overlap = []

            import_type = request.POST.get('import_type')

            if import_type == 'one':
                ticker = form.cleaned_data.get('ticker', None)
                company = form.cleaned_data.get('company')

                date_from = form.cleaned_data.get('date_from', None)
                date_to = form.cleaned_data.get('date_to', None)

                interval = form.cleaned_data.get('interval', None)

                if not company and not ticker:
                    return render(request, 'manage/home.html', {'message': "Wrong form"})

                if (company or ticker) and (not date_from or not date_to):
                    return render(request, 'manage/home.html', {'message': "Wrong form"})

                if date_to and date_from and date_to < date_from and (company or ticker):
                    return render(request, 'manage/home.html', {'message': "Wrong form"})

                if company and not ticker:
                    ticker = company.ticker

                if ticker and date_from and date_to:
                    try:
                        error = parse_stooq_one_company(ticker, date_from, date_to, interval)
                        if error:
                            overlap = error.overlapping_data
                    except ParseError as e:
                        message = "Parse error: " + e.details
                        return render(request, 'manage/home.html', {'message': message})
                else:
                    return render(request, 'manage/home.html', {'message': "Wrong form"})

            else:
                date = form.cleaned_data.get('date', None)

                if not date:
                    return render(request, 'manage/home.html', {'message': "Wrong form"})

                try:
                    error = parse_stooq_all_companies(date)
                    if error:
                        overlap = error.overlapping_data
                except ParseError as e:
                    message = "Parse error: " + e.details
                    return render(request, 'manage/home.html', {'message': message})

            if error:
                return render(request, 'import/stooq.html',
                              {'form': StooqImportForm(),
                               "error": error,
                               "overlap": json.dumps(overlap)})

            return render(request, 'manage/home.html', {'message': "Parsed stooq.com data successfully"})
        else:
            return render(request, 'manage/home.html', {'message': "Wrong form"})
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
            intervals = {
                '-s': form.cleaned_data.get('chosen_interval_stooq', None),
                '-mv': form.cleaned_data.get('chosen_interval_gpw', None)
            }
            date_ranges_count = request.POST.get('date_ranges_count', None)

            statuses = []
            for index in range(int(date_ranges_count) + 1):
                start_date = form.cleaned_data.get('start_date_{index}'.format(index=index))
                end_date = form.cleaned_data.get('end_date_{index}'.format(index=index))

                if index == 0:
                    add_description = True
                else:
                    add_description = False

                if chosen_data != '-s' and chosen_data != '-mv':
                    statuses.append(export_methods.functions[chosen_data](chosen_companies, start_date, end_date,
                                                                          file_name, add_description))
                else:
                    chosen_interval = intervals[chosen_data]
                    statuses.append(export_methods.functions[chosen_data](chosen_companies, start_date, end_date,
                                                                          file_name, chosen_interval, add_description))

            success = [status for status in statuses if status is ExportStatus.SUCCESS]
            if len(success) >= 1:
                status = ExportStatus.SUCCESS
                if is_file_name_unique:
                    return render(request, 'manage/home.html', {'message': status.get_message(file_name)})
                else:
                    return render(request, 'manage/home.html',
                                  {'message': f'Passed file name exists. {status.get_message(file_name)}'})
            else:
                return render(request, 'manage/home.html', {'message': ExportStatus.FAILURE.get_message()})

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


# region grid_edition_views

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


class CompanyMergeView(BSModalFormView):
    template_name = 'manage/companies/merge.html'
    form_class = MergeForm
    success_message = 'Success: Companies were merged.'
    success_url = reverse_lazy('companies')

    def form_valid(self, form):
        self.merge_companies(form.cleaned_data)
        return super(CompanyMergeView, self).form_valid(form)

    def merge_companies(self, valid_data):
        chosen_from = valid_data.get('chosen_from').id
        chosen_to = valid_data.get('chosen_to').id
        merge_assets(chosen_from, chosen_to)
        merge_assets_categories(chosen_from, chosen_to)
        merge_equity_liabilities(chosen_from, chosen_to)
        merge_equity_liabilities_categories(chosen_from, chosen_to)
        merge_financial_ratios(chosen_from, chosen_to)
        merge_dupont_indicators(chosen_from, chosen_to)
        delete_from_assets(chosen_from)
        delete_from_assets_categories(chosen_from)
        delete_from_equity_liabilities(chosen_from)
        delete_from_equity_liabilities_categories(chosen_from)
        delete_from_financial_ratios(chosen_from)
        delete_from_dupont_indicators(chosen_from)
        delete_company(chosen_from)
        pass


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

# endregion
