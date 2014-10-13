# -*- coding: utf-8 -*-
import threading


class SupermodelParseInfo(threading.local):

    def __getattr__(self, name):
        if name == 'stack':
            self.stack = [None]
            return self.stack
        if name == 'i18n_domain':
            return self.__dict__.get('i18n_domain')
        return self.__dict__[name]

parseinfo = SupermodelParseInfo()
