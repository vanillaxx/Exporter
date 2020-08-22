from django.shortcuts import render
from django.http import HttpResponse
from .forms import NotoriaImportForm, ExportForm, GpwImportForm, StooqImportForm
from common.Parsers import excel_parser, pdf_gpw_parser, stooq_parser, pdf_yearbook_parser, excel_yearbook_parser, \
    excel_gpw_parser
import common.Export.export as export_methods
from common.Utils.Errors import UniqueError
from .models import Company
from common.DAL.db_queries import replace_values, get_existing_data_balance_sheet
import json
def index(request):
    return render(request, 'index.html')


def import_notoria(request):
    if request.method == 'POST':
        form = NotoriaImportForm(request.POST)
        if form.is_valid():
            file_path = request.POST.get('file_path', None)
            chosen_sheets_bs = form.cleaned_data.get('chosen_sheets_bs')
            chosen_sheets_fr = form.cleaned_data.get('chosen_sheets_fr')
            chosen_sheets_dp = form.cleaned_data.get('chosen_sheets_dp')
            if chosen_sheets_bs:
                for sheet in chosen_sheets_bs:
                    try:
                        excel_parser.functions['bs'](file_path, sheet)
                    except UniqueError as e:
                        existing_data = []
                        for data in e.overlapping_data:
                            existing = get_existing_data_balance_sheet(data)
                            existing_without_id = list(map(lambda x: x[1:], existing))
                            existing_data.append(existing_without_id)
                        return render(request, 'import/notoria.html',
                                      {'form': form,
                                       "error": e,
                                       "overlap": json.dumps(e.overlapping_data),
                                       "exist": existing_data})
            if chosen_sheets_fr:
                for sheet in chosen_sheets_fr:
                    try:
                        excel_parser.functions['fr'](file_path, sheet)
                    except UniqueError as e:
                        return render(request, 'import/notoria.html',
                                      {'form': form,
                                       "error": e,
                                       "json_data": json.dumps(e.overlapping_data)})

            if chosen_sheets_dp:
                for sheet in chosen_sheets_dp:
                    try:
                        excel_parser.functions['dp'](file_path, sheet)
                    except UniqueError as e:
                        return render(request, 'import/notoria.html',
                                      {'form': form,
                                       "error": e,
                                       "json_data": json.dumps(e.overlapping_data)})
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
            print(form.cleaned_data)
            file_name = request.POST.get('file_name', None)
            chosen_data = request.POST.get('chosen_data', None)
            chosen_companies = list(form.cleaned_data.get('chosen_companies').values_list('id', flat=True))
            date_ranges_count = request.POST.get('date_ranges_count', None)
            for index in range(int(date_ranges_count) + 1):
                start_date = form.cleaned_data.get('start_date_{index}'.format(index=index))
                end_date = form.cleaned_data.get('end_date_{index}'.format(index=index))
                if index == 0:
                    export_methods.functions[chosen_data](chosen_companies, start_date, end_date, file_name)
                else:
                    export_methods.functions[chosen_data](chosen_companies, start_date, end_date, file_name,
                                                          add_description=False)
            return render(request, 'manage/home.html', {'message': "Data exported succsessfully"})
    else:
        form = ExportForm()

    return render(request, 'export/export.html', {'form': form})


def manage(request):
    return render(request, 'manage/home.html')


def get_companies(request):
    companies = Company.objects.all()
    return render(request, 'manage/companies.html', {'companies': companies})


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


