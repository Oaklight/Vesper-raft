import threading
import time
import utils
import sys
from config import cfg

FOLLOWER = 0
CANDIDATE = 1
LEADER = 2


class Node():
    def __init__(self, fellow, my_ip):
        self.addr = my_ip
        self.fellow = fellow
        self.term = 0
        self.status = FOLLOWER
        self.majority = (len(self.fellow) / 2) + 1
        self.voteCount = 0
        self.t_t = None
        self.init_timeout()

    def incrementVote(self, voter):
        self.voteCount += 1
        print(f"number of vote received {self.voteCount}")
        # self.remaining_voters.remove(voter)
        if self.voteCount >= self.majority:
            print(
                f"{self.term} WIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIN"
            )
            self.status = LEADER
            self.startHeartBeat()

    def startElection(self):
        self.voteCount = 1
        self.term += 1
        self.status = CANDIDATE
        # self.remaining_voters = self.fellow[:]
        self.init_timeout()
        self.send_vote_req()
# ------------------------------
# ELECTION TIME CANDIDATE

    def send_vote_req(self):
        message = {"term": self.term, "addr": self.addr}
        route = "vote_req"
        # TODO: use map later for better performance

        # we continue to ask to vote to the address that haven't voted yet
        # till everyone has voted
        # or I am the leader

        # while len(self.remaining_voters) != 0 or self.status != LEADER:
        # for each in self.remaining_voters:
        #     utils.send(each, route, message)
        # time.sleep(0.5)
        for each in self.fellow:
            utils.send(each, route, message)

# "/vote"

    def recv_vote(self, voter_ip):
        if self.status != LEADER:
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

    def send_vote(self, choice, addr, term):
        message = {"term": self.term, "addr": self.addr, "choice": choice}
        route = "vote"
        utils.send(addr, route, message)

# ------------------------------
# START PRESIDENT

    def startHeartBeat(self):
        self.initThreadPool()

    def initThreadPool(self):
        # args = [(self.send_heartbeat, ip) for ip in self.fellow]
        # map(utils.spawn_thread, args)
        print("INIT THREADPOOL")

        for each in self.fellow:
            print(each)
            t = threading.Thread(target=self.send_heartbeat, args=(each, ))
            t.start()
            # threading.Thread(
            #     target=self.send_heartbeat,
            #     args=(each, ),
            # ).start

    def send_heartbeat(self, follower):
        print("sending HEARTBEAT")
        route = "heartbeat"
        while self.status == LEADER:
            # logging messages
            message = {
                "term": self.term,
                "addr": self.addr,
            }
            utils.send(follower, route, message)
            time.sleep(cfg.HB_TIME)

# /heartbeat_back

    def recv_heartbeat_back(self, adr, term):
        # i thought i was leader, but a follower told me
        # that there is a new term, so i now follow it
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

    def recv_heartbeat(self, addr, term):
        print("heartbeat_back")
        # weird case if 2 are PRESIDENT of same term.
        # both receive an heartbeat
        # we will both step down
        if self.term <= term:
            self.reset_timeout()
            self.send_heartbeat_back(addr)
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
            self.send_heartbeat_back(addr)

    def send_heartbeat_back(self, leader):
        route = "heartbeat_back"
        message = {
            "term": self.term,
            "addr": self.addr,
        }
        # TODO add a message with the log stuff
        utils.send(leader, route, message)

    def init_timeout(self):
        print("INIT TIMEOUT")
        if self.t_t and self.t_t.isAlive():
            return
        self.reset_timeout()
        self.t_t = threading.Thread(target=self.timeout_loop)
        self.t_t.start()

    def timeout_loop(self):
        while self.status != LEADER:
            delta = self.election_time - time.time()
            if delta < 0:
                self.startElection()
                break
            else:
                # print(f"SLEEP {delta}")
                time.sleep(delta / 10)
