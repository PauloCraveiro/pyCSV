import os
from itertools import cycle
from urllib import request
from flask import Blueprint, jsonify, request
import csv
from pathlib import Path
from haversine import haversine, Unit
import xlsxwriter
import datetime
from cfg import *
import re  # regular expressions
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

# https://stackoverflow.com/questions/24420857/what-are-flask-blueprints-exactly
myCSVReader = Blueprint('myCSVReader', __name__, template_folder='mycode')


@myCSVReader.route("/myCSVReader", methods=["GET"])
def get_points():
    # importa dados do ficheiro IMPORT_FILE
    # serializedData = importData(IMPORT_FILE)
    isValid = False
    downloadPath = ''
    file = ''

    # valida chaves enviadas para a API
    try:
        if 'file' not in request.files:
            file = None
        else:
            file = request.files['file']
            # FILEPATH = Path(__file__).parent.parent.joinpath(file)
            # Atribui ao DOWNLOAD_PATH o caminho parent.parent do ficheiro a executar, da UPLOAD_FOLDER desejada
            downloadPath = Path(__file__).parent.parent.joinpath(UPLOAD_FOLDER)

        # request.form.get permite valor default, request.form nao permite
        # form.get vai buscar o valor ao POSTMAN, ao campo index, se não tiver anda, coloca None como default
        startIndex = request.form.get('index', None)
        if startIndex == '':
            startIndex = None
        elif startIndex is not None:
            startIndex = int(startIndex)

        # form.get vai buscar o valor ao POSTMAN, ao campo latitude, se não tiver anda, coloca None como default
        latitude = request.form.get('latitude', None)
        if latitude == '':
            latitude = None
        elif latitude is not None:
            latitude = int(latitude)

        # form.get vai buscar o valor ao POSTMAN, ao campo longitude, se não tiver anda, coloca None como default
        longitude = request.form.get('longitude', None)
        if longitude == '':
            longitude = None
        elif longitude is not None:
            longitude = int(longitude)

        # form.get vai buscar o valor ao POSTMAN, ao campo data, se não tiver anda, coloca None como default
        data = request.form.get('data', None)
        if data == '':
            data = None
        elif data is not None:
            data = int(data)

        # form.get vai buscar o valor ao POSTMAN, ao campo tempo, se não tiver anda, coloca None como default
        tempo = request.form.get('time', None)
        if tempo == '':
            tempo = None
        elif tempo is not None:
            tempo = int(tempo)

        # form.get vai buscar o valor ao POSTMAN, ao campo altitude, se não tiver anda, coloca None como default
        altitude = request.form.get('altitude', None)
        if altitude == '':
            altitude = None
        elif altitude is not None:
            altitude = int(altitude)

        # form.get vai buscar o valor ao POSTMAN, ao campo datefrom, se não tiver anda, coloca None como default
        datefrom = request.form.get('datefrom', None)
        if datefrom == '':
            datefrom = None
        elif datefrom is not None:
            datefrom = int(datefrom)

        # form.get vai buscar o valor ao POSTMAN, ao campo nr, se não tiver anda, coloca None como default
        nr = request.form.get('nr', None)
        if nr == '':
            nr = None
        elif nr is not None:
            nr = int(nr)

        # verifica se o file, startindex, latitude, longitude, data e tempo têm valores, e se tiverem coloca o isValid a true
        if file is not None and startIndex is not None and latitude is not None and longitude is not None and data is not None and tempo is not None:
            isValid = True

        # cria o header do ficheiro
        IMPORT_FILE_HEADER_MAP.update({"index": startIndex, "Latitude": latitude, "Longitude": longitude,
                                       "Nr": nr, "Altitude": altitude, "DateFrom": datefrom, "Data": data,
                                       "Tempo": tempo, "Distancia(KM)": None, "Distancia(MT)": None,
                                       "Tempo(S)": None, "Vel(m/s)": None, "Vel(km/h)": None,
                                       "Modo": None})


        if file and isValid:
            filename = secure_filename(file.filename)
            file.save(os.path.join(downloadPath, filename))

    except HTTPException as e:
        print(e)

    # importa os dados para a variavel
    serializedData = importData(downloadPath, file.filename)

    # executa o processData com a variavel serializedData e coloca nas variaveis na ordem
    serializedData, totalDistance, totalTime = processData(serializedData)

    # exporta os dados para o ficheiro XLSX
    exportXLSX(serializedData, totalDistance, totalTime)

    # https://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify
    # exporta para a API em JSON
    if len(serializedData) > 0:
        return jsonify(
            {'ok': True, 'data': serializedData, "count": len(serializedData), "total distance": totalDistance,
             "total time": totalTime}), 200
    else:
        return jsonify({'ok': False, 'message': 'No points found'}), 400


def processData(dataGroup):
    pos = 0
    nextRow = None
    totalDistance = 0.0
    totalTime = 0.0
    distanceMT = 0.0

    for row in dataGroup:
        # calcula o tempo entre pontos
        if row["Tempo(S)"] is None:
            p1_timestamp = datetime.datetime.strptime(row["Data"] + ' ' + row["Tempo"], '%Y-%m-%d %H:%M:%S')

            if pos + 1 <= len(dataGroup) - 1:
                nextRow = dataGroup[pos + 1]

            if nextRow is not None:
                p2_timestamp = datetime.datetime.strptime(nextRow["Data"] + ' ' + nextRow["Tempo"],
                                                          '%Y-%m-%d %H:%M:%S')
                row["Tempo(S)"] = (p2_timestamp - p1_timestamp).total_seconds()

        # calcula a distancia em KM e MT
        if row["Distancia(KM)"] is None:
            p1 = (float(row["Latitude"]), float(row["Longitude"]))

            if pos + 1 <= len(dataGroup) - 1:
                nextRow = dataGroup[pos + 1]

            if nextRow is not None:
                p2 = (float(nextRow["Latitude"]), float(nextRow["Longitude"]))
                row["Distancia(KM)"] = round(haversine(p1, p2, unit=Unit.KILOMETERS), 2)
                row["Distancia(MT)"] = distanciaMT = round(haversine(p1, p2, unit=Unit.METERS), 2)

        # calcula velocidade em m/s e k/s
        if row["Vel(m/s)"] is None:
            try:
                row["Vel(m/s)"] = round(distanciaMT / float(row["Tempo(S)"]), 2)
                row["Vel(km/h)"] = round(float(row["Vel(m/s)"]) * 3.6, 2)
            except:
                row["Vel(m/s)"] = 0.0
                row["Vel(km/h)"] = 0.0

        # calcula o metodo de transporte usado
        if row["Modo"] is None:
            try:
                row["Modo"] = 'Stop'

                # regra guide Possible transportation modes are:
                # walk, bike, bus, car, subway, train, airplane, boat, run and motorcycle
                if 0.01 <= float(row["Vel(km/h)"]) <= 2.0:
                    row["Modo"] = 'Walk'

                # velocidade media de ser humano a andar 2-6 km
                if 2.0 <= float(row["Vel(km/h)"]) <= 7.0:
                    row["Modo"] = 'Walk'

                # velocidade media de ser humano a correr 7-10 km
                if 7.0 <= float(row["Vel(km/h)"]) <= 11.0:
                    row["Modo"] = 'Run'

                # velocidade media bicicleta 11-19 km
                if 11.0 <= float(row["Vel(km/h)"]) <= 20.0:
                    row["Modo"] = 'Bike'

                # velocidade media carro https://en.wikipedia.org/wiki/Medium-speed_vehicle
                if 20.0 <= float(row["Vel(km/h)"]) <= 72.9:
                    row["Modo"] = 'Car'

                # velocidade media aviao https://www.onaverage.co.uk/speed-averages/24-average-speed-of-a-plane
                if 200.0 <= float(row["Vel(km/h)"]) <= 2000.0:
                    row["Modo"] = 'Airplane'
            except:
                row["Modo"] = 'na'

        pos += 1
        totalDistance += distanciaMT
        totalTime += row["Tempo(S)"]

    return dataGroup, round(totalDistance, 2), round(totalTime, 2)


def importData(downloadPath, fileToImport):
    # parent = volta 1 pasta atras , parent.parent volta duas
    processedData = []
    path = os.path.join(downloadPath, fileToImport)
    # path = Path(__file__).parent.parent.joinpath(fileToImport)  # importa o caminho do ficheiro dinamicamente ||
    with open(path, mode="r") as csv_file:  # importa executa e fecha automaticamente
        csvReader = csv.DictReader(csv_file,
                                   fieldnames=("Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Data", "Tempo",
                                               "Distancia(KM)", "Distancia(MT)", "Tempo(S)", "Vel(m/s)", "Vel(km/h)",
                                               "Modo"))
        lineCount = 0
        startLine = 0
        # coloca o index ou seja, o numero de linhas a ignorar
        index = IMPORT_FILE_HEADER_MAP.get('index')
        if not index == "Invalid Index":
            startLine = index

        for row in csvReader:
            if lineCount >= startLine:
                # cast para lista, para se poder tratar os dados de forma mais simples do que
                # sem o cast pois os strings permitem coisas
                # que o dictionary nao permite
                itemsGroup = list(row.items())

                # re.search procura na row a expressão e se encontrar retorna true, se não mantem a variavel como NONE
                row['Latitude'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Latitude')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Latitude', None) is not None else None
                if row['Latitude'] is not None:
                    match = re.search(r'(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$',
                                      row['Latitude'])
                    if match is None:
                        row['Latitude'] = None

                # re.search procura na row a expressão e se encontrar retorna true, se não mantem a variavel como NONE
                row['Longitude'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Longitude')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Longitude', None) is not None else None
                if row['Longitude'] is not None:
                    match = re.search(
                        r'(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$',
                        row['Longitude'])
                    if match is None:
                        row['Longitude'] = None

                # ternarios para insercao do valor na row
                row['Nr'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Nr')][1] if IMPORT_FILE_HEADER_MAP.get('Nr',
                                                                                                          None) is not None else None

                row['Altitude'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Altitude')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Altitude', None) is not None else None
                if row['Altitude'] is not None:
                    if float(row['Altitude']) <= 0:
                        row['Altitude'] = -777

                row['DateFrom'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('DateFrom')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'DateFrom', None) is not None else None

                row['Data'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Data')][1] if IMPORT_FILE_HEADER_MAP.get('Data',
                                                                                                              None) is not None else None

                # expressao regular que procura uma data xx/xx/xxx ou xxxx/xx/xx
                if row['Data'] is not None:
                    match = re.search(r'\d{2}-\d{2}-\d{4}', row['Data'])
                    dataFilter = '%d-%m-%Y'
                    if match is None:
                        match = re.search(r'\d{4}-\d{2}-\d{2}', row['Data'])
                        dataFilter = '%Y-%m-%d'
                    if match is not None:
                        date = datetime.datetime.strptime(match.group(), dataFilter).date()
                        row['Data'] = date.strftime('%Y-%m-%d')
                    else:
                        row['Data'] = None

                row['Tempo'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Tempo')][1] if IMPORT_FILE_HEADER_MAP.get('Tempo',
                                                                                                                None) is not None else None

                if row['Tempo'] is not None:
                    match = re.search(r'\d{2}:\d{2}:\d{2}', row['Tempo'])
                    if match is not None:
                        time = datetime.datetime.strptime(match.group(), '%H:%M:%S').time()
                        row['Tempo'] = time.strftime("%H:%M:%S")
                    else:
                        row['Tempo'] = None

                row['Distancia(KM)'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Distancia(KM)')][
                    1] if IMPORT_FILE_HEADER_MAP.get('Distancia(KM)', None) is not None else None
                row['Distancia(MT)'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Distancia(MT)')][
                    1] if IMPORT_FILE_HEADER_MAP.get('Distance (Mt)', None) is not None else None
                row['Tempo(S)'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Tempo(S)')][
                    1] if IMPORT_FILE_HEADER_MAP.get('Time (Sec)', None) is not None else None
                row['Vel(m/s)'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Vel(m/s)')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Vel(m/s)', None) is not None else None
                row['Vel(km/h)'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Vel(km/h)')][1] if IMPORT_FILE_HEADER_MAP.get(
                    'Vel(km/h)', None) is not None else None
                row['Modo'] = itemsGroup[IMPORT_FILE_HEADER_MAP.get('Modo')][1] if IMPORT_FILE_HEADER_MAP.get('Modo',
                                                                                                              None) is not None else None

                if row['Latitude'] is not None and row['Longitude'] is not None and row['Data'] is not None and row[
                    'Tempo'] is not None:
                    processedData.append(row)

            lineCount += 1

    return processedData


def exportXLSX(dataGroup, totalDistance, totalTime):
    workbook = xlsxwriter.Workbook(XLSX_FILE)
    worksheet = workbook.add_worksheet('Data')
    header_format = workbook.add_format({'bold': True, 'font_color': 'black'})
    header_data_format = workbook.add_format({'font_color': 'Gray'})
    # worksheet.write(0, 0, None, header_data_format)
    worksheet.write_blank(0, 0, None, header_data_format)
    worksheet.write(1, 0, None, header_data_format)

    worksheet.set_column(2, 0, 25)
    worksheet.write(2, 0, 'Total distance(mt)', header_format)
    worksheet.write(2, 1, totalDistance, header_data_format)
    worksheet.set_column(3, 0, 10)
    worksheet.write(3, 0, 'Total time(s)', header_format)
    worksheet.write(3, 1, totalTime, header_data_format)
    worksheet.write(3, 2, 'Delta', header_format)
    worksheet.write(3, 3, str(datetime.timedelta(seconds=totalTime)), header_data_format)

    # # headers
    # worksheet.write('A1', 'Latitude')
    # worksheet.write('B1', 'Latitude')
    # worksheet.write('C1', 'Nr')
    # worksheet.write('D1', 'Altitude')
    # worksheet.write('E1', 'Data')
    # worksheet.write('F1', 'Tempo')
    # worksheet.write('G1', 'Distancia(KM)')
    # worksheet.write('H1', 'Distancia(MT)')
    # worksheet.write('I1', 'Tempo(S)')
    # worksheet.write('J1', 'Vel(m/s)')
    # worksheet.write('K1', 'Vel(km/h)')

    lineNumber = 5
    # headers
    # worksheet.set_column(line_number, 0, 10)
    worksheet.write(lineNumber, 0, 'Latitude', header_format)
    worksheet.write(lineNumber, 1, 'Longitude', header_format)
    worksheet.write(lineNumber, 2, 'Nr', header_format)
    worksheet.write(lineNumber, 3, 'Altitude', header_format)
    worksheet.set_column(lineNumber, 4, 10)
    worksheet.write(lineNumber, 4, 'Data', header_format)
    worksheet.set_column(lineNumber, 5, 10)
    worksheet.write(lineNumber, 5, 'Tempo', header_format)
    worksheet.set_column(lineNumber, 6, 40)
    worksheet.write(lineNumber, 6, 'Distancia(KM)', header_format)
    worksheet.set_column(lineNumber, 7, 40)
    worksheet.write(lineNumber, 7, 'Distancia(MT)', header_format)
    worksheet.set_column(lineNumber, 8, 10)
    worksheet.write(lineNumber, 8, 'Tempo(S)', header_format)
    worksheet.write(lineNumber, 9, 'Vel(m/s)', header_format)
    worksheet.write(lineNumber, 10, 'Vel(km/h)', header_format)
    worksheet.write(lineNumber, 11, 'Modo', header_format)
    lineNumber += 1

    # lines
    #lines_format = workbook.add_format({'bg_color': '#ffffff'})
    data_format_odd = workbook.add_format({'bg_color': '#078a74'})
    data_format_even = workbook.add_format({'bg_color': '#07638a'})
    formats = cycle([data_format_odd, data_format_even])

    for row, row_data in enumerate(dataGroup):
        data_format = next(formats)
        # worksheet.set_row(line_number, None, data_format)
        worksheet.write(lineNumber, 0, row_data["Latitude"], data_format)
        worksheet.write(lineNumber, 1, row_data["Longitude"], data_format)
        worksheet.write(lineNumber, 2, row_data["Nr"], data_format)
        worksheet.write(lineNumber, 3, row_data["Altitude"], data_format)
        worksheet.write(lineNumber, 4, row_data["Data"], data_format)
        worksheet.write(lineNumber, 5, row_data["Tempo"], data_format)
        worksheet.write(lineNumber, 6, row_data["Distancia(KM)"], data_format)
        worksheet.write(lineNumber, 7, row_data["Distancia(MT)"], data_format)
        worksheet.write(lineNumber, 8, row_data["Tempo(S)"], data_format)
        worksheet.write(lineNumber, 9, row_data["Vel(m/s)"], data_format)
        worksheet.write(lineNumber, 10, row_data["Vel(km/h)"], data_format)
        worksheet.write(lineNumber, 11, row_data["Modo"], data_format)
        lineNumber += 1

    workbook.close()
