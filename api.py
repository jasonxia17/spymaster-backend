from flask import Flask, request
from flask_restful import Api, Resource
import base64
from text_recognition import text_detection
app = Flask(__name__)
api = Api(app)

class Board(Resource):
    def post(self):
        im_json = request.get_json()
        with open("example.png", "wb") as output:
            output.write(base64.b64decode(im_json["imageBase64"]))
        list_raw = text_detection("example.png")
        l = []
        for i in range(len(list_raw)):
            for j in range(len(list_raw[i])):
                l.append(list_raw[i][j])
        return l, 200

api.add_resource(Board, "/image")
app.run(host = '0.0.0.0')