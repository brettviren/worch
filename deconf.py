#!/usr/bin/env python
'''A descending configuration parser.

This parser provides for composing a nested data structure from a
Python (ConfigParser) configuration file.  It also allows for a more
flexible string interpolation than the base parser.

The file is parsed by the usual ConfigParser module and the resulting
data is interpreted.  Two special sections are checked.

 - [keytype] :: a mapping of a key name to a "section type"

 - [<name>] :: the starting point of interpretation, default name is "global"

The [keytype] section maps a key name to a section type.  When a
matching key is found in another section it is interpreted as a
colon-separated list of section names and its value in the keytype
dictionary as a section type.  A section expresses its type and name
by starting with a line that matches "[<type> <name>]".  When a
matching key is encountered the keytype mapping and the list of names
are used to set a list on that key in the returned data structure
which contains the result of interpreting the referred to sections.

This loading continues until all potential sections have been loaded.
Not all sections in the file may be represented in the resulting data
structure if they have not been referenced through the keytype
mechanism described ablve.

Any value not used for keytype resolution (simple scalar) is treated
as a string and may contain the names of other simple, scalar
variables surrounded by "{}".  Their values will be replaced in a way
that honors the hierarchy of the data structure.
'''

def parse(filename):
    'Parse the filename, return an uninterpreted object'
    from ConfigParser import SafeConfigParser
    cfg = SafeConfigParser()
    cfg.read(filename)
    return cfg

def to_list(lst):
    return [x.strip() for x in lst.split(',')]

def get_first_typed_section(cfg, typ, name):
    target = '%s %s' % (typ, name)
    for sec in cfg.sections():
        if sec.startswith(target):
            return sec
    raise ValueError, 'No section: <%s> %s' % (typ,name)


def resolve(cfg, sec):
    'Recursively load the configuration starting at the given section'
    keytype = dict(cfg.items('keytype'))
    ret = {}
    for k,v in cfg.items(sec):
        typ = keytype.get(k)
        if not typ:
            ret[k] = v
            continue
        lst = []
        for name in to_list(v):
            other_sec = get_first_typed_section(cfg, typ, name)
            other = resolve(cfg, other_sec)
            lst.append(other)
        ret[k] = lst
    return ret

def interpret(cfg, start = 'global'):
    'Interpret a parsed file, return raw data structure'
    return resolve(cfg, start)

def format_flat_dict(dat, **kwds):
    print "FLAT: %s" % str(dat)
    print "KWDS: %s" % ', '.join(kwds.keys())

    kwds = dict(kwds)
    unformatted = dict(dat)
    formatted = dict()

    while unformatted:
        changed = False
        for k,v in unformatted.items():
            try:
                new_v = v.format(**kwds)
            except KeyError:
                continue        # maybe next time
            changed = True
            formatted[k] = new_v
            kwds[k] = new_v
            unformatted.pop(k)
            continue
        if not changed:
            break
        continue
    if unformatted:
        formatted.update(unformatted)
    return formatted

def format_any(dat, **kwds):
    if isinstance(dat, basestring):
        try:
            return dat.format(**kwds)
        except KeyError:
            return dat
    if isinstance(dat, list):
        return [format_any(x, **kwds) for x in dat]
    flat = dict()
    other = dict()
    for k,v in dat.items():
        if isinstance(v, basestring):
            flat[k] = v
        else:
            other[k] = v
    ret = format_flat_dict(flat, **kwds)
    for k,v in other.items():
        v = format_any(v, **kwds)
        ret[k] = v
    return ret


def inflate(src, defaults = None):
    if not defaults: defaults = dict()
    ret = dict()
    ret.update(defaults)
    ret.update(src)

    flat = dict()
    other = dict()
    for k,v in ret.items():
        if isinstance(v, basestring):
            flat[k] = v
        else:
            other[k] = v
    for key,lst in other.items():
        ret[key] = [inflate(x, flat) for x in lst]

    return ret



if '__main__' == __name__:
    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=2)
    data = interpret(parse('deconf.cfg'))
    data2 = inflate(data)
    data3 = format_any(data2)

    print 'INTERPRETED:'
    pp.pprint(data)
    print 'INFLATED:'
    pp.pprint(data2)
    print 'FORMATTED:'
    pp.pprint(data3)
