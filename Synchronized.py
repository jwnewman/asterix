from threading import Thread, RLock, Event

# This wrapper wraps around functions that actually acquire locks. Any function that modifies data will acquire a lock so that no two threads
# can enter this function at once.
def synchronized(lock):
    def wrap(f):
        def newFunction(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return newFunction
    return wrap

# This wrapper wraps around functions that must simply wait until a lock is released. The reason for having two different functions is that
# we want methods like get_medal_tally to be able to be accessed asynchronously, UNLESS data modification is happening. This prevents inconsistency.
def synchronized_check(lock):
    def wrap(f):
        def newFunction(*args, **kw):
            while(lock.locked()):
                pass
            return f(*args, **kw)
        return newFunction
    return wrap
