from flask import Flask, request, jsonify
from cluegiver import getClues

app = Flask(__name__)

@app.route('/clue', methods=['POST'])
def handleClueRequest():
    import time
    t0 = time.time()
    jsonContent = request.get_json()
    print(jsonContent)
    result = getClues(jsonContent['words'], jsonContent['labels'], jsonContent['team'])
    mostHintedAt = max([i for i in range(len(result)) if result[i]])
    print(mostHintedAt)
    print(time.time() - t0)
    return jsonify(result)
    # placeholder = {
    #     "clue": "sky",
    #     "rating": 0.891205757856369,
    #     "wordsHintedAt": [
    #         "air",
    #         "eye",
    #         "Jupiter"
    #     ]
    # }
    # return jsonify(placeholder)

@app.route('/<name>', methods=['GET', 'POST'])
def hello_name(name):
    return name + ' is not a valid route'

if __name__ == '__main__':
   app.run(host='0.0.0.0')