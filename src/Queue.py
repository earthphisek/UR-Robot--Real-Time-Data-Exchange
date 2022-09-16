class Queue:
    def __init__(self, lst:list) -> None:
        self.__queue = lst.copy()

    def enqueue(self, x):
        self.__queue.append(x)
        return self

    def dequeue(self):
        x = self.__queue[0]
        if len(self.__queue) == 1:
            self.__queue = []
        else:
            self.__queue = self.__queue[1:]
        return x

    def head(self):
        return self.__queue[0]

    def tail(self):
        return self.__queue[-1]

    def get(self):
        return self.__queue.copy()

    def set(self, lst:list):
        self.__queue = lst.copy()

    def is_empty(self):
        return True if len(self.__queue) == 0 else False

