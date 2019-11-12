from flask import Flask
from gevent.pywsgi import WSGIServer
from cfg import *
from mycode.myCSVReader import *
import datetime

app = Flask(__name__)

# api entry point
@app.route("/")
def index():
    return "Bem vindo a CSVReader by Paulo Craveiro - " + '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())


# regista endpoint de mycode.
app.register_blueprint(py)


# inicia api em modo dev/prod
if __name__ == '__main__':
    if SERVER_MODE_DEV:
        # Debug/Development
        app.run(debug=True, host="127.0.0.1", port=SERVER_PORT)
    else:
        # Production
        http_server = WSGIServer(('', SERVER_PORT), app)
        http_server.serve_forever()
