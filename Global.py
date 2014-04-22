from threading import Thread, RLock, Lock, Event

# This class contains the three locks for the important functions and data structures that we do not want to be modified
# and accessed at the same time.

class Global:
    app = None
    medal_lock = Lock()
    score_lock = Lock()
    client_lock = Lock()
    raffle_lock = Lock()