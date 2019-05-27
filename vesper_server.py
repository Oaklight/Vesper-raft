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
    n.recv_vote(addr)
    return Response(status=200)
    # print(request.form)
    # return jsonify(request.form)


@app.route("/vote_req", methods=['POST'])
def vote_req():
    addr = request.json["addr"]
    term = request.json["term"]
    n.recv_vote_req(addr, term)
    return Response(status=200)


@app.route("/heartbeat_back", methods=['POST'])
def heartbeat_back():
    term = request.json["term"]
    n.recv_heartbeat_back(term)
    return Response(status=200)


if __name__ == "__main__":
    # python server.py index ip_list
    logging.basicConfig(format='[%(asctime)s][%(process)s]-%(message)s')
    if len(sys.argv) == 3:
        index = int(sys.argv[1])
        ip_list_file = sys.argv[2]
        ip_list = []
        with open(ip_list_file) as f:
            for ip in f:
                ip = ip.strip()
                ip_list.append(ip)
        ip_list = [
            "http://127.0.0.1:5000",
            "http://127.0.0.1:5001",
        ]
        my_ip = ip_list.pop(index)
        http, host, port = my_ip.split(':')
        # print(host, port)
        n = Node(ip_list, my_ip)
        logging.info(f"starting {port}")
        app.run(host="0.0.0.0", port=int(port), debug=True)
    else:
        print("usage: python server.py index ip_list_file")
