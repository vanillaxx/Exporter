from django.shortcuts import render
import common.Export.export as export_methods
from common.Utils.export_status import ExportStatus
from ..forms import *
import os.path
from django.contrib import messages


def export(request):
    try:
        if request.method == 'POST':
            form = ExportForm(request.POST, count=request.POST.get('date_ranges_count'))
            if form.is_valid():
                file_name = request.POST.get('file_name', None)
                if not file_name.endswith(".csv"):
                    file_name += ".csv"
                if os.path.isfile(file_name):
                    messages.error(request, 'File with that name already exists.')
                    return render(request, 'export/export.html', {'form': form})

                chosen_data = request.POST.get('chosen_data', None)
                chosen_companies = list(form.cleaned_data.get('chosen_companies').values_list('id', flat=True))
                intervals = {
                    '-f': form.cleaned_data.get('chosen_interval_ratios', None),
                    '-d': form.cleaned_data.get('chosen_interval_ratios', None),
                    '-s': form.cleaned_data.get('chosen_interval_stooq', None),
                    '-mv': form.cleaned_data.get('chosen_interval_gpw', None)
                }
                balance_sheet_intervals = ['-da', '-ca', '-fa', '-de', '-ce', '-fe']
                for i in balance_sheet_intervals:
                    intervals[i] = form.cleaned_data.get('chosen_interval_balance', None)

                date_ranges_count = request.POST.get('date_ranges_count', None)

                statuses = []
                for index in range(int(date_ranges_count) + 1):
                    start_date = form.cleaned_data.get('start_date_{index}'.format(index=index))
                    end_date = form.cleaned_data.get('end_date_{index}'.format(index=index))

                    if index == 0:
                        add_description = True
                    else:
                        add_description = False

                    chosen_interval = intervals[chosen_data]
                    statuses.append(export_methods.functions[chosen_data](chosen_companies, start_date, end_date,
                                                                          file_name, chosen_interval, add_description))

                success = [status for status in statuses if status is ExportStatus.SUCCESS]
                if len(success) >= 1:
                    messages.success(request, ExportStatus.SUCCESS.get_message(file_name))
                    return render(request, 'export/export.html', {'form': ExportForm()})
                else:
                    messages.success(request, ExportStatus.FAILURE.get_message(file_name))
                    return render(request, 'export/export.html', {'form': ExportForm()})

        else:
            form = ExportForm()

        return render(request, 'export/export.html', {'form': form})
    except:
        return render(request, 'error.html')
