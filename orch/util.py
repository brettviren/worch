#!/usr/bin/env python
'''
Utility functions
'''
try:    from urllib import request
except: from urllib import urlopen
else:   urlopen = request.urlopen


def update_if(d, p, **kwds):
    '''Return a copy of d updated with kwds.

    If no such item is in d, set item from kwds, else call p(k,v) with
    kwds item and only set if returns True.

    '''
    if p is None:
        p = lambda k,v: v is not None 
    d = dict(d)                 # copy
    for k,v in kwds.items():
        if not d.has_key(k):
            d[k] = v
            continue
        if p(k, v):
            d[k] = v

    return d

    
