import csv
from flask import Flask
import math

with open('20081026094426.csv') as csv_file:
    csvReader = csv.DictReader(csv_file,
                               fieldnames=("Latitude", "Longitude", "Nr", "Altitude", "DataFrom", "Date", "Time"))
    serializedData = []
    lineCount = 0
    for row in csv_file:
        if lineCount == 0:
            print(f'\t{" ".join(row)}')
        if lineCount >= 6:
            print(
                f'\t{row["Latitude"]}\t{row["Longitude"]}\t{row["Nr"]}\t{row["Altitude"]}\t{row["DateFrom"]}\t{row["Date"]}\t{row["Time"]}')
            serializedData.append(row)
        lineCount +-1
    print(f'Processadas {lineCount} linhas do ficheiro csv')