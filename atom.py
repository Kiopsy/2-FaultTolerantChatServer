import multiprocessing

class Counter:
    def __init__(self, val = 0):
        self.counter = multiprocessing.Value('i', val)
    
    def incr(self):
        with self.counter.get_lock():
            self.counter.value += 1
    
    def val(self):
        return self.counter.value