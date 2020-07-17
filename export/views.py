from django.shortcuts import render
from django.http import HttpResponse
from .models import NotoriaExportForm
import common.Export.export as export

def index(request):
    return HttpResponse("Here we will be able to export data to csv.")


def notoria(request):
    if request.method == 'POST':
        form = NotoriaExportForm(request.POST)
        if form.is_valid():
            file_name = request.POST.get('file_name', None)
            chosen_data = request.POST.get('chosen_data', None)
            chosen_companies = request.POST.get('chosen_companies', None)
            print(file_name, chosen_data, chosen_companies)
            export.functions[chosen_data](chosen_companies, file_name)
            return HttpResponse('Data exported successfully')
    else:
        form = NotoriaExportForm()

    return render(request, 'export/notoria.html', {'form': form})