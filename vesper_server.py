from node import Node
from flask import Flask, request, jsonify
import sys
import logging
app = Flask(__name__)


def get_address(r):
    addr = r.environ["REMOTE_ADDR"]
    port = r.environ["REMOTE_PORT"]
    return str(addr) + ":" + str(port)


@app.route('/vote', methods=['GET'])
def vote():
    # n.recv_vote(request.remote_addr)
    # logging.info(request.remote_addr)
    print(get_address(request))
    return jsonify({"address": get_address(request)})


# @app.route('/vote', methods=['GET'])
# def vote():

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
        my_ip = ip_list.pop(index)
        http, host, port = my_ip.split(':')
        # print(host, port)
        n = Node(ip_list, my_ip)
        logging.info(f"starting {port}")
        app.run(host="0.0.0.0", port=int(port), debug=True)
    else:
        print("usage: python server.py index ip_list_file")
