#!/usr/bin/env python


import common
from orch import deconf2 as deconf
import re 

def myformat(string, **items):
    res = re.subn(r'{(\w+)}', lambda match: items.get(match.group(1), ''), string)
    return res[0]

def test_format():
    s = '{a}_{b}'
    d1 = dict(a='one', b='two')

    assert 'one_two' == myformat(s, **d1)

def test_simple_node_format():
    Node = deconf.NodeGroup()
    top = Node('start', version='0', label='{a}-{b}-{c}', a='aye',b='bee',c='sea')
    assert '{x}_{y}' == top.format('{x}_{y}')
    assert 'aye_{y}' == top.format('{a}_{y}')
    assert '{x}_bee' == top.format('{x}_{b}')
    assert 'aye_bee' == top.format('{a}_{b}')
    assert 'what_bee_sea' == top.format('{a}_{b}_{c}', a='what')


if '__main__' == __name__:
    test_format()
    test_simple_node_format()
