import xlrd
import DAL.utils

class ExcelParser():
    def __init__(self):
        self.assets_to_omit = ['Non-current assets', 'Current assets',
        'Assets held for sale and discontinuing operations']
        self.equities_to_omit = ['Equity shareholders of the parent',
        'Non-controlling interests', 'Non-current liabilities', 'Current liabilities',
        'Liabilities related to assets held for sale and discontinued operations']

    def parse(self, path, sheet_name, company):
        excel_file = xlrd.open_workbook(path)
        excel_sheet = excel_file.sheet_by_name(sheet_name)
        company_id = DAL.utils.get_company_id_from_name(company)
        curr_row = 0
        curr_column = 2
        assets = []
        equity_liabilities = []
        while curr_row < excel_sheet.nrows:
            if excel_sheet.cell(curr_row, curr_column).value == 'Balance sheet':
                attributes_column = curr_column
                curr_column += 1
                dates_row = curr_row + 1
                sum_row = dates_row + 1
                curr_row += 3
                assets_attributes = []
                equity_liabilities_attributes = []
                while curr_column < excel_sheet.ncols:
                    #check if data for that period exists
                    if not excel_sheet.cell(sum_row, curr_column).value:
                        curr_column += 1
                        continue
                    else:
                        sum = float(excel_sheet.cell(sum_row, curr_column).value)
                    #add date to list
                    assets.append(excel_sheet.cell(dates_row, curr_column).value)
                    equity_liabilities.append(excel_sheet.cell(dates_row, curr_column).value)
                    #omit
                    #curr_row += 2
                    #iterate from the first element until assets end
                    while excel_sheet.cell(curr_row, attributes_column).value != '':
                        attribute = excel_sheet.cell(curr_row, attributes_column).value
                        if attribute in self.assets_to_omit:
                            curr_row += 1
                            continue
                        assets_attributes.append(attribute)
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
                        attribute = excel_sheet.cell(curr_row, attributes_column).value
                        if attribute in self.equities_to_omit:
                            curr_row += 1
                            continue
                        equity_liabilities_attributes.append(attribute)
                        curr_value = excel_sheet.cell(curr_row, curr_column).value
                        #insert 0 instead of empty value
                        if curr_value != '':
                            percentage_value = float(curr_value) * 100 / sum
                            equity_liabilities.append(round(percentage_value, 2))
                        else:
                            equity_liabilities.append(0.0)
                        curr_row += 1
                    assets_attributes.insert(0, "Date")
                    equity_liabilities_attributes.insert(0, "Date")
                    assets_attributes.insert(0, "CompanyID")
                    equity_liabilities_attributes.insert(0, "CompanyID")
                    assets.insert(0, company_id)
                    equity_liabilities.insert(0, company_id)
                    DAL.utils.insert_values(table_name="Assets",
                                            columns=assets_attributes, values=assets)
                    DAL.utils.insert_values(table_name="EquityLiabilities",
                                            columns=equity_liabilities_attributes,
                                            values=equity_liabilities)
                    assets_attributes = []
                    equity_liabilities_attributes = []
                    assets = []
                    equity_liabilities = []
                    curr_column += 1
                    curr_row = sum_row + 1
                break
            curr_row += 1



if __name__ == "__main__":
    ep = ExcelParser()
    excel_file = input("Enter path to file:\n")
    sheet = input("Enter sheet: QS or YS\n")
    company = input("Enter company name:\n")
    ep.parse(excel_file, sheet, company)