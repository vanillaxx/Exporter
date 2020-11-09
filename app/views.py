from collections import deque
from datetime import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
import common.Export.export as export_methods
from common.Parsers import excel_parser, pdf_gpw_parser, stooq_parser, pdf_yearbook_parser, excel_yearbook_parser, \
    excel_gpw_parser
from common.Utils.Errors import UniqueError, ParseError, DatabaseImportError
from common.Utils.export_status import ExportStatus
from common.Utils.parsing_result import ParsingResult
from common.Utils.unification_info import UnificationInfo
from .forms import *
from .models import *
import json
import os.path
from django.contrib import messages
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalFormView
from common.DAL.db_queries_get import get_existing_data_balance_sheet, get_existing_data_ratios, \
    get_existing_data_stock_quotes, get_existing_data_financial_ratios, get_existing_data_dupont_indicators
from common.DAL.db_queries_merge import merge_assets, merge_assets_categories, merge_dupont_indicators, \
    merge_equity_liabilities_categories, merge_equity_liabilities, merge_financial_ratios
from common.DAL.db_queries_delete import delete_from_assets, delete_from_assets_categories,\
    delete_from_dupont_indicators, delete_from_equity_liabilities, delete_from_equity_liabilities_categories,\
    delete_from_financial_ratios, delete_company, delete_from_stock_quotes
from common.DAL.db_queries_insert import insert_company, replace_values
from common.DAL.db_queries_merge import merge_database, merge_stock_quotes
from shutil import copyfile


def index(request):
    return render(request, 'index.html')


def error(request):
    return render(request, 'error.html')


def import_notoria(request):
    def render_overlapping_data_popup(chosen_sheet, sheet_shortcut, get_existing_data_func, request):
        for sheet in chosen_sheet:
            try:
                res = excel_parser.functions[sheet_shortcut](file_path, sheet)
            except UniqueError as e:
                for data in e.overlapping_data:
                    existing = get_existing_data_func(data)
                    data["exists"] = list(map(lambda x: list(x), existing))
                return e, None
            except ParseError as e:
                messages.error(request, e)
                return render(request, 'import/notoria.html', {'form': NotoriaImportForm()})
            except Exception as e:
                messages.error(request, "Error occurred while parsing. " + type(e).__name__ + ": " + str(e))
                return render(request, 'import/notoria.html', {'form': NotoriaImportForm()})
            return [], res

    try:
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
                result_bs = None
                result_fr = None
                result_dp = None

                if chosen_sheets_bs:
                    error_bs, result_bs = render_overlapping_data_popup(chosen_sheets_bs, 'bs',
                                                                        get_existing_data_balance_sheet, request)
                    if error_bs:
                        overlap_bs = error_bs.overlapping_data

                if chosen_sheets_fr:
                    error_fr, result_fr = render_overlapping_data_popup(chosen_sheets_fr, 'fr',
                                                                        get_existing_data_ratios, request)
                    if error_fr:
                        overlap_fr = error_fr.overlapping_data

                if chosen_sheets_dp:
                    error_dp, result_dp = render_overlapping_data_popup(chosen_sheets_dp, 'dp',
                                                                        get_existing_data_ratios, request)
                    if error_dp:
                        overlap_dp = error_dp.overlapping_data

                if error_bs or error_fr or error_dp:
                    messages.success(request, "Parsed notoria successfully.")
                    return render(request, 'import/notoria.html',
                                  {'form': form,
                                   "error_bs": error_bs,
                                   "error_fr": error_fr,
                                   "error_dp": error_dp,
                                   "overlap_bs": json.dumps(overlap_bs),
                                   "overlap_fr": json.dumps(overlap_fr),
                                   "overlap_dp": json.dumps(overlap_dp)})

                result = ParsingResult.combine_notoria_results(result_bs, result_dp, result_fr)
                if result is not None:
                    messages.success(request, "Parsed notoria successfully")
                    return render(request, 'import/notoria.html', {'form': NotoriaImportForm(),
                                                                   'unification_form':
                                                                       UnificationForm(unification=result.unification_info),
                                                                   'unification': result.to_json()})

                messages.success(request, "Parsed notoria successfully")
                return render(request, 'import/notoria.html', {'form': NotoriaImportForm()})

        return render(request, 'import/notoria.html', {'form': NotoriaImportForm()})
    except:
        return render(request, 'error.html')


def import_stooq(request):
    def parse_stooq_one_company(ticker_arg, date_from_arg, date_to_arg, interval_arg):
        SP = stooq_parser.StooqParser()
        try:
            res = SP.download_company(ticker_arg, date_from_arg, date_to_arg, interval_arg)
        except UniqueError as e:
            for data in e.overlapping_data:
                existing = get_existing_data_stock_quotes(data)
                data["exists"] = list(map(lambda x: list(x), existing))
            return e, None
        except ParseError as pe:
            raise pe
        return None, res

    def parse_stooq_all_companies(date_arg):
        SP = stooq_parser.StooqParser()
        try:
            res = SP.download_all_companies(date_arg)
        except UniqueError as e:
            for data in e.overlapping_data:
                existing = get_existing_data_stock_quotes(data)
                data["exists"] = list(map(lambda x: list(x), existing))
            return e, None
        except ParseError as pe:
            raise pe
        return None, res

    try:
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

                    wrong_form = False
                    if not company and not ticker:
                        messages.warning(request, "Wrong form: no company or ticker is provided.")
                        wrong_form = True

                    if not date_from or not date_to:
                        messages.warning(request, "Wrong form: no date from or to is provided.")
                        wrong_form = True

                    if date_from and date_to and date_to < date_from:
                        messages.warning(request, "Wrong form: date from is larger then date to.")
                        wrong_form = True

                    if wrong_form:
                        return render(request, 'import/stooq.html', {'form': form})

                    if company:
                        ticker = company.ticker

                    if ticker and date_from and date_to:
                        try:
                            error, result = parse_stooq_one_company(ticker, date_from, date_to, interval)
                            if error:
                                overlap = error.overlapping_data
                        except ParseError as e:
                            messages.error(request, e)
                            return render(request, 'import/stooq.html', {'form': StooqImportForm()})
                        except Exception as e:
                            messages.error(request, "Error occurred while parsing. " + type(e).__name__ + ": "+ str(e))
                            return render(request, 'import/stooq.html', {'form': StooqImportForm()})
                    else:
                        messages.warning(request, "Wrong form.")
                        return render(request, 'import/stooq.html', {'form': form})

                else:
                    date = form.cleaned_data.get('date', None)

                    if not date:
                        messages.warning(request, "Wrong form: no date is provided.")
                        return render(request, 'import/stooq.html', {'form': form})

                    try:
                        error, result = parse_stooq_all_companies(date)
                        if error:
                            overlap = error.overlapping_data
                    except ParseError as e:
                        messages.error(request, e)
                        return render(request, 'import/stooq.html', {'form': StooqImportForm()})
                    except Exception as e:
                        messages.error(request, "Error occurred while parsing. " + type(e).__name__ + ": "+ str(e))
                        return render(request, 'import/stooq.html', {'form': StooqImportForm()})

                if error:
                    return render(request, 'import/stooq.html',
                                  {'form': StooqImportForm(),
                                   "error": error,
                                   "overlap": json.dumps(overlap)})
                if result is not None:
                    return render(request, 'import/stooq.html', {'form': StooqImportForm(),
                                                                 'unification_form':
                                                                     UnificationForm(unification=result.unification_info),
                                                                 'unification': result.to_json()})

                messages.success(request, "Parsed stooq.com data successfully.")
                return render(request, 'import/stooq.html', {'form': StooqImportForm()})
            else:
                messages.warning(request, "Wrong form.")
                return render(request, 'import/stooq.html', {'form': form})

        return render(request, 'import/stooq.html', {'form': StooqImportForm()})
    except Exception as e:
        return render(request, 'error.html')


def import_gpw(request):
    parsers = {
        'yearbook_excel': excel_yearbook_parser.ExcelYearbookParser,
        'yearbook_pdf': pdf_yearbook_parser.PdfYearbookParser,
        'statistics_excel': excel_gpw_parser.ExcelGPWParser,
        'statistics_pdf': pdf_gpw_parser.PdfGPWParser
    }

    try:
        if request.method == 'POST':
            form = GpwImportForm(request.POST)
            if form.is_valid():
                path = form.cleaned_data['path']
                file_type = form.cleaned_data['file_type']
                parser = parsers[file_type]()
                try:
                    result = parser.parse(path)
                except UniqueError as e:
                    def remove_name(l):
                        new_l = l.copy()
                        new_l.pop(1)
                        return new_l

                    overlapping = e.overlapping_data[0].copy()
                    overlapping['columns'] = overlapping['columns'].copy()
                    overlapping['values'] = overlapping['values'].copy()

                    overlapping['columns'].pop(1)
                    overlapping['values'] = list(map(remove_name, overlapping['values']))

                    messages.success(request, 'Parsed GPW file successfully.')
                    return render(request, 'import/gpw.html',
                                  {'form': GpwImportForm(),
                                   'overlapping': e.overlapping_data[0],
                                   'data': json.dumps([overlapping])})
                except ParseError as e:
                    messages.error(request, e)
                    return render(request, 'import/gpw.html', {'form': GpwImportForm()})
                except Exception as e:
                    messages.error(request, "Error occurred while parsing. " + type(e).__name__ + ": " + str(e))
                    return render(request, 'import/gpw.html', {'form': GpwImportForm()})

                if result is not None:
                    messages.success(request, 'Parsed GPW file successfully.')
                    return render(request, 'import/gpw.html', {'form': GpwImportForm(),
                                                               'unification_form':
                                                                   UnificationForm(unification=result.unification_info),
                                                               'unification': result.to_json()})

                messages.success(request, 'Parsed GPW file successfully.')
                return render(request, 'import/gpw.html', {'form': GpwImportForm()})
        else:
            form = GpwImportForm()

        return render(request, 'import/gpw.html', {'form': form})
    except:
        return render(request, 'error.html')


def export(request):
    try:
        if request.method == 'POST':
            form = ExportForm(request.POST, count=request.POST.get('date_ranges_count'))
            if form.is_valid():
                file_name = request.POST.get('file_name', None)
                if not file_name.endswith(".csv"):
                    file_name += ".csv"
                if os.path.isfile(file_name):
                    messages.error(request, 'File with that name already exists.')
                    return render(request, 'export/export.html', {'form': form})

                chosen_data = request.POST.get('chosen_data', None)
                chosen_companies = list(form.cleaned_data.get('chosen_companies').values_list('id', flat=True))
                intervals = {
                    '-f': form.cleaned_data.get('chosen_interval_ratios', None),
                    '-d': form.cleaned_data.get('chosen_interval_ratios', None),
                    '-s': form.cleaned_data.get('chosen_interval_stooq', None),
                    '-mv': form.cleaned_data.get('chosen_interval_gpw', None)
                }
                balance_sheet_intervals = ['-da', '-ca', '-fa', '-de', '-ce', '-fe']
                for i in balance_sheet_intervals:
                    intervals[i] = form.cleaned_data.get('chosen_interval_balance', None)

                date_ranges_count = request.POST.get('date_ranges_count', None)

                statuses = []
                for index in range(int(date_ranges_count) + 1):
                    start_date = form.cleaned_data.get('start_date_{index}'.format(index=index))
                    end_date = form.cleaned_data.get('end_date_{index}'.format(index=index))

                    if index == 0:
                        add_description = True
                    else:
                        add_description = False

                    chosen_interval = intervals[chosen_data]
                    statuses.append(export_methods.functions[chosen_data](chosen_companies, start_date, end_date,
                                                                          file_name, chosen_interval, add_description))

                success = [status for status in statuses if status is ExportStatus.SUCCESS]
                if len(success) >= 1:
                    messages.success(request, ExportStatus.SUCCESS.get_message(file_name))
                    return render(request, 'export/export.html', {'form': ExportForm()})
                else:
                    messages.success(request, ExportStatus.FAILURE.get_message(file_name))
                    return render(request, 'export/export.html', {'form': ExportForm()})

        else:
            form = ExportForm()

        return render(request, 'export/export.html', {'form': form})
    except:
        return render(request, 'error.html')


def export_database(request):
    def copy_database_to_folder(path):
        if not os.path.isdir(path):
            return False

        destination = os.path.join(path, 'exporter.db')
        copyfile('exporter.db', destination)
        return True

    try:
        if request.method == 'POST':
            form = ExportDatabaseForm(request.POST)
            if form.is_valid():
                folder = form.cleaned_data['folder']
                delete = form.cleaned_data['delete']

                copied_properly = copy_database_to_folder(folder)
                if delete:
                    _delete_all_info_from_database()

                if not copied_properly:
                    messages.error(request, 'Cannot export database.')
                    return render(request, 'manage/databaseExport.html', {'form': form})
                else:
                    messages.success(request, 'Database exported successfully.')
                    return render(request, 'manage/databaseExport.html', {'form': ExportDatabaseForm()})

        return render(request, 'manage/databaseExport.html', {'form': ExportDatabaseForm()})
    except:
        return render(request, 'error.html')


def import_database(request):
    def is_sqlite3(filename):
        from os.path import isfile, getsize

        if not isfile(filename):
            return False
        if getsize(filename) < 100:
            return False

        with open(filename, 'rb') as fd:
            header = fd.read(100)
        return header[:16] == b'SQLite format 3\x00' or header[:16] == 'SQLite format 3\x00'

    def is_properly_database(path):
        return is_sqlite3(path)

    try:
        if request.method == 'POST':
            form = ImportDatabaseForm(request.POST)
            if form.is_valid():
                file = form.cleaned_data['file']

                if not is_properly_database(file):
                    messages.error(request, 'Chosen file is not of properly SQLite3 file type.')
                    return render(request, 'manage/databaseExport.html', {'form': form})

                if not _is_database_empty():
                    return render(request, 'manage/databaseImport.html',
                                  {'form': ImportDatabaseForm(),
                                   'path': file.replace('\\', '\\\\')})

                merge_database(file)

                messages.success(request, 'Database imported successfully.')
                return render(request, 'manage/databaseImport.html', {'form': ImportDatabaseForm()})

        return render(request, 'manage/databaseImport.html', {'form': ImportDatabaseForm()})
    except:
        return render(request, 'error.html')


def manage(request):
    return render(request, 'manage/home.html')


def replace_data(request):
    data = request.POST.get('data', '')
    json_data = json.loads(data)
    for data_to_replace in json_data:
        table_name = data_to_replace['table_name']
        columns = data_to_replace['columns']
        values = data_to_replace['values']
        existing_company_id = data_to_replace["exists"][0][0]
        for value in values:
            listed_value = list(value)
            listed_value[0] = existing_company_id
            replace_values(table_name, columns, listed_value)
    return HttpResponse({'message': "Data replaced successfully."})


def replace_data_multiple(request):
    data = request.POST.get('data')
    json_data = json.loads(data)
    for data_to_replace in json_data:
        table_name = data_to_replace['table_name']
        columns = data_to_replace['columns']
        values = data_to_replace['values']
        for value in values:
            replace_values(table_name, columns, value)
    return HttpResponse({'message': "Data replaced successfully"})


def replace_database(request):
    path = request.POST.get('path')
    _delete_all_info_from_database()
    try:
        merge_database(path)
    except DatabaseImportError as e:
        messages.error(request, e)
        return HttpResponse(e)

    messages.success(request, "Database imported successfully.")
    return HttpResponse("Database imported successfully.")


def insert_data(request):
    if request.method == 'POST':
        data_json = request.POST.get('unification')
        data = json.loads(data_json)
        data_type = None

        for ind, data_to_insert in enumerate(data):
            company_id = request.POST.get(f'company_choices_{ind}', None)
            ui = UnificationInfo.from_json(data_to_insert)

            if company_id is None:
                company_id = insert_company(ui.company)
            else:
                company_id = json.loads(company_id)

            ui.insert_data_to_db(company_id)

            if data_type is None:
                data_type = ui.get_data_type()

        return render(request, 'manage/home.html',
                      {'message': f'Parsed {data_type} successfully. Chosen companies unified'})

    return render(request, 'base.html')


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
        balance_was_same = False
        fr_was_same = False
        dp_was_same = False

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
                fr_was_same = True
            elif indexes and model is DuPontIndicators:
                dp_was_same = True

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
            stock_quotes_values = StockQuotes.objects.filter(company_id=chosen_to,
                                                             date__in=overlapping_stock_quotes.values("date"),
                                                             interval__in=overlapping_stock_quotes
                                                             .values("interval")).values_list(flat=True)

            values = list(map(lambda x: list(x.values())[1:], overlapping_stock_quotes.values_list(flat=True)
                              .values()))
            exists = list(map(lambda x: list(x.values())[1:], stock_quotes_values.values()))
            stock_quotes_dict = {"table_name": StockQuotes.objects.model._meta.db_table,
                                 "columns": [f.get_attname_column()[1] for f in
                                             StockQuotes._meta.get_fields() if f.name != 'id'],
                                 "values": values,
                                 "exists": exists}
            overlapping_balance_data.append(stock_quotes_dict)

        if overlapping_balance_data or overlapping_financial_ratios_data or overlapping_dupont_indicators_data:
            error_bs = []
            error_fr = []
            error_dp = []
            overlap_bs = []
            overlap_fr = []
            overlap_dp = []
            if overlapping_balance_data:
                error_bs = UniqueError(*overlapping_balance_data)
                overlap_bs = json.dumps(error_bs.overlapping_data, default=str)
            if overlapping_financial_ratios_data:
                error_fr = UniqueError(*overlapping_financial_ratios_data)
                overlap_fr = json.dumps(error_fr.overlapping_data, default=str)
            if overlapping_dupont_indicators_data:
                error_dp = UniqueError(*overlapping_dupont_indicators_data)
                overlap_dp = json.dumps(error_dp.overlapping_data, default=str)
            return render(self.request, 'manage/home.html',
                          {"company_to_delete_id": chosen_from,
                           "error_bs": error_bs,
                           "overlap_bs": overlap_bs,
                           "error_fr": error_fr,
                           "overlap_fr": overlap_fr,
                           "error_dp": error_dp,
                           "overlap_dp": overlap_dp})
        else:
            if balance_was_same:
                delete_from_assets(chosen_from)
                delete_from_assets_categories(chosen_from)
                delete_from_equity_liabilities(chosen_from)
                delete_from_equity_liabilities_categories(chosen_from)
                delete_from_stock_quotes(chosen_from)
            if fr_was_same:
                delete_from_financial_ratios(chosen_from)
            if dp_was_same:
                delete_from_dupont_indicators(chosen_from)

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

# region database_private_methods


def _is_database_empty():
    return Company.objects.all().count() == 0 and \
           EkdClass.objects.all().count() == 0 and \
           EkdSection.objects.all().count() == 0 and \
           Assets.objects.all().count() == 0 and \
           AssetsCategories.objects.all().count() == 0 and \
           DuPontIndicators.objects.all().count() == 0 and \
           EkdClass.objects.all().count() == 0 and \
           EkdSection.objects.all().count() == 0 and \
           EquityLiabilities.objects.all().count() == 0 and \
           EquityLiabilitiesCategories.objects.all().count() == 0 and \
           FinancialRatios.objects.all().count() == 0 and \
           MarketValues.objects.all().count() == 0 and \
           StockQuotes.objects.all().count() == 0


def _delete_all_info_from_database():
    Company.objects.all().delete()
    EkdClass.objects.all().delete()
    EkdSection.objects.all().delete()
    Assets.objects.all().delete()
    AssetsCategories.objects.all().delete()
    DuPontIndicators.objects.all().delete()
    EkdClass.objects.all().delete()
    EkdSection.objects.all().delete()
    EquityLiabilities.objects.all().delete()
    EquityLiabilitiesCategories.objects.all().delete()
    FinancialRatios.objects.all().delete()
    MarketValues.objects.all().delete()
    StockQuotes.objects.all().delete()


# endregion

# region grid_edition_views


class CompanyView(generic.ListView):
    model = Company
    context_object_name = 'companies'
    template_name = 'manage/companies.html'


class CompanyCreateView(BSModalCreateView):
    template_name = 'manage/companies/create.html'
    form_class = CompanyModelForm
    success_message = 'Company was created.'
    success_url = reverse_lazy('companies')


class CompanyUpdateView(BSModalUpdateView):
    model = Company
    template_name = 'manage/companies/update.html'
    form_class = CompanyModelForm
    success_message = 'Company was updated.'
    success_url = reverse_lazy('companies')


class CompanyDeleteView(BSModalDeleteView):
    model = Company
    template_name = 'manage/companies/delete.html'
    success_message = 'Company was deleted.'
    success_url = reverse_lazy('companies')


class AssetsView(generic.ListView):
    model = Assets
    context_object_name = 'assets'
    template_name = 'manage/assets.html'


class AssetsCreateView(BSModalCreateView):
    template_name = 'manage/assets/create.html'
    form_class = AssetsModelForm
    success_message = 'Assets was created.'
    success_url = reverse_lazy('assets')


class AssetsUpdateView(BSModalUpdateView):
    model = Assets
    template_name = 'manage/assets/update.html'
    form_class = AssetsModelForm
    success_message = 'Assets was updated.'
    success_url = reverse_lazy('assets')


class AssetsDeleteView(BSModalDeleteView):
    model = Assets
    template_name = 'manage/assets/delete.html'
    success_message = 'Assets was deleted.'
    success_url = reverse_lazy('assets')


class AssetsCategoryView(generic.ListView):
    model = AssetsCategories
    context_object_name = 'assets_categories'
    template_name = 'manage/assetsCategories.html'


class AssetsCategoryCreateView(BSModalCreateView):
    template_name = 'manage/assetsCategories/create.html'
    form_class = AssetsCategoryModelForm
    success_message = 'Assets category was created.'
    success_url = reverse_lazy('assets_categories')


class AssetsCategoryUpdateView(BSModalUpdateView):
    model = AssetsCategories
    template_name = 'manage/assetsCategories/update.html'
    form_class = AssetsCategoryModelForm
    success_message = 'Assets category was updated.'
    success_url = reverse_lazy('assets_categories')


class AssetsCategoryDeleteView(BSModalDeleteView):
    model = AssetsCategories
    template_name = 'manage/assetsCategories/delete.html'
    success_message = 'Assets category was deleted.'
    success_url = reverse_lazy('assets_categories')


class DuPontIndicatorView(generic.ListView):
    model = DuPontIndicators
    context_object_name = 'indicators'
    template_name = 'manage/duPont.html'


class DuPontIndicatorCreateView(BSModalCreateView):
    template_name = 'manage/duPont/create.html'
    form_class = DuPointIndicatorModelForm
    success_message = 'DuPont indicator was created.'
    success_url = reverse_lazy('dupont')


class DuPontIndicatorUpdateView(BSModalUpdateView):
    model = DuPontIndicators
    template_name = 'manage/duPont/update.html'
    form_class = DuPointIndicatorModelForm
    success_message = 'DuPont indicator was updated.'
    success_url = reverse_lazy('dupont')


class DuPontIndicatorDeleteView(BSModalDeleteView):
    model = DuPontIndicators
    template_name = 'manage/duPont/delete.html'
    success_message = 'DuPont indicator was deleted.'
    success_url = reverse_lazy('dupont')


class EkdClassView(generic.ListView):
    model = EkdClass
    context_object_name = 'classes'
    template_name = 'manage/ekdClasses.html'


class EkdClassCreateView(BSModalCreateView):
    template_name = 'manage/ekdClasses/create.html'
    form_class = EkdClassModelForm
    success_message = 'EKD class was created.'
    success_url = reverse_lazy('ekd_classes')


class EkdClassUpdateView(BSModalUpdateView):
    model = EkdClass
    template_name = 'manage/ekdClasses/update.html'
    form_class = EkdClassModelForm
    success_message = 'EKD class was updated.'
    success_url = reverse_lazy('ekd_classes')


class EkdClassDeleteView(BSModalDeleteView):
    model = EkdClass
    template_name = 'manage/ekdClasses/delete.html'
    success_message = 'EKD class was deleted.'
    success_url = reverse_lazy('ekd_classes')


class EkdSectionView(generic.ListView):
    model = EkdSection
    context_object_name = 'sections'
    template_name = 'manage/ekdSections.html'


class EkdSectionCreateView(BSModalCreateView):
    template_name = 'manage/ekdSections/create.html'
    form_class = EkdSectionModelForm
    success_message = 'EKD section was created.'
    success_url = reverse_lazy('ekd_sections')


class EkdSectionUpdateView(BSModalUpdateView):
    model = EkdSection
    template_name = 'manage/ekdSections/update.html'
    form_class = EkdSectionModelForm
    success_message = 'EKD section was updated.'
    success_url = reverse_lazy('ekd_sections')


class EkdSectionDeleteView(BSModalDeleteView):
    model = EkdSection
    template_name = 'manage/ekdSections/delete.html'
    success_message = 'EKD section was deleted.'
    success_url = reverse_lazy('ekd_sections')


class EquityLiabilitiesView(generic.ListView):
    model = EquityLiabilities
    context_object_name = 'liabilities'
    template_name = 'manage/equityLiabilities.html'


class EquityLiabilitiesCreateView(BSModalCreateView):
    template_name = 'manage/equityLiabilities/create.html'
    form_class = EquityLiabilitiesModelForm
    success_message = 'Equity Liabilities was created.'
    success_url = reverse_lazy('equity_liabilities')


class EquityLiabilitiesUpdateView(BSModalUpdateView):
    model = EquityLiabilities
    template_name = 'manage/equityLiabilities/update.html'
    form_class = EquityLiabilitiesModelForm
    success_message = 'EquityLiabilities was updated.'
    success_url = reverse_lazy('equity_liabilities')


class EquityLiabilitiesDeleteView(BSModalDeleteView):
    model = EquityLiabilities
    template_name = 'manage/equityLiabilities/delete.html'
    success_message = 'EquityLiabilities was deleted.'
    success_url = reverse_lazy('equity_liabilities')


class EquityLiabilitiesCategoryView(generic.ListView):
    model = EquityLiabilitiesCategories
    context_object_name = 'liabilities_categories'
    template_name = 'manage/equityLiabilitiesCategories.html'


class EquityLiabilitiesCategoryCreateView(BSModalCreateView):
    template_name = 'manage/equityLiabilitiesCategories/create.html'
    form_class = EquityLiabilitiesCategoryModelForm
    success_message = 'Equity liabilities category was created.'
    success_url = reverse_lazy('equity_liabilities_categories')


class EquityLiabilitiesCategoryUpdateView(BSModalUpdateView):
    model = EquityLiabilitiesCategories
    template_name = 'manage/equityLiabilitiesCategories/update.html'
    form_class = EquityLiabilitiesCategoryModelForm
    success_message = 'Equity liabilities category was updated.'
    success_url = reverse_lazy('equity_liabilities_categories')


class EquityLiabilitiesCategoryDeleteView(BSModalDeleteView):
    model = EquityLiabilitiesCategories
    template_name = 'manage/equityLiabilitiesCategories/delete.html'
    success_message = 'Equity liabilities category was deleted.'
    success_url = reverse_lazy('equity_liabilities_categories')


class FinancialRatiosView(generic.ListView):
    model = FinancialRatios
    context_object_name = 'ratios'
    template_name = 'manage/financial.html'


class FinancialRatiosCreateView(BSModalCreateView):
    template_name = 'manage/financial/create.html'
    form_class = FinancialRatiosModelForm
    success_message = 'Financial ratios was created.'
    success_url = reverse_lazy('financial')


class FinancialRatiosUpdateView(BSModalUpdateView):
    model = FinancialRatios
    template_name = 'manage/financial/update.html'
    form_class = FinancialRatiosModelForm
    success_message = 'Financial ratios was updated.'
    success_url = reverse_lazy('financial')


class FinancialRatiosDeleteView(BSModalDeleteView):
    model = FinancialRatios
    template_name = 'manage/financial/delete.html'
    success_message = 'Financial ratios was deleted.'
    success_url = reverse_lazy('financial')


class MarketValueView(generic.ListView):
    model = MarketValues
    context_object_name = 'values'
    template_name = 'manage/market.html'


class MarketValueCreateView(BSModalCreateView):
    template_name = 'manage/market/create.html'
    form_class = MarketValuesModelForm
    success_message = 'Market value was created.'
    success_url = reverse_lazy('market')


class MarketValueUpdateView(BSModalUpdateView):
    model = MarketValues
    template_name = 'manage/market/update.html'
    form_class = MarketValuesModelForm
    success_message = 'Market value was updated.'
    success_url = reverse_lazy('market')


class MarketValueDeleteView(BSModalDeleteView):
    model = MarketValues
    template_name = 'manage/market/delete.html'
    success_message = 'Market value was deleted.'
    success_url = reverse_lazy('market')


class StockQuoteView(generic.ListView):
    model = StockQuotes
    context_object_name = 'stock'
    template_name = 'manage/stock.html'


class StockQuoteCreateView(BSModalCreateView):
    template_name = 'manage/stock/create.html'
    form_class = StockQuotesModelForm
    success_message = 'Stock quote was created.'
    success_url = reverse_lazy('stock')


class StockQuoteUpdateView(BSModalUpdateView):
    model = StockQuotes
    template_name = 'manage/stock/update.html'
    form_class = StockQuotesModelForm
    success_message = 'Stock quote was updated.'
    success_url = reverse_lazy('stock')


class StockQuoteDeleteView(BSModalDeleteView):
    model = StockQuotes
    template_name = 'manage/stock/delete.html'
    success_message = 'Stock quote was deleted.'
    success_url = reverse_lazy('stock')

# endregion
