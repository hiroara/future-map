from concurrent.futures import wait, FIRST_COMPLETED, ALL_COMPLETED


class FutureMap:
    def __init__(self, fn, iterable, buffersize):
        self.__fn = fn
        self.__iterable = iterable
        self.__buffersize = buffersize
        self.__futures = set()

    def __iter__(self):
        for value in self.__iterable:
            while not self.__reserve(value):
                for result in self.__consume(return_when=FIRST_COMPLETED):
                    yield result
            for result in self.__consume(timeout=0):
                yield result
        for result in self.__consume(return_when=ALL_COMPLETED):
            yield result

    @property
    def size(self):
        return len(self.__futures)

    @property
    def full(self):
        return len(self.__futures) >= self.__buffersize

    def __reserve(self, value):
        if self.full:
            return False
        self.__futures.add(self.__fn(value))
        return True

    def __consume(self, timeout=None, return_when=ALL_COMPLETED):
        done, not_done = wait(self.__futures, timeout=timeout, return_when=return_when)
        for future in done:
            yield future.result()
        self.__futures = not_done


def future_map(fn, iterable, buffersize):
    return FutureMap(fn, iterable, buffersize)
