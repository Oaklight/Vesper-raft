import threading

FOLLOWER = 0
CANDIDATE = 1
LEADER = 2


class Node():
    def __init__(self, ip, port, id):
        self.id = id
        self.addr = f"{ip}:{port}"
        self.fellow = {}

        self.term = 0
        self.status = FOLLOWER

        self.voted = False
        self.majority = len(self.fellow) / 2 + 1
        self.voteCount = 0
        # self.fellow[self.id] = None

        return self

    def incrementVote(self):
        self.voteCount += 1
        if self.majority <= self.voteCount:
            self.status = LEADER
            self.startHeartBeat()

    def startElection(self):
        self.incrementVote()
        self.term += 1
        self.voted = True
        self.vote4Me()
        self.status = CANDIDATE

    def vote4Me(self):
        url = "vote4Me{self.term}"
        # use map later for better performance
        for each in self.fellow.values():
            utils.send(each, url)

    def vote(self, choice, candidate, term):
        url = f"vote4U{self.term}{choice}"
        utils.send(candidate, url)

    def vote4U(self, addr, term):
        # new election
        if self.term < term:
            self.term = term
            self.voted = True
            self.vote(True, addr, term)
        else:
            self.vote(False, addr, term)

    def startHeartBeat(self):
        self.initThreadPool(len(self.fellow.keys()))

    def initThreadPool(self, size):
        pass

    def heartbeat(self, follower):
        while self.status == LEADER:
            hbMsg = {
                "term": self.term,
            }
            utils.send(follower, hbMsg)