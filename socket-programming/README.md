# Socket Programming Demo

Two echo server demos showing the difference between TCP and UDP.

## TCP Echo (port 65432)

- Client connects to server (3-way handshake)
- Client sends a message → server echoes it back
- Connection stays open for multiple messages
- Server detects when client disconnects

```
python tcp_server.py   # terminal 1
python tcp_client.py   # terminal 2
```

## UDP Echo (port 65433)

- No connection — client just sends a datagram
- Server echoes it back to whoever sent it
- Each message is independent (no session)
- Client times out after 2 seconds if no reply

```
python udp_server.py   # terminal 1
python udp_client.py   # terminal 2
```

## Key Difference

| | TCP | UDP |
|---|---|---|
| Connection | Required (`connect`) | None |
| Reliability | Guaranteed delivery | Best-effort |
| Send | `sendall(data)` | `sendto(data, addr)` |
| Receive | `recv(n)` | `recvfrom(n)` |

**`sendall` vs `send`:** `send()` may deliver only part of the data and returns the byte count — the caller must retry for the remainder. `sendall()` loops internally until every byte is sent (or raises on failure). Always prefer `sendall()` for TCP.

**`sendto`:** UDP has no connection, so the destination address must be passed on every call. Each call sends one self-contained datagram.

## TCP Message Boundaries

TCP is a **byte stream** — it has no concept of message boundaries. Even if `sendall()` sends `"hello world"` in one call, `recv()` may return it in pieces:

```
sendall(b"hello world")   →   recv() returns b"hello"
                               recv() returns b" world"
```

This can happen due to network fragmentation, OS buffering, or TCP segmentation. The demo works reliably because messages are small and sent over loopback, but production code must handle partial reads. Common solutions:

| Strategy | How it works |
|---|---|
| Fixed-length | Always send/recv exactly N bytes |
| Length prefix | Send message length first, then read that many bytes |
| Delimiter | Use a sentinel like `\n` and read until you see it |

UDP does **not** have this problem — `recvfrom()` always returns exactly one datagram, whole or not at all. This is because the UDP header contains a **Length field** that specifies the exact size of the datagram (header + data), so the receiver knows precisely how many bytes to read. TCP has no such field in its header. It is a raw byte stream and leaves message framing entirely to the application.
