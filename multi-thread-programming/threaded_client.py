"""
TCP Client for the Multi-threaded Echo Server
---------------------------------------------
Identical in spirit to ../socket-programming/tcp_client.py — the whole point is that the CLIENT doesn't change at all. Concurrency is the server's job.

Open several terminals and run this script in each one. They will all be
connected and echoed simultaneously, because the server gives every
connection its own thread.

Run:
    python threaded_client.py

Make sure threaded_server.py is already running first.
"""

import socket

HOST = "127.0.0.1"  # server address (localhost for local testing)
PORT = 65434        # must match threaded_server.py
BUFFER_SIZE = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    # connect() performs the TCP three-way handshake with the server.
    sock.connect((HOST, PORT))
    print(f"[Client] Connected to {HOST}:{PORT}")
    print("[Client] Type a message and press Enter. Type 'quit' to exit.\n")

    while True:
        message = input("You: ").strip()

        if message.lower() == "quit":
            print("[Client] Closing connection.")
            break

        if not message:
            continue

        # Send the message, then block until the server echoes it back.
        sock.sendall(message.encode())
        response = sock.recv(BUFFER_SIZE)

        print(f"Echo: {response.decode()}\n")
