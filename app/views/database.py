from django.shortcuts import render
from django.http import HttpResponse
from common.Utils.Errors import DatabaseImportError
from ..forms import *
import os.path
from django.contrib import messages
from common.DAL.db_queries_merge import merge_database
from shutil import copyfile


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
