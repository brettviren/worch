#!/usr/bin/env python
'''

'''

import os
import sys
sys.path.insert(0, '/'.join(os.path.realpath(__file__).split('/')[:-2] + ['orch']))
import util


if '__main__' == __name__:
    text='''\
EDITOR=emacs -nw
LANG=C
oneliner=() { echo "I got my one eye on you" }
module=() {  eval `/usr/bin/modulecmd bash $*`
}
'''
    parsed = util.envvars(text)
    assert len(parsed) == 4, 'Lost something'
    for k,v in parsed.items():
        print ('name="%s" value=[%s]' % (k,v))
        if k == 'module':
            assert v, 'where is my function?'
            assert len(v.split('\n')) == 2, 'lost multilinedness'
