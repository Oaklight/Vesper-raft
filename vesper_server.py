from node import Node
from node import FOLLOWER, LEADER, CANDIDATE
from flask import Flask, request, jsonify, Response
import utils
import sys
import logging

app = Flask(__name__)


@app.route("/value", methods=['GET'])
def value():
    payload = request.json["payload"]
    if n.status == LEADER:
        # request handle, reply is a dictionary
        result = n.handle_get(payload)
        if result:
            reply = {"code": "success", "payload": result}
        else:
            reply = {"code": 'fail', 'payload': payload}
    elif n.status == FOLLOWER:
        # redirect request
        leader = n.leader
        payload["message"] = leader
        reply = {"code": 'fail', 'payload': payload}
    else:
        reply = {"code": 'fail', 'payload': payload}
    return jsonify(reply)


@app.route("/value", methods=['PUT'])
def value():
    payload = request.json["payload"]
    if n.status == LEADER:
        # request handle, reply is a dictionary
        result = n.handle_put(payload)
        if result:
            reply = {"code": "success"}
        else:
            reply = {"code": 'fail'}
    elif n.status == FOLLOWER:
        # redirect request
        leader = n.leader
        payload["message"] = leader
        reply = {"code": 'fail', 'payload': payload}
    else:
        reply = {"code": 'fail'}
    return jsonify(reply)


@app.route("/vote_req", methods=['POST'])
def vote_req():
    # also need to let me know whether up-to-date or not
    term = request.json["term"]
    commitIdx = request.json["commitIdx"]
    choice, term = n.decide_vote(term, commitIdx)
    message = {"choice": choice, "term": term}
    return jsonify(message)


@app.route("/heartbeat", methods=['POST'])
def heartbeat():
    # term = request.json["term"]
    term = n.heartbeat_follower(request.json)
    # return anyway, if nothing received by leader, we dead
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
