#!/usr/bin/env python

import common
from orch import util

def test_update_if():
    start = dict(a=1,b=2, something=None, override=None, keep='lovely')
    end = util.update_if(start, None, b=42, c=69, nothing=None, override='something', keep=None)
    assert len(end) == 7
    assert end['a'] == 1
    assert end['b'] == 42
    assert end['c'] == 69
    assert end['nothing'] is None
    assert end['override'] is 'something'
    assert end['keep'] is 'lovely'
    print (end)


if '__main__' == __name__:
    test_update_if()
    
