# api settings
SERVER_MODE_DEV = True
SERVER_PORT = 4000
XLSX_FILE = 'myCSVReader.xlsx'
IMPORT_FILE = '20081026094426.csv'
#IMPORT_FILE = '15-07-2017-ap-02738d854419-pml.csv'
IMPORT_FILE_INDEX = {
        "20081026094426.csv": 6,
        "15-07-2017-ap-02738d854419-pml.csv": 1
    }
# "Latitude", "Longitude", "Nr", "Altitude", "DateFrom", "Date", "Time", "Distance (Km)", "Distance (Mt)", "Time (Sec)", "Vel. m/s", "Vel. km/h", "Mode"
IMPORT_FILE_HEADER_MAP = {
        "Latitude": 0,
        "Longitude": 1,
        "Nr": 2,
        "Altitude": 3,
        "DateFrom": 4,
        "Data": 5,
        "Tempo": 6,
        "Distancia(KM)": None,
        "Distancia(MT)": None,
        "Tempo(S)": None,
        "Vel(m/s)": None,
        "Vel(km/h)": None,
        "Modo": None
    }

# "_id","bssid","dayoftheweek","ssid","attractiveness","dateTime","latitude","longitude"
# IMPORT_FILE_HEADER_MAP = {
#         "Latitude": 6,
#         "Longitude": 7,
#         "Nr": 0,
#         "Altitude": None,
#         "DateFrom": None,
#         "Date": 5,
#         "Tempo": 5,
#         "Distancia(KM)": None,
#         "Distancia(MT)": None,
#         "Tempo(S)": None,
#         "Vel(m/s)": None,
#         "Vel(km/h)": None,
#         "Modo": None
#     }
