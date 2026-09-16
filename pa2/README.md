# Leader Election on an Asynchronous Ring

A single program that acts as both a client and a server and runs the
n^3 leader-election algorithm on an asynchronous, non-anonymous
ring. Each node receives from their predecessor and sends to its successor. 

## Files

| File                 | Purpose                                                        |
|----------------------|---------------------------------------------------------------|
| `myprocess.py` | The node program (client + server + election logic).          |
| `config.txt`         | Two lines: this node's `ip,port`, then the peer's `ip,port`.   |
| `log.txt`            | Created at runtime. Records `Received` / `Sent` / `Ignored`.   |

---

## Configuration

`config.txt` lives in the same directory as the code and has exactly two lines:

```
<my_ip>,<my_port>        # line 1: used as the SERVER (the node listen here)
<peer_ip>,<peer_port>    # line 2: used as the CLIENT (the node connects to here)
```

Example:

```
10.1.1.1,5001
10.1.1.2,5001
```

---

## How to run

### Requirements
- Python 3.

### In-class demo (two machines)
1. Exchange one `ip,port` pair with the student on each side of you.
2. Put your `ip,port` on line 1 of `config.txt` and your successor's on line 2.
3. Everyone runs:
   ```
   python3 myprocess.py
   ```
The program starts its server thread first, then once every server node is up and running 
the operator can press a key to run connect(). When the ring is complete the election runs
automatically and every node prints `leader is <id>`.


### Local test (one machine, three nodes)
Give each node its own folder so it has its own `config.txt` and `log.txt`.
Ring: `5001 -> 5002 -> 5003 -> 5001`.

```bash
mkdir -p n1 n2 n3
printf "127.0.0.1,5001\n127.0.0.1,5002\n" > n1/config.txt   
printf "127.0.0.1,5002\n127.0.0.1,5003\n" > n2/config.txt   
printf "127.0.0.1,5003\n127.0.0.1,5001\n" > n3/config.txt   
cp myprocess.py n1/ && cp myprocess.py n2/ && cp myprocess.py n3/
# IN SEPARATE TABS:
cd n1 && python3 myprocess.py
cd n2 && python3 myprocess.py
cd n3 && python3 myprocess.py
```

Each node's output goes to its terminal (and to its own `log.txt`).

---

## Execution example

Real output from a three-node local run. The three random IDs this run were:

| Node | Port map        | UUID                                   |
|------|-----------------|----------------------------------------|
| 1    | 5001 → 5002     | `e53087f6-e841-4016-91c0-4ca656ccef56` |
| 2    | 5002 → 5003     | `c5996714-9644-4e20-9d79-90b53548c1ab` |
| 3    | 5003 → 5001     | `566c4872-1671-4599-b7ca-043e6806c728` |

Node 1 holds the largest UUID, so it becomes the leader.

### Node 1 (own 5001 → peer 5002) — the winner
```
ID e53087f6-e841-4016-91c0-4ca656ccef56
[Server] listening on port 5001
[Server] connection from ('127.0.0.1', 49192)
[Client] connected to 127.0.0.1:5002
Received: uuid=566c4872-1671-4599-b7ca-043e6806c728, flag=0, less, 0
Sent: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=0
Received: uuid=c5996714-9644-4e20-9d79-90b53548c1ab, flag=0, less, 0
Received: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=0, same, 0
Leader is decided to e53087f6-e841-4016-91c0-4ca656ccef56.
leader is e53087f6-e841-4016-91c0-4ca656ccef56
Sent: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=1
Received: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=1, same, 1, leader=e53087f6-e841-4016-91c0-4ca656ccef56
```

### Node 2 (own 5002 → peer 5003)
```
ID c5996714-9644-4e20-9d79-90b53548c1ab
[Server] listening on port 5002
[Server] connection from ('127.0.0.1', 45276)
Received: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=0, greater, 0
[Client] connected to 127.0.0.1:5003
Sent: uuid=c5996714-9644-4e20-9d79-90b53548c1ab, flag=0
Sent: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=0
Received: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=1, greater, 0
leader is e53087f6-e841-4016-91c0-4ca656ccef56
Sent: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=1
```

### Node 3 (own 5003 → peer 5001)
```
ID 566c4872-1671-4599-b7ca-043e6806c728
[Server] listening on port 5003
[Client] connected to 127.0.0.1:5001
Sent: uuid=566c4872-1671-4599-b7ca-043e6806c728, flag=0
[Server] connection from ('127.0.0.1', 57222)
Received: uuid=c5996714-9644-4e20-9d79-90b53548c1ab, flag=0, greater, 0
Sent: uuid=c5996714-9644-4e20-9d79-90b53548c1ab, flag=0
Received: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=0, greater, 0
Sent: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=0
Received: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=1, greater, 0
leader is e53087f6-e841-4016-91c0-4ca656ccef56
Sent: uuid=e53087f6-e841-4016-91c0-4ca656ccef56, flag=1
```

All three nodes finish with the same `leader_id`
(`e53087f6-e841-4016-91c0-4ca656ccef56`) and stop sending

---

