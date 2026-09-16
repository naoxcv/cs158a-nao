"""
Multi-threaded TCP Echo Server
------------------------------
A single TCP server that handles many clients at the same time.

The single-threaded TCP server (../socket-programming/tcp_server.py) can only
talk to ONE client at a time: it sits inside recv() for that client, so a
second client's connect() just waits in the OS backlog queue until the first
one disconnects.

This version fixes that. The main thread does nothing but accept() new
connections. Each time a client connects, we hand its dedicated socket to a
brand-new worker thread and immediately loop back to accept() the next one.
While one worker is blocked in recv(), the others keep running.

Run:
    python threaded_server.py

Then start one or more threaded_client.py in separate terminals.
"""

import socket
import threading

HOST = ""        # empty string = listen on all network interfaces
PORT = 65434
BUFFER_SIZE = 1024


def handle_client(conn, addr):
    """Talk to one client until it disconnects. Runs in its own thread.

    Each call to this function owns a separate `conn` socket, so many copies
    can run concurrently without interfering with one another.
    """
    # threading.current_thread().name labels the log so you can SEE that
    # different clients are served by different threads.
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Connected by {addr}")

    # `with conn` guarantees the socket is closed when this client leaves,
    # whether through a normal disconnect or an exception.
    with conn:
        while True:
            # recv() BLOCKS this thread until data arrives. Crucially, it only
            # blocks THIS thread — the main thread and other workers run on.
            data = conn.recv(BUFFER_SIZE)

            if not data:
                # Empty bytes means the client closed the connection.
                print(f"[{thread_name}] Client {addr} disconnected.")
                break

            print(f"[{thread_name}] Received: {data.decode()!r}")

            # sendall() echoes every byte back, retrying internally if needed.
            conn.sendall(data)
            print(f"[{thread_name}] Echoed back to {addr}.")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:

    # Allow reusing the port immediately after the server stops.
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_sock.bind((HOST, PORT))

    # The backlog is larger here because we expect several clients to connect
    # in quick succession before each gets handed off to a thread.
    server_sock.listen(5)

    print(f"[Main] Listening on port {PORT} ... (multi-threaded)")

    try:
        while True:
            # The main thread does ONE job: accept connections. accept()
            # blocks until a client connects, then returns a fresh socket
            # dedicated to that client.
            conn, addr = server_sock.accept()

            # Spawn a worker thread to serve this client, then immediately
            # loop back to accept() the next one. daemon=True lets the program
            # exit on Ctrl+C without waiting for active clients to finish.
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            )
            client_thread.start()

            # active_count() includes the main thread, so subtract 1 to show
            # how many clients are currently being served.
            print(f"[Main] Active clients: {threading.active_count() - 1}")

    except KeyboardInterrupt:
        print("\n[Main] Shutting down.")
