from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/clue', methods=['POST'])
def handleClueRequest():
    jsonContent = request.get_json()
    print('got request')
    print(jsonContent)
    return jsonify({'numOfWords' : len(jsonContent['words'])})

@app.route('/<name>', methods=['GET', 'POST'])
def hello_name(name):
    return name + ' is not a valid route'

if __name__ == '__main__':
   app.run()