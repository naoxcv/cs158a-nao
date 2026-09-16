"""
Multi-threading
------------------------------------
The threaded server (threaded_server.py) mixes two ideas: networking AND threads. This file strips the networking away so you can see the THREADING idea on its own. The bone structure is the same:

    server                     this demo
    ------                     ---------
    main thread: accept()  ->  main thread: hand out jobs
    worker: handle_client  ->  worker: do_work
    blocked in recv()      ->  blocked in time.sleep()

A "job" here is just a number. The worker "processes" it by sleeping for a moment (pretending to do slow work, exactly like recv() waits on the network) and then prints the result.

Run:
    python threads_demo.py
"""

import threading
import time

JOBS = [1, 2, 3, 4, 5]   # the "clients" — five pieces of work to do


def do_work(job):
    """Process one job. Runs in its own thread, just like handle_client().

    The time.sleep() stands in for any slow, blocking operation — a network
    recv(), a database query, reading a big file. While this thread sleeps,
    the OTHER worker threads keep running.
    """
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Starting job {job} ...")

    # Pretend the work takes a while. This BLOCKS only this thread.
    time.sleep(5)
    print(f"[{thread_name}] Finished job {job} -> result is {job * job}")


# --- Main thread: hand each job to its own worker thread ---------------------
print("[Main] Dispatching jobs ...")

threads = []

s = time.time()

for job in JOBS:
    # Spawn a worker thread for this job, then immediately loop to the next.
    # We do NOT wait for it to finish — that's what makes the work overlap.
    worker = threading.Thread(target=do_work, args=(job,))
    worker.start()
    threads.append(worker)

print(f"[Main] All {len(JOBS)} jobs dispatched. Active threads: {threading.active_count() - 1}")

# join() waits for a thread to finish. We join every worker so the main thread
# doesn't exit (and print "Done") until all jobs are complete.
for worker in threads:
    worker.join()

print(f'[Main] All jobs finished in {time.time() - s:.2f} seconds.')

print("[Main] Done — every job finished.")
