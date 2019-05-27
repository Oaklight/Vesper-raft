from node import Node
from flask import Flask, request, jsonify, Response
import sys
import logging
app = Flask(__name__)


def get_address(r):
    addr = r.environ["REMOTE_ADDR"]
    port = r.environ["REMOTE_PORT"]
    return str(addr) + ":" + str(port)


@app.route('/vote', methods=['POST'])
def vote():
    addr = request.json["addr"]
    term = request.json["term"]
    choice = request.json["choice"]
    if choice:
        n.recv_vote(addr)
    # logging.info(f"VOTE from {addr} for term : {term} [{choice}]")
    return Response(status=200)
    # print(request.form)
    # return jsonify(request.form)


@app.route("/vote_req", methods=['POST'])
def vote_req():
    addr = request.json["addr"]
    term = request.json["term"]
    n.recv_vote_req(addr, term)
    # logging.info(f"VOTE_REQ from : {addr} for term : {term}")
    # message = {"term": term, "addr": addr, "choice": choice}
    # return jsonify(message)
    return Response(status=200)


@app.route("/heartbeat", methods=['POST'])
def heartbeat():
    addr = request.json["addr"]
    term = request.json["term"]
    # logging.info(f"heartbeat_back from : {addr} for term : {term}")

    n.recv_heartbeat(addr, term)
    return Response(status=200)


@app.route("/heartbeat_back", methods=['POST'])
def heartbeat_back():
    addr = request.json["addr"]
    term = request.json["term"]
    # logging.info(f"heartbeat_back from : {addr} for term : {term}")

    n.recv_heartbeat_back(addr, term)
    return Response(status=200)


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
        app.run(host="0.0.0.0", port=int(port), debug=True)
    else:
        print("usage: python server.py index ip_list_file")
