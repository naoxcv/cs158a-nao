"""
TCP Echo Server
---------------
Waits for a client to connect, echoes back every message it receives,
then waits for the next client.

Run:
    python tcp_server.py

Then start tcp_client.py in a separate terminal.
"""

import socket

HOST = ""        # empty string = listen on all network interfaces
PORT = 65432     # port to listen on (must match client)
BUFFER_SIZE = 1024

# AF_INET  = IPv4 address family
# SOCK_STREAM = TCP (reliable, connection-oriented)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:

    # Allow reusing the port immediately after the server stops.
    # Without this, you'd get "Address already in use" for ~60 seconds.
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to (host, port) so the OS knows where to send packets.
    server_sock.bind((HOST, PORT))

    # Start listening. The argument is the backlog: how many pending
    # connections the OS will queue while we're busy in accept().
    server_sock.listen(1)

    print(f"[TCP Server] Listening on port {PORT} ...")

    while True:  # outer loop: accept one client, then loop back for the next
        # accept() BLOCKS here until a client calls connect().
        # Returns a NEW socket (conn) dedicated to this client,
        # and the client's (ip, port) address.
        conn, addr = server_sock.accept()

        with conn:
            print(f"[TCP Server] Connected by {addr}")

            while True:  # inner loop: exchange messages with this client
                # recv() BLOCKS until data arrives (or the connection closes).
                # Returns bytes; empty bytes means the client disconnected.
                data = conn.recv(BUFFER_SIZE)

                if not data:
                    print(f"[TCP Server] Client {addr} disconnected.")
                    break

                # repr() gives the developer representation of an object 
                print(f"[TCP Server] Received: {data.decode()!r}")

                # sendall() sends all bytes, retrying internally if needed.
                conn.sendall(data)
                print(f"[TCP Server] Echoed back.")
