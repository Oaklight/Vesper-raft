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
        self.fellow = fellow
        self.term = 0
        self.status = FOLLOWER
        self.majority = len(self.fellow) / 2 + 1
        self.voteCount = 0
        self.init_timeout()

    def incrementVote(self, voter):
        self.voteCount += 1
        self.remaining_voters.remove(voter)
        if self.majority <= self.voteCount:
            self.status = LEADER
            self.startHeartBeat()

    def startElection(self):
        self.voteCount = 1
        self.term += 1
        self.status = CANDIDATE
        self.remaining_voters = self.fellow[:]
        self.send_vote_req()
# ------------------------------
# ELECTION TIME CANDIDATE

    def send_vote_req(self):
        message = {"term": self.term}
        route = "vote_req"
        # TODO: use map later for better performance

        # we continue to ask to vote to the address that haven't voted yet
        # till everyone has voted
        # or I am the leader
        while len(self.remaining_voters) != 0 or self.status != LEADER:
            for each in self.remaining_voters:
                utils.send(each, route, message)

# "/vote"

    def recv_vote(self, voter_ip):
        self.incrementVote(voter_ip)

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
            # logging messages
            message = {
                "term": self.term,
            }
            utils.send(follower, route, message)
            time.sleep(cfg.HB_TIME)

# /heartbeat_back

    def recv_heartbeat_back(self, term):
        # i thought i was leader, but a follower told me that there is a new term, so i now follow it
        if term > self.term:
            self.term = term
            self.status = FOLLOWER
            self.init_timeout()

        # TODO logging replies

# ------------------------------
# FOLLOWER STUFF

    def reset_timeout(self):
        self.election_time = time.time() + utils.random_timeout()


# /heartbeat

    def recv_heartbeat(self, leader, term):
        # weird case if 2 are PRESIDENT of same term.
        # both receive an heartbeat
        # we will both step down
        if self.term <= term:
            self.reset_timeout()
            self.send_heartbeat_back(leader)
            # in case I am not follower
            # or started an election and lost it
            if self.status == CANDIDATE:
                self.status = FOLLOWER
            elif self.status == LEADER:
                self.status = FOLLOWER
                self.init_timeout()
            # i have missed a few messages
            if self.term < term:
                self.term = term
        else:
            # inform the poor leader that he is an old man
            self.send_heartbeat_back(leader)

    def send_heartbeat_back(self, leader):
        route = "heartbeat_back"
        message = {
            "term": self.term,
        }
        # TODO add a message with the log stuff
        utils.send(leader, route, message)

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
