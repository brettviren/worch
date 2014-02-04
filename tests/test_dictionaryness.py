#!/usr/bin/env python

import UserDict

class MyDict(UserDict.DictMixin):
    def __init__(self, **items):
        self._mydict = items
    def __getitem__(self, key):
        return self._mydict[key]
    def keys(self):
        return self._mydict.keys()

def blah(d, **items):
    assert d == items
    print items

def test_something():
    md = MyDict(a=1,b=2,c=3)
    md['a']
    blah(md, **md)              # doesn't work in python 2.4.6


if '__main__' == __name__:
    test_something()


