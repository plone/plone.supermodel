import linecache
import threading

parse_info = threading.local()


class SupermodelImportException(Exception):
    
    def __init__(self, msg, element):
        self.msg = msg
        self.fname = getattr(parse_info, 'fname', None)
        self.lineno = getattr(element, 'sourceline', None)

    def __str__(self):
        if self.fname is not None and self.lineno is not None:
            line = linecache.getline(self.fname, self.lineno).strip()
        fname = self.fname or '<unknown>'
        lineno = self.lineno or 'unknown'
        return '\n  File "%s", line %s\n      %s\n%s' % (
            fname, lineno, line, self.msg)
