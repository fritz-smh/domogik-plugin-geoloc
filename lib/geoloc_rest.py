from flask import Flask
app = Flask(__name__)

@app.route('/')
def root():
    return 'Domogik geoloc plugin!'


@app.route('/position_degree/<string:data>', methods = ["GET"])
def position_degree(data):
    return "data : {0}".format(data)


if __name__ == '__main__':
    app.run(debug=True, host = "192.168.1.10", port = 8000)
