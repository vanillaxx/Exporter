from django.http import HttpResponse
from django.shortcuts import render

from app.forms import GpwImportForm, StooqImportForm, NotoriaImportForm
from common.DAL.db_queries_get import update_company, get_existing_data_stock_quotes, get_existing_data_balance_sheet, \
    get_existing_financial_ratios_for_parsed_file, get_existing_dupont_indicators_for_parsed_file
from common.Utils.Errors import UniqueError
from common.Utils.gpw_utils import copy_and_remove_name_from_overlapping_info
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

        overlapping_data_json = request.POST.get('overlapping', json.dumps({}))
        overlapping_data = json.loads(overlapping_data_json)

        new_overlapping_data = [overlapping_data]
        data_type = None

        for ind, data_to_insert in enumerate(data):
            company = request.POST.get(f'company_choices_{ind}', None)
            ui = UnificationInfo.from_json(data_to_insert)

            if company is None:
                company_id = insert_company(ui.company)
                company_name = ui.company.name
            else:
                company_id, company_name = json.loads(company)
                update_company(company_id, ui.company)
                # company_name = ui.company.name

            ui.insert_data_to_db(new_overlapping_data, company_id, company_name)

            if data_type is None:
                data_type = ui.data_type, ui.get_data_type()

        if new_overlapping_data and new_overlapping_data[0]:
            render_response = {
                'notoria': __render_response_for_notoria,
                'stooq': __render_response_for_stooq,
                'gpw': __render_response_for_gpw
            }
            return render_response[data_type[0]](request, new_overlapping_data)
        else:
            return render(request, 'manage/home.html',
                          {'message': f'Parsed {data_type[1]} successfully. Chosen companies unified'})

    return render(request, 'base.html')


def __render_response_for_gpw(request, overlapping):
    overlapping_data = copy_and_remove_name_from_overlapping_info(overlapping[0])

    return render(request, 'import/gpw.html',
                  {'form': GpwImportForm(),
                   'overlapping': overlapping[0],
                   'data': json.dumps([overlapping_data])})


def __render_response_for_stooq(request, overlapping):
    for data in overlapping:
        existing = get_existing_data_stock_quotes(data)
        data['exists'] = list(map(lambda x: list(x), existing))

    return render(request, 'import/stooq.html',
                  {'form': StooqImportForm(),
                   'error': UniqueError(overlapping[0]),
                   'overlap': json.dumps(overlapping)})


def __render_response_for_notoria(request, overlapping):
    overlap_bs = []
    overlap_fr = []
    overlap_dp = []

    get_existing_data_func_and_overlap = {
        'Assets': (get_existing_data_balance_sheet, overlap_bs),
        'EquityLiabilities': (get_existing_data_balance_sheet, overlap_bs),
        'AssetsCategories': (get_existing_data_balance_sheet, overlap_bs),
        'EquityLiabilitiesCategories': (get_existing_data_balance_sheet, overlap_bs),
        'FinancialRatios': (get_existing_financial_ratios_for_parsed_file, overlap_fr),
        'DuPontIndicators': (get_existing_dupont_indicators_for_parsed_file, overlap_dp)
    }

    for data in overlapping:
        get_existing, overlap = get_existing_data_func_and_overlap[data['table_name']]
        existing = get_existing(data)
        data['exists'] = list(map(lambda x: list(x), existing))
        overlap.append(data)

    return render(request, 'import/notoria.html',
                  {'form': NotoriaImportForm(),
                   'error_bs': UniqueError(*overlap_bs),
                   'error_fr': UniqueError(*overlap_fr),
                   'error_dp': UniqueError(*overlap_dp),
                   'overlap_bs': json.dumps(overlap_bs),
                   'overlap_fr': json.dumps(overlap_fr),
                   'overlap_dp': json.dumps(overlap_dp)})
