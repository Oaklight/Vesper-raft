# Vesper
a fault tolerant distributed Key value store using the raft consensus algorithm.

# Names and e-mail addresses of all the students in the group (first name alphabetical order)
Nicola Manzini nmanzini@uchicago.edu  
Peng Ding dingpeng@uchicago.edu

# A description of what each student worked on
we pair programmed the entire project.

# Concise instructions on how we should run your scripts 
## how to run SERVER
each server is initialized with an index and an ip_list.txt
```
usage: python3 server.py <id> <ip-list-file>
```

there is a file called `ip_list.txt` that has a list of ips of the servers, the consensus majority wil be calculated based on the number of servers(lines) in this file. make sure there are no empty lines!

```
http://127.0.0.1:5000
http://127.0.0.1:5001
http://127.0.0.1:5002
http://127.0.0.1:5003
http://127.0.0.1:5004
```

 example of 5 servers
```
➜  python3 server.py 0 ip_list.txt
➜  python3 server.py 1 ip_list.txt
➜  python3 server.py 2 ip_list.txt
➜  python3 server.py 3 ip_list.txt
➜  python3 server.py 4 ip_list.txt
```

## how to run the CLIENT
the client can perform `GET` and `PUT` request from the command line.
- the first argument is alwasy the http://ip:port of a functioning server
- the second is the key
- the third is optional and is a value
  - if the value is present the client performs a `PUT` request with key and value to the specified server
  - if the value is not present the client perform a `GET` request of the key to the specified server

```
PUT usage: python3 client.py 'address' 'key' 'value'
GET usage: python3 client.py 'address' 'key'
Format: address: http://ip:port
```

example of PUT key="name" , value="Kyle Chard"
```
➜  python3 client.py http://127.0.0.1:5000 name "Kyle Chard"
{'code': 'success'}
```
example of GET key="name" 
```
➜  python3 client.py http://127.0.0.1:5000 name 
{'code': 'success', 'payload': {'key': 'name', 'value': 'Kyle Chard'}}
```

# References
- https://raft.github.io/raft.pdf
- https://raft.github.io/
- https://github.com/ongardie/raftscope
- http://thesecretlivesofdata.com/raft/
- http://flask.pocoo.org/docs/1.0/

# Python requirements
packages used in this project, they are all standard python packages.
- sys
- logging
- flask
- time
- threading
- random
- requests
