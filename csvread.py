import csv


with open('20081026094426.csv') as csv_file:
    csv_reader = csv.DictReader(csv_file,
                                fieldnames=("Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Date", "Time"))
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'\t{" ".join(row)}')
        if line_count >= 6:
            print(
                f'\t{row["Latitude"]}\t{row["Longitude"]}\t{row["Nr"]}\t{row["Altitude"]}\t{row["DateFrom"]}\t{row["Date"]}\t{row["Time"]}')

        line_count += 1
    print(f'Processadas {line_count} linhas.')
