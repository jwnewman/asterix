from threading import Thread, RLock, Lock

class Global:
    app = None
    lock = Lock()
