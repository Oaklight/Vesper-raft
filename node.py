import threading
import time
import utils
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
        self.commitIdx = 0
        self.t_t = None
        self.init_timeout()

    def incrementVote(self, voter):
        self.voteCount += 1
        if self.voteCount >= self.majority:
            self.status = LEADER
            self.startHeartBeat()

    def startElection(self):
        print(f"-----Starting ELECTION term: {self.term}")
        self.voteCount = 1
        self.term += 1
        self.status = CANDIDATE
        self.init_timeout()
        self.send_vote_req()

# ------------------------------
# ELECTION TIME CANDIDATE

    def send_vote_req(self):
        # TODO: use map later for better performance
        # we continue to ask to vote to the address that haven't voted yet
        # till everyone has voted
        # or I am the leader
        for voter in self.fellow:
            threading.Thread(target=self.ask_for_vote, args=(voter, )).start()

    def ask_for_vote(self, voter):
        # need to include self.commitIdx, only up-to-date candidate could win
        message = {"term": self.term, "commitIdx": self.commitIdx}
        route = "vote_req"
        while self.status != LEADER:
            reply = utils.send(voter, route, message)
            if reply:
                choice = reply.json()["choice"]
                print(f"RECEIVED VOTE {choice} from {voter}")
                if choice and self.status != LEADER:
                    self.incrementVote(voter)
                elif not choice:
                    # they declined because either I'm out-of-date or not newest term
                    # update my term
                    term = reply.json()["term"]
                    if term > self.term:
                        self.term = term
                    # fix out-of-date needed
                break

    def send_vote_req_non_threaded(self):
        # need to include self.commitIdx, only up-to-date candidate could win
        message = {"term": self.term, "commitIdx": self.commitIdx}
        route = "vote_req"
        # TODO: use map later for better performance

        # we continue to ask to vote to the address that haven't voted yet
        # till everyone has voted
        # or I am the leader

        voters = self.fellow[:]

        while len(self.remaining_voters) != 0 or self.status != LEADER:
            new_voters = []
            for voter in voters:
                reply = utils.send(voter, route, message)
                if reply:
                    choice = reply.json()["choice"]
                    print(f"RECEIVED VOTE {choice} from {voter}")
                    if choice and self.status != LEADER:
                        self.incrementVote(voter)
                else:
                    new_voters.append(voter)
            voters = new_voters

# ------------------------------
# ELECTION TIME FOLLOWER

    def decide_vote(self, term, commitIdx):
        # new election
        # decline all non-up-to-date candidate's vote request as well
        # but update term all the time, not reset timeout during decision
        if self.term < term and self.commitIdx <= commitIdx:
            # self.reset_timeout()
            self.term = term
            return True
        else:
            return False

# ------------------------------
# START PRESIDENT

    def startHeartBeat(self):
        self.initThreadPool()

    def initThreadPool(self):
        print("INIT THREADPOOL")
        for each in self.fellow:
            print(each)
            t = threading.Thread(target=self.send_heartbeat, args=(each, ))
            t.start()

    def send_heartbeat(self, follower):
        print("Starting HEARTBEAT")
        route = "heartbeat"
        while self.status == LEADER:
            message = {"term": self.term}
            start = time.time()
            reply = utils.send(follower, route, message)
            if reply:
                self.heartbeat_reply_handler(reply.json()["term"])
            delta = time.time() - start
            time.sleep((cfg.HB_TIME - delta) / 1000)

# /heartbeat_back

    def heartbeat_reply_handler(self, term):
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
        # print("RESET TIMEOUT")
        self.election_time = time.time() + utils.random_timeout()


# /heartbeat

    def heartbeat_follower(self, term):
        # weird case if 2 are PRESIDENT of same term.
        # both receive an heartbeat
        # we will both step down
        if self.term <= term:
            self.reset_timeout()
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
        return self.term

    def init_timeout(self):
        self.reset_timeout()
        print("---> INIT TIMEOUT")
        if self.t_t and self.t_t.isAlive():
            return
        self.t_t = threading.Thread(target=self.timeout_loop)
        self.t_t.start()

    def timeout_loop(self):
        while self.status != LEADER:
            delta = self.election_time - time.time()
            if delta < 0:
                self.startElection()
                break
            else:
                time.sleep(delta)
