from flask import Blueprint, jsonify
import csv
from pathlib import Path
from haversine import haversine, Unit
import xlsxwriter
import datetime
from cfg import XLSX_FILE

se = Blueprint('se', __name__, template_folder='templates')


@se.route("/se", methods=["GET"])
def get_points():
    serializedData = []
    next_row = None
    total_distance = 0.0
    total_time = 0.0

    path = Path(__file__).parent.parent.joinpath('20081026094426.csv') #importa o caminho do csv
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=("Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Date", "Time", "Distance (Km)", "Time (Sec)", "Vel. m/s", "Vel. km/h", "Mode"))
        line_count = 0
        for row in csv_reader:
            # if line_count == 0:
            #     print(f'\t{" ".join(row)}')

            if line_count >= 6:
                # print(f'\t{row["Latitude"]}\t{row["Longitude"]}\t{row["Nr"]}\t{row["Altitude"]}\t{row["DateFrom"]}\t{row["Date"]}\t{row["Time"]}')

                # Remover os valores negativos da altitude
                a1 = float(row["Altitude"])
                if a1 <= 0:
                    row['Altitude'] = -777

                print(f'\t{row["Altitude"]}')

                serializedData.append(row)
            line_count += 1
        # print(f'Processadas {line_count} linhas.')xx

        pos = 0
        for row in serializedData:
            if row["Time (Sec)"] is None:
                p1_timestamp = datetime.datetime.strptime(row["Date"] + ' ' + row["Time"], '%Y-%m-%d %H:%M:%S')
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
                    row["Distance (Km)"] = round(haversine(p1, p2), 2)
            pos += 1
            total_distance += row["Distance (Km)"]
            total_time += row["Time (Sec)"]

    workbook = xlsxwriter.Workbook(XLSX_FILE)
    worksheet = workbook.add_worksheet('Data')

    # headers
    worksheet.write('A1', 'Latitude')
    worksheet.write('B1', 'Latitude')
    worksheet.write('C1', 'Nr')
    worksheet.write('D1', 'Altitude')
    worksheet.write('E1', 'Date')
    worksheet.write('F1', 'Time')
    worksheet.write('G1', 'Distance (Km)')
    worksheet.write('H1', 'Time (Sec)')

    # lines
    line_number = 5
    for row in serializedData:
        worksheet.write(line_number, 0, row["Latitude"])
        worksheet.write(line_number, 1, row["Longitude"])
        worksheet.write(line_number, 2, row["Nr"])
        worksheet.write(line_number, 3, row["Altitude"])
        worksheet.write(line_number, 4, row["Date"])
        worksheet.write(line_number, 5, row["Time"])
        worksheet.write(line_number, 6, row["Distance (Km)"])
        worksheet.write(line_number, 7, row["Time (Sec)"])
        line_number += 1

    workbook.close()

    if line_count > 0:
        return jsonify({'ok': True, 'data': serializedData, "count": len(serializedData), "total distance": total_distance, "total time": total_time}), 200
    else:
        return jsonify({'ok': False, 'message': 'No points found'}), 400

