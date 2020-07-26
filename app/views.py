from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import NotoriaImportForm, NotoriaExportForm, GpwImportForm
from common.Parsers import excel_parser, pdf_gpw_parser, pdf_yearbook_parser
import common.Export.export as export


def index(request):
    return render(request, 'index.html')


def import_notoria(request):
    if request.method == 'POST':
        form = NotoriaImportForm(request.POST)
        if form.is_valid():
            EP = excel_parser.ExcelParser()
            file_path = request.POST.get('file_path', None)
            EP.parse_balance_sheet(file_path, 'QS')
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


def import_gpw(request):
    parsers = {
        'yearbook_excel': pdf_yearbook_parser.PdfYearbookParser,
        'yearbook_pdf': pdf_yearbook_parser.PdfYearbookParser,
        'statistics_excel': excel_parser.ExcelParser,
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
