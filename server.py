from flask import Flask, request, jsonify, Response
import sys, json

app = Flask(__name__)

DATABASE = {}


@app.route('/put', methods=['POST'])
def put():
    packet = request.json
    print(f"Received put request{packet}")
    key = packet["key"]
    value = packet["value"]
    DATABASE[key] = value
    return Response(status=202)


@app.route('/get', methods=['GET'])
def get():
    packet = request.json
    print(f"Received get request {packet}")
    key = packet["key"]
    if key in DATABASE:
        return jsonify(value=DATABASE[key])
    else:
        return Response(status=404)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
        app.run(host='127.0.0.1', port=port, debug=True, threaded=True)
    else:
        print("usage: python3 server.py <port>")