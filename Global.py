from threading import Thread, RLock, Lock, Condition

class Global:
    app = None
    medal_lock = Lock()
    score_lock = Lock()
    client_lock = Lock()
    
    medal_condition = Condition(medal_lock)
    score_condition = Condition(score_lock)
    client_condition = Condition(client_lock)