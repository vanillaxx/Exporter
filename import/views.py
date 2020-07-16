from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import FilePath
from common.Parsers import excel_parser


def index(request):
    return HttpResponse("Here we will be able to import data to database.")

def balance_sheet(request):
    if request.method == 'POST':
        form = FilePath(request.POST)
        if form.is_valid():
            EP = excel_parser.ExcelParser()
            file_path = request.POST.get('file_path', None)
            EP.parse_balance_sheet(file_path, 'QS')
            return HttpResponse('Parsed balance sheet successfully')
    else:
        form = FilePath()

    return render(request, 'import/balance_sheet.html', {'form': form})
