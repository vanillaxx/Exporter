from django.shortcuts import render
import os.path
from common.Parsers import excel_parser, pdf_gpw_parser, stooq_parser, pdf_yearbook_parser, excel_yearbook_parser, \
    excel_gpw_parser
from common.Utils.Errors import UniqueError, ParseError
from common.Utils.parsing_result import ParsingResult
from ..forms import *
import json
from django.contrib import messages
from common.DAL.db_queries_get import get_existing_data_balance_sheet, get_existing_data_ratios, \
    get_existing_data_stock_quotes


def import_notoria(request):
    def is_excel_file(file_path):
        extension = os.path.splitext(file_path)[1]
        return extension == '.xls' or extension == '.xlsx'

    def render_overlapping_data_popup(chosen_sheet, sheet_shortcut, get_existing_data_func, request):
        for sheet in chosen_sheet:
            try:
                res = excel_parser.functions[sheet_shortcut](file_path, sheet, override=override, save=save)
            except UniqueError as e:
                for data in e.overlapping_data:
                    existing = get_existing_data_func(data)
                    data["exists"] = list(map(lambda x: list(x), existing))
                return e, None
            return [], res

    try:
        if request.method == 'POST':
            form = NotoriaImportForm(request.POST)
            if form.is_valid():
                file_path = request.POST.get('file_path', None)
                chosen_sheets_bs = form.cleaned_data.get('chosen_sheets_bs')
                chosen_sheets_fr = form.cleaned_data.get('chosen_sheets_fr')
                chosen_sheets_dp = form.cleaned_data.get('chosen_sheets_dp')
                directory_import = form.cleaned_data.get('directory_import')
                override = False
                save = False
                files_paths = []
                if directory_import:
                    if os.path.isdir(file_path):
                        override_save = form.cleaned_data.get('override_save')
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                if is_excel_file(file):
                                    absolute_path = os.path.join(root, file)
                                    files_paths.append(absolute_path)
                                else:
                                    messages.error(request,
                                                   "Directory must have only excel files from notoria.")
                                    return render(request, 'import/notoria.html', {'form': NotoriaImportForm()})
                            break
                        if override_save == 'o':
                            override = True
                            save = False
                        elif override_save == 's':
                            save = True
                            override = False
                    else:
                        messages.error(request,
                                       "Pass proper path to directory with Notoria excel files, e.g '/home/notoria")
                        return render(request, 'import/notoria.html', {'form': NotoriaImportForm()})
                else:
                    extension = os.path.splitext(file_path)[1]
                    if extension == '.xls' or extension == '.xlsx':
                        files_paths = [file_path]
                    else:
                        messages.error(request, "Pass proper path to Notoria excel files, e.g '/home/AGORA.xlsx'")
                        return render(request, 'import/notoria.html', {'form': NotoriaImportForm()})


                error_bs = []
                error_fr = []
                error_dp = []
                overlap_bs = []
                overlap_fr = []
                overlap_dp = []
                result_bs = None
                result_fr = None
                result_dp = None

                try:
                    for fp in files_paths:
                        file_path = fp.__str__()
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
                except ParseError as e:
                    messages.error(request, e)
                    return render(request, 'import/notoria.html', {'form': NotoriaImportForm()})
                except Exception as e:
                    print(e)
                    messages.error(request, "Error occurred while parsing. " + type(e).__name__ + ": " + str(e))
                    return render(request, 'import/notoria.html', {'form': NotoriaImportForm()})

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
            else:
                for field in form:
                    for err in field.errors:
                        messages.error(request, field.label + ": " + err)
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
