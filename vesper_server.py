from node import Node
from flask import Flask, request, jsonify, Response
import sys
import logging

app = Flask(__name__)


@app.route("/vote_req", methods=['POST'])
def vote_req():
    term = request.json["term"]
    choice = n.decide_vote(term)
    message = {"choice": choice}
    return jsonify(message)


@app.route("/heartbeat", methods=['POST'])
def heartbeat():
    term = request.json["term"]
    term = n.heartbeat_follower(term)
    message = {"term": term}
    return jsonify(message)


log = logging.getLogger('werkzeug')
log.disabled = True

if __name__ == "__main__":
    # python server.py index ip_list
    if len(sys.argv) == 3:
        index = int(sys.argv[1])
        ip_list_file = sys.argv[2]
        ip_list = []
        with open(ip_list_file) as f:
            for ip in f:
                ip = ip.strip()
                ip_list.append(ip)
        my_ip = ip_list.pop(index)
        print(ip_list)

        http, host, port = my_ip.split(':')
        logging.basicConfig(format=f'[{port}]-%(message)s', level=logging.INFO)
        # print(host, port)
        n = Node(ip_list, my_ip)
        logging.info(f"starting {port}")
        app.run(host="0.0.0.0", port=int(port), debug=False)
    else:
        print("usage: python server.py index ip_list_file")
