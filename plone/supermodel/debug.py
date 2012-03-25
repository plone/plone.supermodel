import threading


class SupermodelParseInfo(threading.local):

    def __getattr__(self, name):
        if name == 'stack':
            self.stack = [None]
            return self.stack
        return self.__dict__.get(name)

parseinfo = SupermodelParseInfo()
