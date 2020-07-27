from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import NotoriaImportForm, NotoriaExportForm
from common.Parsers import excel_parser
import common.Export.export as export
from common.Utils.Errors import CompanyNotFoundError


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
        form = NotoriaImportForm(request.POST)
        if form.is_valid():
            EP = excel_parser.ExcelParser()
            file_path = request.POST.get('file_path', None)
            EP.parse_balance_sheet(file_path, 'QS')
            return HttpResponse('Parsed notoria successfully')
    else:
        form = NotoriaImportForm()

    return render(request, 'import/stooq.html', {'form': form})


def export_notoria(request):
    if request.method == 'POST':
        form = NotoriaExportForm(request.POST)
        if form.is_valid():
            file_name = request.POST.get('file_name', None)
            chosen_data = request.POST.get('chosen_data', None)
            chosen_companies = form.cleaned_data.get('chosen_companies')
            print(chosen_companies)
            for company in chosen_companies:
                export.functions[chosen_data](company.id, file_name)
            return HttpResponse('Data exported successfully')
    else:
        form = NotoriaExportForm()

    return render(request, 'export/notoria.html', {'form': form})