# Interaction with the client
## get request
- if we are the leader: we access the store and reply with key and value
- if we are a follower: we reply with the ip address of the leader
- if we are a candidate we reply with a failure, it means an election is going on and we do not know who is the leader right now

## put request
- if we are the leader: we start the process of log replication and we reply positively once a majority of followershas added this update to their log, more details in the [Log Replication paragraph](#log-replication) 
- if we are a follower: we reply with the ip address of the leader
- if we are a candidate we reply with a failure, it means an election is going on and we do not know who is the leader right now

# Log Replication
this is the most complicated part of the project, after much studying and talking with TA and PROFESSOR we decided to go for this approach. 

Once a put request is received we call the function `def handle_put(self, payload):` passing the payload.

here we perform these action:
- acquire `self.lock`: we perform only une update at a time.
- store this new update in `self.staged`: temporarily store this update.
- create a message `log_message` for all the follower with the order to stage it ( temporarily store the update till it receives a request to commit).
- create `log_confirmations` to count how many follower accepted the request (we will confirm back to the client only if a majority has accepted the update).
- start a thread with the function `self.spread_update` to send `log_message` to all the followers, each positive request is logged in `log_confirmations`.
- while the thread is telling the follower to update we continuously check if we reached a majority of confirmations by counting the positive answers in `log_confirmations`:
  - if we do not reach it after `cfg.MAX_LOG_WAIT` millisecond we `return False` a failure to the client and we do not proceed with the commit process, hence in the next update `self.staged` will be overwritten adn forgotten by the LEADER and its follower. we releas the lock before returning, so we can accept new updates
  - if we reach a majority in less than `cfg.MAX_LOG_WAIT` millisecond we proceed with the committing process.
  - `cfg.MAX_LOG_WAIT` is a sort of server side timeout in case a majority is not reached .
- we continue if a majority of confirmations is reached, we call `self.commit()` to add our staged update to our definitive store `self.DB`.
- we create the message `commit_message` for all the follower with the order to commit the last update, if they have nothing in staged there is a copy of the original payload so they can commit that directly. after a request is sent to every follower (active or crashed) we release the lock to then allow for a new `POST` request to be satisfied
- start a thread with the function `self.spread_update` to send `commit_message` to all the followers.
- we return a positive message `return True` to the `client`.

# Fault Tolerant Replication
we have to support fail-stop failures only (i.e., nodes do not recover from failure).
hence we have a few possibilities:
- Follower crashes: 
  - if we still have a majority of servers anymore : we continue as usual.
  - if we don't have a majority of server active anymore : we will not be able to `POST` updates anymore to the KV store because it will be impossible to reach a majority of confirmations from the followers.
- Leader crashes:
  - NOT DURING A LOG REPLICATION: a CANDIDATE will start an election, all the other FOLLOWER will have the same state as the CANDIDATE so the Leadership with smoothly pass to a new server that has the same state as his new follower. this is a simple case
  - DURING A LOG REPLICATION: harder situation to analyze we have to guarantee that the new LEADER winning the election will have the most updated state as specified in the Raft paper section 5.4, also this state has to be congruent with what the client reply that the client received.

# Leader fail-stop while replicating the log

as described in the [Log Replication paragraph](#log-replication)  we perform a `staging` operation to the leader and follower(temporarly logging the update in `self.staged`). if we receive a majority of consensus we perform the `committing` operation to the leader and follower (save the update to `self.DB`). each single `POST` operation is atomic because we lock before the staging operation and we release after the committing. this atomicity makes it easier to prove the fault tolerance during the log replication.

if the client receive a success update, we make sure that the new leader will have that update and log it in the right order.

The Leader might crash in these moments:
- after receiving the request, before sending messages to the followers:
  - the client will not receive a success/failure, instead it will receive a `requests.exceptions.ConnectionError:`
  - the update has not been communicated to other followers so the next leader is safe
- while sending the `staging` messages but before reaching a majority of confirmations:
  - the client wil not receive a success/failure, instead it will receive a `requests.exceptions.ConnectionError:`
  - the update has been communicated to less than majority other followers so a minority of follower have the update. here we have to decide who to elect, RAFT tells us in section 5.4 to vote as a new leader the most updated version, and we do that in `decide_vote` we check for `commitIdx` and the state of the `staged`, we try to vote for server with a `>= commitIdx` than us and same or more updated version of `staged`
  - I talked long with the PROFESSOR and we decided to go with what the raft recommended, let the most updated follower win. the problem is that a follower might vote for a candidate with its own level of updatedness not knowing yet there are more updated candidates. the outcome of this election is unpredictable
- while sending the `staging` messages after reaching a majority of confirmations:
  - the client wil receive a success
  - the update reached a majority of server, we always vote for the most updated one so an updated follower will win the election. it will take care to give it to all the followers and try to commit it.
- between the `staging` and `committing`:
  - the client already received a success
  - the new leader will have the update in `self.staged` and will push it to the followers
- during the `committing` but without a majority of follower committing it:
  - the client already received a success
  - the majority hasn't committed the update yet: we vote for the most updated commitidx but there is a chance that
  - TODO: handle safely this option
- during the `committing` without a majority of follower committing it:
  - the client already received a success
  - the new leader will have a the committed index and will make all the follower without the update commit it with a call to update_follower_commitIdx
- after the `committing`:
  - the client already received a success
  - all the follower will have the update commited so the state is stable.



as soon as a server wins the election it checks 2 options:
- if it has an element in `self.staged`: it will push it to all the new followers and then make them commit them if a majority of consensus is reached. done in `def startHeartBeat`.
- it will query each follower for their commitIdx and if it is lower it will give them  the update they lack. done in `update_follower_commitIdx`

