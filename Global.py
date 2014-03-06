from threading import Thread, RLock, Lock

class Global:
    app = None
    medal_lock = Lock()
    score_lock = Lock()
    client_lock = Lock()
