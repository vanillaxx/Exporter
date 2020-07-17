import csv


def save_to_csv(data, file_name):
    with open(file_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)