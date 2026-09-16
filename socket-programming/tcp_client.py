"""
TCP Echo Client
---------------
Connects to the TCP echo server, sends lines of text, and prints
the server's response. Type 'quit' to exit.

Run:
    python tcp_client.py

Make sure tcp_server.py is already running first.
"""

import socket

HOST = "127.0.0.1"  # server address (localhost for local testing)
PORT = 65432        # must match tcp_server.py
BUFFER_SIZE = 1024

# Create the TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    # connect() performs the TCP three-way handshake with the server.
    # This call BLOCKS until the connection is established (or fails).
    sock.connect((HOST, PORT))
    print(f"[TCP Client] Connected to {HOST}:{PORT}")
    print("[TCP Client] Type a message and press Enter. Type 'quit' to exit.\n")

    while True:
        message = input("You: ").strip()

        if message.lower() == "quit":
            print("[TCP Client] Closing connection.")
            break

        if not message:
            continue

        # encode() encodes the string to bytes, and sendall() sends it to the server.
        sock.sendall(message.encode())

        # recv() BLOCKS until the server sends data back.
        response = sock.recv(BUFFER_SIZE)

        print(f"Echo: {response.decode()}\n")
