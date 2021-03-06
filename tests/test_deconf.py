#!/usr/bin/env python

import common
from orch import deconf
from orch.util import string2list
import os
import time

testcfgdir = os.path.join(common.worch_dir, 'tests/configs')
exampledir = os.path.join(common.worch_dir, 'examples')

cfgdirlist = [testcfgdir, exampledir]
os.environ['DECONF_INCLUDE_PATH'] = ':'.join(cfgdirlist)

def test_get_deconf_include_paths():
    got = deconf.get_deconf_include_paths()
    assert len(got) >= 2

def test_find_file():
    deconf.find_file('incs.cfg', cfgdirlist)

def test_parse_incs():
    cfg = deconf.parse('incs.cfg')
    deconf.add_includes(cfg)
    assert cfg.has_section('package foo'), 'no section [package foo]'
    assert cfg.has_section('group bar'), 'no section [group bar]'


def test_nodes_simple():
    Node = deconf.NodeGroup()
    top = Node('start', a = '1', b = '2', c = '3')

    g1 = Node('g1', 'group', top, a='10')
    assert g1._parent is top
    assert g1['a'] == '10'
    assert g1['b'] == '2'

    p11 = Node('p11', 'package', g1, b='11')
    assert p11._parent is g1
    assert p11['a'] == '10'
    assert p11['b'] == '11'

    p12 = Node('p12', 'package', g1, b='12')
    assert p12._parent is g1
    assert p12['a'] == '10'
    assert p12['b'] == '12'
    assert p12['p11_b'] == '11'

    g2 = Node('g2', 'group', top, a='20')
    assert g2['a'] == '20'
    assert g2['b'] == '2'
    assert g2['c'] == '3'

    p21 = Node('p21', 'package', g2, a='21')
    assert p21['a'] == '21'
    assert p21['b'] == '2'
    assert p21['c'] == '3'

    p22 = Node('p22', 'package', g2, c='22')
    assert p22['a'] == '20'
    assert p22['b'] == '2'
    assert p22['c'] == '22'
    assert p22['g2_c'] == '3'
    assert p22['start_a'] == '1'
    
    print 'TOP.keys', top.keys()
    assert len(top.keys()) == 3 + 3 + 3 * 6
    assert len(g1.keys()) == 3 + 3 + 3 * 6
    assert len(p22.keys()) == 3 + 3 + 3 * 6

    def blah(node, **kwds):
        print ('%(name)s: a=%(a)s b=%(b)s c=%(c)s len=%(size1)d/%(size2)d %(dump)s' % \
               dict(name=node._name, size1=len(kwds), size2=len(node._items),
                    dump=str(node._items), **kwds))

    for n in [top,g1,p11,p12,g2,p21,p22]:
        blah(n, **n.dict())

def test_nodes_interp():
    Node = deconf.NodeGroup()
    top = Node('start', a = "one", b = "two", c = "{a}_{b}_{d}")
    g1 = Node('g1', 'group', top, a="ten_{b}_{start_a}", d='g1', e='{a}_{start_undef}')

    g1._items.setdefault('xxx', 'some new value')
    assert g1['xxx'] == 'some new value'

    assert 'one' == g1.raw('start_a')
    assert 'one' == g1.format('{start_a}')
    assert 'one' == g1['start_a']
    assert top['c'] == "one_two_{d}", top['c']
    assert 'ten_two_one_two_g1' == g1['c'], g1['c']
    assert 'ten_two_one_{start_undef}' == g1['e'], g1['e']

    p11 = Node('p11', 'package', g1, d='p11')
    assert 'ten_two_one_two_p11' == p11['c'], p11['c']

    p12 = Node('p12', 'package', g1, c='{d}_{a}')
    assert 'g1_ten_two_one' == p12['c']

    assert len(g1.incomplete()) == 1, g1.incomplete() 
    assert len(p11.incomplete()) == 1, p11.incomplete() 

    g2 = Node('g2', 'group', top, a="ten_{b}_{start_a}", e='{a}_{c}')
    p21 = Node('p21', 'package', g2, c='sea', d='p21')
    assert len(g2.incomplete()) == 2, g2.incomplete()
    assert len(p21.incomplete()) == 0, p21.incomplete()

def test_chain():
    Node = deconf.NodeGroup()

    a = Node('a', 'A',    field1 = 'a')
    b = Node('b', 'B', a, field2 = 'b')
    c = Node('c', 'C', b, field3 = 'c', field4 = '{field1}_{field2}_{field3}')

    assert c['field1'] == 'a'
    assert c['field4'] == 'a_b_c'

def mytimeit(run, number=1):
    t1 = time.time()
    for x in range(number):
        run()
    t2 = time.time()
    return t2-t1


def make_name(what, number):
    return '%s%04d' % (what, number)

def create_packages(top, ngroups=10, npackages=10):
    Node = top.owner()
    groups = []
    packages = []
    pcount = 0
    group_names = []
    for ig in range(ngroups):
        group_name = make_name('group', ig)
        group_names.append(group_name)
        group = Node(group_name, type='group', parent=top, version='%d'%ig, group=group_name)
        groups.append(group)
        package_names = []
        for ip in range(npackages):
            pcount += 1
            package_name = make_name('package',pcount)
            package_names.append(package_name)
            package = Node(package_name, type='package', parent = group, 
                           version='%d.%d' %(ig,ip),
                           package = package_name,
                           groupversion = '{%s_version}'%group_name)
            packages.append(package)
        group.setdefault('packages', ', '.join(package_names))
    top.setdefault('groups',', '.join(group_names))
    return groups, packages

def test_stress():

    Node = deconf.NodeGroup()
    top = Node('start', version='0', label='{group}-{package}-{version}')


    ct = time.time()
    groups, packages = create_packages(top)
    ct = time.time() - ct
    print 'To create: %f' % ct

    def interrogate_packages():
        for p in packages:
            #print p._name
            assert p['groupversion']
            assert '{' not in p['label'], str(p)
    it1 = mytimeit(interrogate_packages, number=1)
    print 'To interrogate (*1): %f' % it1

    number = 100
    it2 = mytimeit(interrogate_packages, number=number)
    print 'To interrogate (*%d): %f (rel=%.3f)' % (number, it2, it2/it1/number)
    it3 = mytimeit(interrogate_packages, number=number)
    print 'To interrogate (*%d): %f (rel=%.3f)' % (number, it3, it3/it2)


def test_iterate():
    'Test iterating down the nodes'

    t1 = time.time()
    Node = deconf.NodeGroup(keytype = dict(groups='group', packages='package'))
    top = Node('start', version='0', label='{group}-{package}-{version}')
    groups, packages = create_packages(top, 10, 10)
    t2 = time.time()
    print 'Created in %.3f' % (t2-t1)
    
    got_groups = list()
    got_packages = list()
    for gname in string2list(top['groups']):
        #assert g in groups
        got_groups.append(gname)
        g = top.owner().node(gname)
        for p in string2list(g['packages']):
            #assert p in packages
            got_packages.append(p)
    t3 = time.time()
    print 'Iterated in %.3f' % (t3-t2)

    assert len(groups) == len(got_groups)
    assert len(packages) == len(got_packages)
    

config_file = os.environ.get('WORCH_CONFIG_FILE',
                             'g4root/all.cfg')
print ('Using worch config file:', config_file) 

fake_worch_data = dict( PREFIX = '/path/to/install',
                        out = '/path/to/tmp',
                        version_2digit = 'XXX.YYY',
                        version_dashed = 'XXX-YYY',
                        source_archive_file = 'the_source_file.tgz',
                        source_unpacked = 'the_source',
                        libbits = 'SixtyFourBits',
                        kernelname = 'Popcorn',
                        soext = 'soext',
                        root_config_arch = 'RootConfigArch',
                        tagsdashed = 'tag-dash-ed')

def test_load_config_file():
    'Test reading in some real config files'
    t1 = time.time()
    top = deconf.load(config_file, **fake_worch_data)
    t2 = time.time()
    print 'Created in %.3f' % (t2-t1)

    def dump_node(n):
        print n
        for k,v in n.local_items():
            print '%s = %s' % (k,v)
        print

    ngroups = 0
    npackages = 0
    for gname in string2list(top['groups']):
        g = top.owner().node(gname)
        for gk,gv in g.items():
            ngroups += 1

        for pname in string2list(g['packages']):
            p = top.owner().node(pname)
            for pk,pv in p.items():
                npackages += 1

    t3 = time.time()
    print 'Iterated in %.3f (#g=%d, #p=%d)' % (t3-t2, ngroups, npackages)

    ngroups = 0
    npackages = 0
    for gname in string2list(top['groups']):
        g = top.owner().node(gname)
        for gk,gv in g.items():
            ngroups += 1

        for pname in string2list(g['packages']):
            p = top.owner().node(pname)
            for pk,pv in p.items():
                npackages += 1

    t4 = time.time()
    print 'Iterated again in %.3f (#g=%d, #p=%d)' % (t4-t3, ngroups, npackages)


def test_other():
    '''
    Test that one package can reference another's variable
    '''
    cfg = deconf.load('other.cfg')
    top = cfg.owner()
    print top.keys()
    for g in [1, 2]:
        grp = 'g%d' % (g,)
        assert top.node(grp), 'no section [group %s] have: %s' % (grp, ', '.join(top.keys()))
        for p in [1, 2]:
            pkg = 'g%dp%d' % (g,p)
            assert top.node(pkg), 'no section [package %s]' % pkg
    g2p1 = top.node('g2p1')
    g2p2 = top.node('g2p2')
    assert g2p1['g1p1_version'] == '11', 'Can not get version for g1p1'
    assert g2p1['other_version1'] == '11', 'Can not get other_version1 from g2p1'
    assert g2p1['other_version2'] == '22', 'Can not get other_version2 from g2p1'
    print g2p1['g1p1_version'], g2p2['g1p2_version'], 
    print g2p1['other_version1'], g2p1['other_version2']


if '__main__' == __name__:
    test_other()
    test_get_deconf_include_paths()
    test_find_file()
    test_parse_incs()
    test_nodes_simple()
    test_nodes_interp()
    test_chain()
    test_iterate()
    test_stress()
    test_load_config_file()

