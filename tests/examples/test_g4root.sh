#!/bin/bash
srcdir=$(dirname $(dirname $(dirname $(readlink -f $BASH_SOURCE))))
echo $srcdir

if [ -n "$1" ] ; then
    workdir="$1" ; shift
    echo "Reusing workdir: $workdir"
else
    workdir=$(mktemp -d /tmp/worch-test-g4root.XXXX)
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
	--orch-config=$srcdir/examples/g4root/all.cfg \
        configure build 
fi

cd $workdir

source $workdir/install/env.sh

module avail 2>&1 | grep -q $workdir/install/modules
module avail 2>&1 | grep -q python/2.7.9

module load ipython

if [ -z "$(which ipython | grep $workdir/install)" ] ; then
    echo "Failed to find correct ipython:"
    which ipython
    exit 1
else
    echo "Found ipython at: $(which ipython)"
fi

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
