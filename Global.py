from threading import Thread, RLock

class Global:
    app = None
    lock = RLock()
