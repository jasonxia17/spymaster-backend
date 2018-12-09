from flask import Flask, request, jsonify
from cluegiver import getClues

app = Flask(__name__)

@app.route('/clue', methods=['POST'])
def handleClueRequest():
    import time
    t0 = time.time()
    jsonContent = request.get_json()
    try:
        result = getClues(jsonContent['wordObjectList'], jsonContent['teamName'])
        print(time.time() - t0)
        return jsonify(result)
    except ValueError as err:
        return jsonify({'err': str(err)})

@app.route('/<name>', methods=['GET', 'POST'])
def hello_name(name):
    return name + ' is not a valid route'

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'The site is up and running! You can make a post request to the server now :)'

if __name__ == '__main__':
   app.run(host='0.0.0.0')