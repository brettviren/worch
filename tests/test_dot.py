#!/usr/bin/env python
import os
import sys
orch_dir = '/'.join(os.path.realpath(__file__).split('/')[:-2] + ['orch'])
#print ('Using orch modules from: %s' % orch_dir)
sys.path.insert(0, orch_dir)

import dot

def test_graph():
    g = dot.Graph('TestGraph')
    g.add_node('m1', shape='box')
    g.add_node('m2', shape='ellipse')
    g.add_edge('m1', 'm2')
    print g

def test_sub_graph():
    g = dot.Graph('TestGraph', color='blue', label='maingraph')
    g.add_subgraph('TestSubGraph1', style='filled', color='lightgrey', label='main')
    g.add_subgraph('TestSubGraph2', style='filled', color='grey', label='alt')
    g.add_node('m1', 'TestSubGraph1', shape='box')
    g.add_node('m2', 'TestSubGraph1', shape='ellipse')
    g.add_edge('m1', 'm2')
    g.add_node('s1', 'TestSubGraph2', shape='box')
    g.add_node('s2', 'TestSubGraph2', shape='ellipse')
    g.add_edge('s1', 's2')
    g.add_edge('m1','s2')
    g.add_node('start', shape='Mdiamond')
    g.add_node('end', shape='Msquare')
    g.add_edge('start','m1')
    g.add_edge('start','s1')
    g.add_edge('m2','end')
    g.add_edge('s2','end')
    print g

if '__main__' == __name__:
    #test_graph()
    test_sub_graph()

