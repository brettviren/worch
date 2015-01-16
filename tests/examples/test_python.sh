#!/bin/bash

srcdir=$(dirname $(dirname $(dirname $(readlink -f $BASH_SOURCE))))
echo $srcdir

if [ -n "$1" ] ; then
    workdir="$1" ; shift
    echo "Reusing workdir: $workdir"
else
    workdir=$(mktemp -d /tmp/worch-test-python.XXXX)
fi

cd $workdir
if [ ! -d venv ] ; then
    virtualenv venv
fi
source venv/bin/activate


if [ -n "$1" -a "$1" = "nobuild" ] ; then
    shift
    echo "Not building"
else
    cd $srcdir
    pip uninstall -r worch
    python setup.py sdist
    pip install $(ls -t dist/worch-*.tar.gz | head -1)

    which waf
    waf --version

    cd $workdir

    cp $workdir/venv/share/worch/wscripts/worch/wscript .
    waf \
	--prefix=$workdir/install \
	--out=$workdir/tmp \
	--orch-config=$srcdir/examples/python/main.cfg \
        configure build 
fi

cd $workdir

set -e

PATH=$workdir/install/bin:$PATH
if [ -z "$(which python | grep $workdir)" ] ; then
    echo "Failed to find right Python, found:"
    which python
    exit 1
else
    which python
fi

ppath=$(python -c "import sys; print \"\n\".join(sys.path)")
if [ -z "$(echo $ppath | grep $workdir/install/lib/python2.7)" ] ; then
    echo "Failed to find installed Python library in sys.path, found:"
    echo "$ppath"
    exit 1
else
    echo "Found installed Python in sys.path"
fi

export LD_LIBRARY_PATH=$workdir/install/lib

pver_want="2.7.9"		# check examples/python/main.cfg file
pver="$(python --version 2>&1)"
if [ -z "$(echo $pver | grep $pver_want)" ] ; then
    echo "Failed to get correct Python version."
    echo "Want: $pver_want"
    echo "Got: $pver"
    exit 1
else
    echo "Got expected Python version: $pver"
fi

export PYTHONHOME=$workdir/install
export PYTHONNOUSERSITE=yes
ppath=$(python -c "import sys; print \"\n\".join(sys.path)")
if [ -n "$(echo $ppath | grep /usr/lib/python2.7/dist-packages)" ] ; then
    echo "PYTHONUSERSITE fails to get rid of system dist-packages"
    echo "$ppath"
    exit 1
else
    echo "PYTHONUSERSITE removes system dist-packages"
fi



ipver=$(ipython --version)
ipver_want=2.3.1
if [ -z "$(echo $ipver | grep $ipver_want)" ] ; then
    echo "Got wrong ipython version"
    echo "Want: $ipver_want"
    echo "Got: $ipver"
    exit 1
else
    echo "Got expected ipython version: $ipver"
fi

