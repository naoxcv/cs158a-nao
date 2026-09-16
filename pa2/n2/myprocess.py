import sys
import json
import uuid
import time
import queue
import socket
import threading

# This node is both a server and a client.
#   - a server thread waits for its upstream neighbor to connect, then receives the message.
#   - a client thread connects to its downstream neighbor, then sends the initial message + messages queued by the server thread.
# 
# config.txt (same directory as the code):
#   line 1 = my ip,port          (used as the server)
#   line 2 = the peer's ip,port  (the server I connect to as a client)

BUFFER_SIZE = 1024
CONFIG_FILE = "config.txt"
LOG_FILE    = "log.txt"


class Message:
    def __init__(self, msg_uuid, flag=0):
        self.uuid = msg_uuid          # a uuid.UUID (sender's id)
        self.flag = flag              # 0 = election ongoing, 1 = leader elected

    def to_json(self):
        return json.dumps({"uuid": str(self.uuid), "flag": self.flag})

    @staticmethod
    def from_dict(d):
        return Message(uuid.UUID(d["uuid"]), int(d["flag"]))


MY_UUID   = uuid.uuid4()             # this node's id, fixed for the whole run
leader_id = None                     # str once known
state     = 0                        # 0 = still electing, 1 = knows the leader

outbox    = queue.Queue()            # Messages the client must send
done      = threading.Event()        # set when this node should stop
listening = threading.Event()        # set once our server socket is listening
log_lock  = threading.Lock()


def log(line):
    with log_lock:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    print(line, flush=True)


def compare(other_uuid):
    if other_uuid > MY_UUID:
        return "greater"
    if other_uuid < MY_UUID:
        return "less"
    return "same"


def shutdown():
    """Stop the node: unblock the client and let threads/main exit."""
    done.set()
    outbox.put(None)                 # sentinel for outbox.get()


def handle(msg):
    """O(n^2) algorithm"""
    global leader_id, state

    comp = compare(msg.uuid)

    # log every receive with current state
    log(f"Received: uuid={msg.uuid}, flag={msg.flag}, {comp}, {state}")

    # leader already announced (flag == 1)
    if msg.flag == 1:
        leader_id = str(msg.uuid)
        state = 1
        if msg.uuid == MY_UUID:
            # the announcement travelled the whole ring back to the leader: stop
            print(f"leader is {leader_id}", flush=True)
            shutdown()
        else:
            print(f"leader is {leader_id}", flush=True)
            outbox.put(Message(msg.uuid, 1))     # pass the announcement along once
            shutdown()
        return

    # still electing (flag == 0)
    if state == 1:
        # already know the leader; drop stray election traffic
        return

    if comp == "greater":
        outbox.put(Message(msg.uuid, 0))         # forward the larger id
    elif comp == "less":
        pass                                    # ignore smaller id
    else:  # same = this node is the leader
        leader_id = str(MY_UUID)
        state = 1
        log(f"Leader is decided to {leader_id}.")
        outbox.put(Message(MY_UUID, 1))          # announce with flag = 1


# server
def server(my_port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", my_port))
    srv.listen(1)
    log(f"[Server] listening on port {my_port}")
    listening.set()                              # main can show the connect barrier now

    conn, addr = srv.accept()                    # upstream neighbor connects once
    log(f"[Server] connection from {addr}")

    decoder = json.JSONDecoder()
    buffer = ""
    with conn:
        while not done.is_set():
            data = conn.recv(BUFFER_SIZE)
            if not data:
                log("[Server] upstream disconnected")
                break
            buffer += data.decode()
            while buffer.strip() and not done.is_set():
                buffer = buffer.lstrip()
                try:
                    obj, idx = decoder.raw_decode(buffer)
                except json.JSONDecodeError:
                    break                        # incomplete; wait for more bytes
                buffer = buffer[idx:]
                handle(Message.from_dict(obj))  #json to message and handle it


# client
def connect_to_peer(peer_host, peer_port):
    # connect once, after the manual barrier. if the neighbor is not up yet,
    # say so and let the user press Enter to try again (still key-press driven)
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((peer_host, peer_port))
            return sock
        except OSError as e:
            sock.close()
            print(f"[Client] could not reach {peer_host}:{peer_port} ({e}).")
            input("press Enter to try connecting again. ")


def client(peer_host, peer_port):
    sock = connect_to_peer(peer_host, peer_port)
    log(f"[Client] connected to {peer_host}:{peer_port}")

    # initial message: my own uuid, sent exactly once, no comparison
    initial = Message(MY_UUID, 0)
    sock.sendall(initial.to_json().encode())
    log(f"Sent: uuid={initial.uuid}, flag={initial.flag}")

    # forward whatever the server thread puts in the outbox
    while True:
        msg = outbox.get()
        if msg is None:                          # shutdown sentinel
            break
        sock.sendall(msg.to_json().encode())
        log(f"Sent: uuid={msg.uuid}, flag={msg.flag}")


# main
def read_config():
    with open(CONFIG_FILE) as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    parsed = []
    for ln in lines[:2]:
        ip, port = ln.split(",")
        parsed.append((ip.strip(), int(port.strip())))
    return parsed


def main():
    cfg = read_config()
    (_, my_port)             = cfg[0]            # my server line
    (peer_host, peer_port)   = cfg[1]            # the peer I connect to

    log(f"ID {MY_UUID}")                         # log our id first, on start

    threading.Thread(target=server, args=(my_port,), daemon=True).start()
    listening.wait()                            # our server socket is up
    # manual barrier: everyone binds first, then connects together on Enter
    input("press Enter when everyone is ready. ")
    client(peer_host, peer_port)
if __name__ == "__main__":
    main()