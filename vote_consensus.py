import threading
import time
import utils
import sys

from config import cfg

FOLLOWER = 0
CANDIDATE = 1
LEADER = 2


class Node():
    def __init__(self, fellow):
        self.addr = f"{ip}:{port}"
        self.fellow = fellow
        self.term = 0
        self.status = FOLLOWER
        self.majority = len(self.fellow) / 2 + 1
        self.voteCount = 0
        self.init_timeout()

    def incrementVote(self):
        self.voteCount += 1
        if self.majority <= self.voteCount:
            self.status = LEADER
            self.startHeartBeat()

    def startElection(self):
        self.voteCount = 1
        self.term += 1
        self.status = CANDIDATE
        self.send_vote_req()
# ------------------------------
# ELECTION TIME CANDIDATE

    def send_vote_req(self):
        message = {"term": self.term}
        route = "vote_req"
        # TODO: use map later for better performance
        for each in self.fellow:
            utils.send(each, route, message)

# "/vote"

    def recv_vote(self):
        self.incrementVote()

# ------------------------------
# ELECTION TIME FOLLOWER

# "/vote_req"

    def recv_vote_req(self, addr, term):
        # new election
        if self.term < term:
            self.reset_timeout()
            self.term = term
            self.send_vote(True, addr, term)
        else:
            self.send_vote(False, addr, term)

    def send_vote(self, choice, candidate, term):
        message = {"term": self.term, "choice": choice}
        route = "vote"
        utils.send(candidate, route, message)

# ------------------------------
# START PRESIDENT

    def startHeartBeat(self):
        self.initThreadPool()

    def initThreadPool(self):
        thread_pool = list(map(utils.spawn_thread, self.fellow))

    def send_heartbeat(self, follower):
        route = "heartbeat"
        while self.status == LEADER:
            message = {
                "term": self.term,
            }
            utils.send(follower, route, message)
            time.sleep(cfg.HB_TIME)

    def recv_heartbeat_back(self, term):
        if self.term < term:
            self.status = FOLLOWER
            self.term = term


# ------------------------------
# FOLLOWER STUFF

    def reset_timeout(self):
        self.election_time = time.time() + utils.random_timeout()

    def recv_heartbeat(self, leader):
        self.reset_timeout()
        self.send_heartbeat_back(leader)

    def send_heartbeat_back(self, leader):
        route = "heartbeat_back"
        utils.send(leader, route)

    def init_timeout(self):
        t_t = threading.Thread(self.timeout_loop)
        t_t.start()

    def timeout_loop(self):
        while self.status != LEADER:
            if time.time() >= self.election_time:
                self.startElection()
            else:
                time.sleep(self.election_time - time.time())

if __name__ == "__main__":
    # python server.py index ip_list
    index = int(sys.argv[0])
    ip_list_file = sys.argv[1]
    ip_list = []
    with open(ip_list_file) as f:
        for ip in f:
            ip_list.append(ip)
    my_ip = ip_list.pop(index)
    n = Node(ip_list)
