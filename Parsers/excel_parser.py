import xlrd


class ExcelParser():
    def __init__(self):
        self.assets_to_omit = ['Non-current assets', 'Current assets',
        'Assets held for sale and discontinuing operations', 'Called up capital',
        'Own shares']
        self.equities_to_omit = ['Equity shareholders of the parent',
        'Non-controlling interests', 'Non-current liabilities', 'Current liabilities',
        'Liabilities related to assets held for sale and discontinued operations']

    def parse(path, sheet_name):
        excel_file = xlrd.open_workbook(path)
        excel_sheet = excel_file.sheet_by_name(sheet_name)

        curr_row = 0
        curr_column = 2
        assets = []
        equity_liabilities = []
        while curr_row < excel_sheet.nrows:
            if excel_sheet.cell(curr_row, curr_column).value == 'Balance sheet':
                attributes_column = curr_column
                curr_column += 1
                curr_row += 1
                dates_row = curr_row
                while curr_column < excel_sheet.ncols:
                    #check if data for that period exists
                    if not excel_sheet.cell(dates_row + 1, curr_column).value:
                        curr_column += 1
                        continue
                    else:
                        sum = float(excel_sheet.cell(dates_row + 1, curr_column).value)
                    #add date to list
                    assets.append(excel_sheet.cell(curr_row, curr_column).value)
                    equity_liabilities.append(excel_sheet.cell(curr_row, curr_column).value)
                    #add sum of assets == equity & liabilities to list
                    assets.append(excel_sheet.cell(curr_row+1, curr_column).value)
                    equity_liabilities.append(excel_sheet.cell(curr_row+1, curr_column).value)
                    curr_row += 2
                    #iterate from the first element until assets end
                    while excel_sheet.cell(curr_row, attributes_column).value != '':
                        curr_value = excel_sheet.cell(curr_row, curr_column).value
                        #insert 0 instead of empty value
                        if curr_value != '':
                            percentage_value = float(curr_value) * 100 / sum
                            assets.append(round(percentage_value, 2))
                        else:
                            assets.append(0.0)
                        curr_row += 1
                    curr_row += 2
                    #omit headers and iterate until equities and liabilities end
                    while excel_sheet.cell(curr_row, attributes_column).value != 'Date of publication':
                        curr_value = excel_sheet.cell(curr_row, curr_column).value
                        #insert 0 instead of empty value
                        if curr_value != '':
                            percentage_value = float(curr_value) * 100 / sum
                            equity_liabilities.append(round(percentage_value, 2))
                        else:
                            equity_liabilities.append(0.0)
                        curr_row += 1
                    print(assets)
                    print(equity_liabilities)
                    assets = []
                    equity_liabilities = []
                    curr_column += 1
                    curr_row = dates_row
                break
            curr_row += 1



if __name__ == "__main__":
    ep = ExcelParser
    excel_file = input("Enter path to file:\n")
    sheet = input("Enter sheet: QS or YS\n")
    ep.parse(excel_file,sheet)