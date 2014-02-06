#!/usr/bin/env python


import common
from orch import confnode
from orch.util import format, format_get

def test_format():
    kwds = dict(a='one', b='two')
    
    trials = [
        ('{a}_{b}', 'one_two'),
    ]
    
    for give, want in trials:
        got = format(give, **kwds)
        assert want == got, 'Want: "%s", got: "%s"' % (want, got)
        got = format_get(give, kwds.get)
        assert want == got, 'Want: "%s", got: "%s"' % (want, got)


def test_simple_node_format():
    Node = confnode.NodeGroup()
    top = Node('start', version='0', label='{a}-{b}-{c}', a='aye',b='bee',c='sea')

    trials = [
        ('{x}_{y}', '{x}_{y}', {}),
        ('{a}_{y}', 'aye_{y}', {}),
        ('{x}_{b}', '{x}_bee', {}),
        ('{a}_{b}', 'aye_bee', {}),
        ('{a}_{b}_{c}', 'what_bee_sea', dict(a='what')),
        ('{a}_{undef}', 'aye_{undef}', {}),
        ]
    for give, want, extra in trials:
        got = top.format(give, **extra)
        assert want == got, 'Want: "%s", got: "%s"' % (want, got)


if '__main__' == __name__:
    test_format()
    test_simple_node_format()
