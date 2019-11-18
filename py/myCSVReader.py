from flask import Blueprint, jsonify
import csv
from pathlib import Path
from haversine import haversine, Unit
import xlsxwriter
import datetime
from cfg import XLSX_FILE

#https://stackoverflow.com/questions/24420857/what-are-flask-blueprints-exactly
py = Blueprint('py', __name__, template_folder='py')

@py.route("/py", methods=["GET"])
def get_points():
    serializedData = []
    nextRow = None
    totalDistance = 0.0
    totalTime = 0.0

    path = Path(__file__).parent.parent.joinpath('20081026094426.csv') #importa o caminho do csv dinamicamente
    with open(path, mode="r") as csv_file:  #importa executa e fecha automaticamente
        csvReader = csv.DictReader(csv_file, fieldnames=("Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Data", "Tempo"
                                                         "Distancia(KM)", "Tempo(S)", "Vel(m/s)", "Vel(Km/h)", "Mode"))
        lineCount = 0
        for row in csvReader:
            if lineCount == 0:
                print(f'\t{" ".join(row)}')
            if lineCount >= 6:
                # print(f'\t{row["Latitude"]}\t{row["Longitude"]}\t{row["Nr"]}\t{row["Altitude"]}\t{row["DateFrom"]}\t{row["Date"]}\t{row["Time"]}')

                altTest = float(row["Altitude"])
                if altTest < 0:
                    row["Altitude"] = -333
                print(f'\t{row["Altitude"]}')
            serializedData.append(row)
        lineCount += 1

        pos = 0
        for row in serializedData:
            if row["Tempo(S)"] is None:
                p1_timestamp = datetime.datetime.strftime(row["Data"] + ' ' + row["Tempo"], '%Y-%m-%d %H:%M:%S')
                if pos + 1 <= len(serializedData) - 1:
                    next_row = serializedData[pos + 1]
                if next_row is not None:
                    p2_timestamp = datetime.datetime.strptime(next_row["Date"] + ' ' + next_row["Time"], '%Y-%m-%d %H:%M:%S')
                    row["Time (Sec)"] = (p2_timestamp - p1_timestamp).total_seconds()

            if row["Distance (Km)"] is None:
                p1 = (float(row["Latitude"]), float(row["Longitude"]))
                if pos + 1 <= len(serializedData) - 1:
                    next_row = serializedData[pos + 1]
            if next_row is not None:
                p2 = (float(next_row["Latitude"]), float(next_row["Longitude"]))
                row["Distancia(KM)"] = round(haversine(p1, p2), 2)
            pos += 1
            totalDistance += row["Distancia(KM)"]
            totalTime += row["Tempo(S)"]

    workbook = xlsxwriter.Workbook(XLSX_FILE)
    worksheet = workbook.add_worksheet('Data')

    # headers
    worksheet.write('A1', 'Latitude')
    worksheet.write('B1', 'Latitude')
    worksheet.write('C1', 'Nr')
    worksheet.write('D1', 'Altitude')
    worksheet.write('E1', 'Data')
    worksheet.write('F1', 'Tempo')
    worksheet.write('G1', 'Distancia(KM)')
    worksheet.write('H1', 'Tempo(S)')

    # lines
    lineNumber = 5
    for row in serializedData:
        worksheet.write(lineNumber, 0, row["Latitude"])
        worksheet.write(lineNumber, 1, row["Longitude"])
        worksheet.write(lineNumber, 2, row["Nr"])
        worksheet.write(lineNumber, 3, row["Altitude"])
        worksheet.write(lineNumber, 4, row["Data"])
        worksheet.write(lineNumber, 5, row["Tempo"])
        worksheet.write(lineNumber, 6, row["Distancia(KM)"])
        worksheet.write(lineNumber, 7, row["Tempo(S)"])
        lineNumber += 1

    workbook.close()

    #https://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify
    if lineCount > 0:
        return jsonify({'ok' : True, 'data': serializedData, "count": len(serializedData), "Distancia Total": totalDistance, "Tempo Total": totalTime}), 200
    else:
        return jsonify({'ok': False, 'message': 'No points found'}), 400