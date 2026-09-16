"""
UDP Echo Server
---------------
Receives datagrams from any client and sends each one straight back.
No connection setup is needed — every packet is handled independently.

Run:
    python udp_server.py

Then start udp_client.py in a separate terminal.
"""

import socket

HOST = ""        # listen on all interfaces
PORT = 65433     # different port from the TCP demo
BUFFER_SIZE = 1024

# SOCK_DGRAM = UDP (unreliable, connectionless)
# Each recvfrom() / sendto() call is one independent datagram.
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:

    # With UDP there is no listen() or accept() — just bind and receive.
    server_sock.bind((HOST, PORT))

    print(f"[UDP Server] Listening on port {PORT} ...")

    while True:
        # recvfrom() returns (data_bytes, client_address).
        # The server doesn't know who will send until a packet arrives.
        data, addr = server_sock.recvfrom(BUFFER_SIZE)

        print(f"[UDP Server] Received from {addr}: {data.decode()!r}")

        # sendto() sends the datagram directly to the client's address.
        # UDP has no persistent connection, so we always supply the address.
        server_sock.sendto(data, addr)

        print(f"[UDP Server] Echoed back to {addr}.")
