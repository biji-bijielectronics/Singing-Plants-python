class MovingAvg:

    def __init__(self, size):
        self._nAdd = 0
        self._index = 0
        self._accum = 0
        self._size = size
        self._buffer = [0] * size

    def _next(self, index):
        return index + 1 if index < self._size - 1 else 0

    def _prev(self, index):
        return index - 1 if index > 0 else self._size - 1   

    def add(self, value):
	if self._nAdd < self._size:
            self._nAdd += 1
        self._accum += value
        self._accum -= self._buffer[self._index]
        self._buffer[self._index] = value
        self._index = self._next(self._index)

    def reset(self):
        self._nAdd = 0
        self._accum = 0
        for i in range(4):
            self._buffer[i] = 0

    def get(self):
        return self._accum/self._nAdd if self._nAdd > 0 else self._accum

    def getBuffer(self):
	return self._buffer
        
