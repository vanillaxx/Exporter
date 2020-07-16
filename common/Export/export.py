from common.DAL.db_queries import get_assets_for_company
import csv


if __name__ == "__main__":

    csv_file = []
    for row in get_assets_for_company('Comarch SA'):
        print(row)
        skip = 3
        fresh_row = []
        for value in row:
            if skip > 0:
                skip = skip -1
                fresh_row.append(value)
            else:
                fresh_row.append(value / row[2])
        csv_file.append(fresh_row)
    print(csv_file)

    with open("output.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_file)