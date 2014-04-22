"""Module for synchronization decorators used for locking."""

from threading import Thread, RLock, Event

def synchronized(lock):
    """@synchronized is a decorator for functions that acquires a locks. 
    Any function modifying shared data is decorated to make it thread-safe.

    Arguments:
    lock -- A threading.Lock object.
    """
    def wrap(f):
        def newFunction(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return newFunction
    return wrap

def synchronized_check(lock):
    """@synchronized_check is a decorator for functions that have to wait for lock releases.
    This is separate from @synchronized because somemethods shouldn't have to wait on eachother (e.g., get_medal_tally).
    
    Arguments:
    lock -- A threading.Lock object.
    """
    def wrap(f):
        def newFunction(*args, **kw):
            while(lock.locked()):
                pass
            return f(*args, **kw)
        return newFunction
    return wrap