from django.http import HttpResponse
from django.shortcuts import render

from common.DAL.db_queries_get import update_company
from common.Utils.unification_info import UnificationInfo
import json
from common.DAL.db_queries_insert import insert_company, replace_values


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
                update_company(company_id, ui.company)

            ui.insert_data_to_db(company_id)

            if data_type is None:
                data_type = ui.get_data_type()

        return render(request, 'manage/home.html',
                      {'message': f'Parsed {data_type} successfully. Chosen companies unified'})

    return render(request, 'base.html')
