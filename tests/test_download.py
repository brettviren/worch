#!/usr/bin/env python

import os
import common
from orch.util import download

def test_python():
    url = "https://www.python.org/ftp/python/2.7.6/Python-2.7.6.tgz"
    md5sum = "md5:1d8728eb0dfcac72a0fd99c17ec7f386"
    #url = "https://legacy.python.org/ftp/python/2.7.6/Python-2.7.6.tgz"
    tgt = os.path.basename(url)
    download(url,tgt, md5sum)

def test_boost_many():
    urls = [
        'http://downloads.sourceforge.net/project/boost/boost/1.57.0/boost_1_57_0.tar.gz',
        'https://lbne.bnl.gov/packages/source/boost_1_57_0.tar.gz',
        ]
    md5sum = 'md5:25f9a8ac28beeb5ab84aa98510305299'
    tgt = os.path.basename(urls[0])
    got = download(urls, tgt, md5sum)
    print got

if '__main__' == __name__:
#    test_python()
    test_boost_many()
