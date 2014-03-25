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

if '__main__' == __name__:
    test_python()
