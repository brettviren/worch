#!/bin/bash

# test the simple-with-modules example
# this assumes this script is in-source

set -e

srcdir=$(dirname $(dirname $(dirname $(readlink -f $BASH_SOURCE))))
echo $srcdir
workdir=$(mktemp -d /tmp/worch-test-simple-with-module.XXXX)
echo $workdir

pushd $srcdir
./waf --prefix=$workdir/install \
      --out=$workdir/tmp \
      --orch-config=$srcdir/examples/simple-with-modules/main.cfg \
        configure build


source $workdir/install/env.sh
module avail
module avail 2>&1 | grep $workdir/install/modules
module avail 2>&1 | grep bc/1.06
module avail 2>&1 | grep hello/2.8
module load hello
which hello | grep $workdir
which bc | grep $workdir





