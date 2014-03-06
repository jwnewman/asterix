from threading import Thread, RLock, Lock, Event

class Global:
    app = None
    medal_lock = Lock()
    score_lock = Lock()
    client_lock = Lock()

    # medal_event = Event()
    # score_event = Event()
    # client_event = Event()