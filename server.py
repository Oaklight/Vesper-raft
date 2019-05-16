from flask import Flask, request, jsonify
import sys, json

app = Flask(__name__)

DATABASE = {}

@app.route('/store', methods=['POST'])
def success():
    
    packet = request.json
    print(f"Received {packet}")
    key = packet["key"]
    value = packet["value"]
    DATABASE[key] = value 

    return jsonify({"code" : 202})


if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = int (sys.argv[1])
        app.run(host='127.0.0.1',port=port, debug=True)
    else:
        print("usage: python3 server.py <port>")