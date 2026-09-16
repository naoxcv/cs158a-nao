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
Give each node its own folder (and ideally its own terminal, so you can press
Enter in each). Ring: `5001 -> 5002 -> 5003 -> 5001`.
 
```bash
mkdir -p n1 n2 n3
printf "127.0.0.1,5001\n127.0.0.1,5002\n" > n1/config.txt   # node 1 -> node 2
printf "127.0.0.1,5002\n127.0.0.1,5003\n" > n2/config.txt   # node 2 -> node 3
printf "127.0.0.1,5003\n127.0.0.1,5001\n" > n3/config.txt   # node 3 -> node 1
cp myprocess.py n1/ && cp myprocess.py n2/ && cp myprocess.py n3/
```
 
Then, in three separate terminals:
 
```bash
cd n1 && python3 myprocess.py      # terminal 1
cd n2 && python3 myprocess.py      # terminal 2
cd n3 && python3 myprocess.py      # terminal 3
```
 
When all three show `press Enter when everyone is ready.`, press Enter in each.
Each node's output goes to its terminal (and to its own `log.txt`).
 
---
 
## Execution example
 
A three-node run on one machine (three terminals, ports
5001–5003). Each node printed `press Enter when everyone is ready.`; once all
three were up, Enter was pressed in each. The three random IDs this run were:
 
| Node | Port map        | UUID                                   |
|------|-----------------|----------------------------------------|
| 1    | 5001 → 5002     | `005ed8a0-f1db-4913-9765-57852757de37` |
| 2    | 5002 → 5003     | `13e63818-457e-4c41-99e0-ce156199f67a` |
| 3    | 5003 → 5001     | `77f695c4-b3bc-47b5-963d-3f31b55c64cf` |
 
Node 3 holds the largest UUID, so it becomes the leader.
 
### Node 1 (own 5001 → peer 5002)
```
ID 005ed8a0-f1db-4913-9765-57852757de37
[Server] listening on port 5001
press Enter when everyone is ready.
[Server] connection from ('127.0.0.1', 61383)
Received: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=0, greater, 0
[Client] connected to 127.0.0.1:5002
Sent: uuid=005ed8a0-f1db-4913-9765-57852757de37, flag=0
Sent: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=0
Received: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=1, greater, 0
leader is 77f695c4-b3bc-47b5-963d-3f31b55c64cf
Sent: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=1
```
 
### Node 2 (own 5002 → peer 5003)
```
ID 13e63818-457e-4c41-99e0-ce156199f67a
[Server] listening on port 5002
press Enter when everyone is ready.
[Client] connected to 127.0.0.1:5003
Sent: uuid=13e63818-457e-4c41-99e0-ce156199f67a, flag=0
[Server] connection from ('127.0.0.1', 61387)
Received: uuid=005ed8a0-f1db-4913-9765-57852757de37, flag=0, less, 0
Received: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=0, greater, 0
Sent: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=0
Received: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=1, greater, 0
leader is 77f695c4-b3bc-47b5-963d-3f31b55c64cf
Sent: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=1
```
 
### Node 3 (own 5003 → peer 5001) — the winner
```
ID 77f695c4-b3bc-47b5-963d-3f31b55c64cf
[Server] listening on port 5003
press Enter when everyone is ready.
[Client] connected to 127.0.0.1:5001
Sent: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=0
[Server] connection from ('127.0.0.1', 61386)
Received: uuid=13e63818-457e-4c41-99e0-ce156199f67a, flag=0, less, 0
Received: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=0, same, 0
Leader is decided to 77f695c4-b3bc-47b5-963d-3f31b55c64cf.
Sent: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=1
Received: uuid=77f695c4-b3bc-47b5-963d-3f31b55c64cf, flag=1, same, 1
leader is 77f695c4-b3bc-47b5-963d-3f31b55c64cf
```
 
All three nodes finish with the same `leader_id`
(`77f695c4-b3bc-47b5-963d-3f31b55c64cf`) and stop 
---

