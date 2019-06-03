# REPORT
this is the report.

# Interaction between client and server
the client interects with the client with an http request to the route `/request` using the mandated json format as a body of the request.
## `GET` request
`@app.route("/request", methods=['GET'])`
- if we are the leader: we access the store and reply with key and value
- if we are a follower: we reply with the ip address of the leader, the clients automatically retries to send the same request to the leader
- if we are a candidate we reply with a failure, it means an election is going on and we do not know who is the leader right now.

## `GET` reply
- if the key is present in the storage a `code`:`success` is returned, with a payload of `key` and `value`
- else a `code`:`fail` is returned with no payload

## `PUT` request
`@app.route("/request", methods=['PUT'])`
- if we are the leader: we start the process of log replication and we reply positively once a majority of followers has added this update to their log, more details in the [Log Replication paragraph](#log-replication) 
- if we are a follower: we reply with the ip address of the leader, the clients automatically retries to send the same request to the leader
- if we are a candidate we reply with a failure, it means an election is going on and we do not know who is the leader right now.

## `PUT` reply
- if the key is successfully inserted in the key value store a `code`:`success` is returned, with no payload
- else a `code`:`fail` is returned with no payload

# election

## Node Initialization

Upon creation of each server node, we set the node `status` as `FOLLOWER` first, and initiate the `commitIdx` and `voteCount` to 0. At the end of all initiation, we call `init_timeout` to trigger the first timeout.

## Timeout behavior (only for non-leader status)

### when

- to timeout:

    Whenever a node assumes status of either `FOLLOWER` or `CANDIDATE`. Timeout should be either reset or initiated whenever one node in such two status receives a `HEARTBEAT` or a `LEADER` node `step down` from leadership.

- not to timeout:
    
    Whenever a node assumes the `LEADER` status.

### `init_timeout`

Every time the function is called, we `reset_timeout` first, which is just assigning the next `election_time` to a random future time.

Since the timeout should always be carried out in a standalone thread. We must check if that timeout thread is still alive or already run out of scope due to the node's winning of previous election and becoming a `LEADER` node. Therefore, a new timeout thread should always been spawned once we found the old one is gone.

### `timeout_loop`

The timeout thread executing this function only when itself assumes a non-leader status, which means even if it starts to running campaign for its election, the timeout is still running, in case that it might fail and falls back to the `FOLLOWER` status.

## Candidate Status Behavior

### `startElection`

Once a node times out before anything (either a heartbeat or vote request from other nodes) arrives, it starts the campaign to run for a `LEADER` status, during which it first resets its `term` to 0, and switch its status to `CANDIDATE`. Immediately after all of these, it initializes a new timeout, and votes for itself using `incrementVote`. Then it calls `send_vote_req` to ask for its peers' opinions.

### `send_vote_req`

We would like the vote requests running in parallel, so that the votes can be sent across more efficiently, and any failure to request one server does not compromise the requests to others. Threads are spawned running `ask_for_vote` with the `CANDIDATE`'s current election `term` passed through.

### `ask_for_vote`

Vote-request thread prepares the message comprising of the `CANDIDATE`'s `term`, `commitIdx`, and current `staged` changes. In most of the time, `self.staged` should remain `None`. If in any case there is anything, it means that there is something left staged but not commited due to the previous `LEADER` node's failure before / during sending commit confirmation, or any network linking problems.

After the message prepared, the node should first check if it still a `CANDIDATE`, and whether its current `term` remains the same because there might be some other node already won the election or has a higher version of `term` due to various reasons (e.g. partition, etc.), then the local term would be updated accordingly. 

While they all look good, the thread keeps sending out request to a specific `voter` and waits for its reply. The `utils.send` function has a timeout in case that a network latency or failure which could potentially permanently blocks the thread. And if within the timeout there is something coming back, the thread will check the `voter`'s choice (granted or not) and if it's a granted vote, and its `CANDIDATE` status still remains, it bumps up the vote counter by 1.

If a `voter` declines the vote request, the reason is either the `CANDIDATE`'s `term` is outdated, or its log is outdated, or their uncommited staged changes does not agree. In case of the outdated `term`, the thread checks the `voter`'s `term` in the replied message, update if it finds a more advanced version and fall back to `FOLLOWER` status. Stop requesting to a voter once it replies, no matter what `choice` it makes.

## Follower Status Behavior

### `decide_vote`

One follower should only decide to vote for a `vote_req` when all of the following criteria satisfied:

- `self.term` is not more advanced than that of the `CANDIDATE`.
- `self.commitIdx` is not more advanced than that of the `CANDIDATE`.
- `self.staged` is not more advanced than that of the `CANDIDATE`. (usually both of `self.staged` and the `CANDIDATE`'s `staged` should be `None`)

When a node responds to the vote request, apart from granted or not, `self.term` should always be returned in case of itself sitting in a more advanced `term`.

### `heartbeat_follower`

After some node becomes the `LEADER`, the follower nodes will receive heartbeat every `cfg.HB_TIME` seconds. Worth to mention that any node in any status could receive heartbeat, and they should behave accordingly. First, if the `term` embedded in the heartbeat is not updated enough, it should be replied with the updated `term` and thus the outdated leader can step down. Otherwise, the timeout is reset because at any time, there could only be one **true** `LEADER`, the one with the more "updated" `term`, given there are multiple node in `LEADER` status. After reset timeout, the status should always be `FOLLOWER`, and the `term` should be updated to the one in the heartbeat message if they should disagree (`term` in message can only be greater if this step is executed.) Then if there is any `action` embedded in the heartbeat, meaning there is a request to respond to. Either it is a "log" message, to put the `payload` into `self.staged` or it is a "commit" message, to execute the `payload` staged already. Should there be a network failure or latency, etc. that the previous "log" message did not make through, the follower should always catch up to stage the `payload` and then commit it.

### `commit`

For `LEADER` node, this only happens after the majority of its `FOLLOWER`s reply (they only reply when they staged the changes). And for `FOLLOWER` or `CANDIDATE` (which should fall back to `FOLLOWER` once receive heartbeat with higher `term`) executes its staged payload (if previous "log" message arrived) or the payload in commit confirmation heartbeat (should the "log" do not make it at first place.)

## Leader Status Behavior

Once the majority vote for a `CANDIDATE`'s `vote_req`, which is checked after every time the `voteCount` is incremented for receiving a positive vote, the campaigning node wins the election of its `term`, and assumes leadership immediately. The status switching to `LEADER` also terminates the remaining `vote_req` threads. Meanwhile, its `timeout` thread also goes out of scope.

### startHeartBeat

Immediately after assuming leadership, the node `startHeartBeat`. which first check whether there is anything staged but not commited in the last `term`. This rarely happens only when the last `LEADER` runs into trouble sending commit confirmation to its followers, or package lost during the transmission.

<!-- why we want to handle the uncommited but staged changes? -->
We would like to handle the staged changes because, if there is anything in the staged but not commited, which suggests one possible scenario where, in the last `term`, the `LEADER` passed the changes to the majority of its followers and received first batch of confirmations. So it commited its staged change to its local DB, and spawned threads to send commit confirmation to the followers. And it replied to the client with the confirm message saying the request was done, however, the spawned threads somehow did not make it to inform all the follower, even more extremely, none of them got the commit confirmation. Then there is a discrepency between the client status and those of the majority of server nodes. To settle this possible scenario, we should always write the staged but uncommitted changes at the beginning of one's leadership.

After the staged changes is properly handled, given there is any, the `LEADER` should spawn threads to `send_heartbeat` to all its followers.

### `send_hearbeat`

In most cases, we should first check all the followers' `commitIdx`, in case there were some of them are not updated enough. This is achieved by `update_follower_commitIdx`, in which the first heartbeat message is a probing to all its followers' current `term`.
If they are outdated, at most 1 step behind. The `LEADER` informs the node of the missing log value and ask it to update the transaction.

This is a fault-tolerant step so that if there was a partition causing some follower's term is actually higher than the `LEADER`, which potentially means the `LEADER` was down or segregated for a while and some other node now is leading the consensus, the old `LEADER` can be notified and voluntarily "steps down".

All the later heartbeat messages only includes the `LEADER`'s `term` (in case of "outdated follower") and the address (for communication). `FOLLOWER`s also reply with their `term` (in case of "outdated leader"). Heartbeat is sent every `cfg.HB_TIME` seconds.

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
  - if we do not reach it after `cfg.MAX_LOG_WAIT` millisecond we `return False` a failure to the client and we do not proceed with the commit process, hence in the next update `self.staged` will be overwritten adn forgotten by the LEADER and its follower. we release the lock before returning, so we can accept new updates
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

## Leader fail-stop while replicating the log

as described in the [Log Replication paragraph](#log-replication)  we perform a `staging` operation to the leader and follower(temporarily logging the update in `self.staged`). if we receive a majority of consensus we perform the `committing` operation to the leader and follower (save the update to `self.DB`). each single `POST` operation is atomic because we lock before the staging operation and we release after the committing. this atomicity makes it easier to prove the fault tolerance during the log replication.

if the client receive a success update, we make sure that the new leader will have that update and log it in the right order.

The Leader might crash in these moments:
- after receiving the request, before sending messages to the followers:
  - the client will not receive a success/failure, instead it will receive a `requests.exceptions.ConnectionError:`
  - the update has not been communicated to other followers so the next leader is safe
- while sending the `staging` messages but before reaching a majority of confirmations:
  - the client wil not receive a success/failure, instead it will receive a `requests.exceptions.ConnectionError:`
  - the update has been communicated to less than majority other followers so a minority of follower have the update. here we have to decide who to elect, RAFT tells us in section 5.4 to vote as a new leader the most updated version, and we do that in `decide_vote` we check for `commitIdx` and the state of the `staged`, we try to vote for server with a `>= commitIdx` than us and same or more updated version of `staged`
  - I talked long with the PROFESSOR and we decided to go with what the raft recommended, let the most updated follower win. the problem is that a follower might vote for a candidate with its own level of updated-ness not knowing yet there are more updated candidates. the outcome of this election is unpredictable
- while sending the `staging` messages after reaching a majority of confirmations:
  - the client wil receive a success
  - the update reached a majority of server, we always vote for the most updated one so an updated follower will win the election. it will take care to give it to all the followers and try to commit it.
- between the `staging` and `committing`:
  - the client already received a success
  - the new leader will have the update in `self.staged` and will push it to the followers
- during the `committing` but without a majority of follower committing it:
  - the client already received a success
  - the majority hasn't committed the update yet: we vote for the most updated commitidx but there is a chance that a group of non commited followers vote for one of their own without having seen the committed Candidate. we fix this situation by discarding the commit request by Leaders with a commitIdx lowers than ours
  - TODO: handle safely this option
- during the `committing` without a majority of follower committing it:
  - the client already received a success
  - the new leader will have a the committed index and will make all the follower without the update commit it with a call to update_follower_commitIdx
- after the `committing`:
  - the client already received a success
  - all the follower will have the update committed so the state is stable.



as soon as a server wins the election it checks 2 options to sync itself with the followers:
- if it has an element in `self.staged`: it will push it to all the new followers and then make them commit them if a majority of consensus is reached. done in `def startHeartBeat`.
- it will query each follower for their commitIdx and if it is lower it will give them  the update they lack. done in `update_follower_commitIdx`

