# Multi-threaded Socket Programming

A TCP echo server that serves **many clients at once** by giving each connection its own thread.

## Start here: threading without sockets ([`threads_demo.py`](threads_demo.py))

Before the networking version, [`threads_demo.py`](threads_demo.py) shows the threading idea on its own. It dispatches five "jobs" to five worker threads; each one `time.sleep(5)`s to fake slow work. All five overlap, so the program finishes in ~5 seconds instead of ~25.

```
python threads_demo.py
```

It keeps the same bone structure as the server, just without the sockets:

| `threaded_server.py` | `threads_demo.py` |
|---|---|
| main thread: `accept()` | main thread: hand out jobs |
| worker: `handle_client()` | worker: `do_work()` |
| blocked in `recv()` | blocked in `time.sleep()` |

**What is `join()`?** Calling `worker.join()` makes the *current* thread wait until `worker` has finished. The main thread loops over every worker and joins each one, so it can't print "Done" — or exit — until all jobs are complete.
Without the joins, the main thread would race to the end of the script and the program could finish before the workers ever printed their results. (The server doesn't join its workers because it never wants to stop accepting clients.)

## The problem it solves

The single-threaded server in [`../socket-programming/tcp_server.py`](../socket-programming/tcp_server.py) handles one client at a time. While it is blocked inside `recv()` waiting for that client, any other client's `connect()` just sits in the OS backlog queue.

## The fix (threaded server, port 65434)

- The **main thread** does only one thing: loop on `accept()`.
- Every new connection is handed to a fresh **worker thread** running `handle_client()`, then the main thread loops back to `accept()` the next.
- A worker blocked in `recv()` blocks only *itself* — every other thread keeps running, so all clients are served concurrently.

```
python threaded_server.py    # terminal 1
python threaded_client.py    # terminal 2
python threaded_client.py    # terminal 3  (and as many more as you like)
```

The client is intentionally the same as the plain TCP client — concurrency is entirely the server's responsibility. Watch the server log: each client is labeled with its thread name (`Thread-1`, `Thread-2`, ...) to make the one-thread-per-client model visible.

## Thread-per-connection notes

| Detail | Why |
|---|---|
| `setsockopt(SO_REUSEADDR, 1)` | Lets the server rebind the port immediately after it stops, instead of waiting ~60s for the OS `TIME_WAIT` state to clear (avoids "Address already in use" on restart). |
| `daemon=True` | Worker threads don't block program exit; `Ctrl+C` quits even with clients connected. |
| `listen(5)` | Larger backlog: several clients may connect before each is handed to a thread. |
| `with conn:` inside the worker | Each thread owns its own socket and closes it on exit. |
| `active_count() - 1` | Counts live clients (subtract the main thread). |

**Scaling caveat:** one OS thread per connection is simple and great for learning, but it does not scale to thousands of clients (memory + context-switch cost). Production servers use a thread pool, or asynchronous I/O (`selectors` / `asyncio`) to multiplex many connections on a few threads.