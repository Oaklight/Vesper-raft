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

## Leader Status Behavior

Once the majority vote for a `CANDIDATE`'s `vote_req`, which is checked after every time the `voteCount` is incremented for receiving a positive vote, the campaigning node wins the election of its `term`, and assumes leadership immediately. The status switching to `LEADER` also terminates the remaining `vote_req` threads. Meanwhile, its `timeout` thread also goes out of scope.

### startHeartBeat

Immediately after assuming leadership, the node `startHeartBeat`. which first check whether there is anything staged not commited in the last `term`. This rarely happens only when the last `LEADER` runs into trouble sending commit confirmation to its followers. 

<!-- why we want to handle the uncommited but staged changes? -->
