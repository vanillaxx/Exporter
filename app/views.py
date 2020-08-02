from django.shortcuts import render
from django.http import HttpResponse
from .forms import NotoriaImportForm, NotoriaExportForm, GpwImportForm, StooqImportForm
from common.Parsers import excel_parser, pdf_gpw_parser, stooq_parser, pdf_yearbook_parser, excel_yearbook_parser, excel_gpw_parser
import common.Export.export as export
from common.Utils.Errors import CompanyNotFoundError
from datetime import datetime
from .models import Company


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
            period_end = form.cleaned_data.get('period_end')
            if chosen_sheets_bs:
                for sheet in chosen_sheets_bs:
                    excel_parser.functions['bs'](file_path, sheet)
            if chosen_sheets_fr:
                for sheet in chosen_sheets_fr:
                    excel_parser.functions['fr'](file_path, sheet)
            if chosen_sheets_dp:
                for sheet in chosen_sheets_dp:
                    excel_parser.functions['dp'](file_path, sheet)
            if period_end:
                try:
                    excel_parser.functions['gpw'](file_path, period_end)
                except CompanyNotFoundError as err:
                    return render(request, 'import/notoria.html', {'form': form, 'error': err})
            return HttpResponse('Parsed notoria successfully')
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

            if company and not ticker:
                ticker = company.ticker

            if ticker and date_from and date_to:
                SP.download_company(ticker, date_from, date_to, interval)

            if date:
                SP.download_all_companies(date)

            return HttpResponse('Parsed stooq successfully')

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
            return HttpResponse('Parsed GPW file successfully')
    else:
        form = GpwImportForm()

    return render(request, 'import/gpw.html', {'form': form})


def export_notoria(request):
    if request.method == 'POST':
        form = NotoriaExportForm(request.POST, count=request.POST.get('date_ranges_count'))
        if form.is_valid():
            print(form.cleaned_data)
            file_name = request.POST.get('file_name', None)
            chosen_data = request.POST.get('chosen_data', None)
            chosen_companies = list(form.cleaned_data.get('chosen_companies').values_list('id', flat=True))
            date_ranges_count = request.POST.get('date_ranges_count', None)
            for index in range(int(date_ranges_count)+1):
                start_date = form.cleaned_data.get('start_date_{index}'.format(index=index))
                end_date = form.cleaned_data.get('end_date_{index}'.format(index=index))
                if index == 0:
                    export.functions[chosen_data](chosen_companies, start_date, end_date, file_name)
                else:
                    export.functions[chosen_data](chosen_companies, start_date, end_date, file_name,
                                                  add_description=False)
            return HttpResponse('Data exported successfully')
    else:
        form = NotoriaExportForm()

    return render(request, 'export/notoria.html', {'form': form})


def manage(request):
    return render(request, 'manage/home.html')


def get_companies(request):
    companies = Company.objects.all()
    return render(request, 'manage/companies.html', {'companies': companies})
