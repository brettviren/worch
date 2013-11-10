#!/bin/bash


run () {
    echo "Running $@"
    $@
    if [ "$?" != "0" ] ; then
	echo "Failed to run: $@"
	exit 1
    fi
}

run_tests () {
    python=$1 ; shift
    
    rm -rf .waf-* install tmp
    echo "Testing with $python"
    run $python waf --version



    for config in tests/configs/deps.cfg 'examples/simple-with-patch/*.cfg'

    do
	run $python waf --prefix=install --out=tmp --orch-config=$config configure build
    done
}	


for pythonX in python2.6 python2.7 python3.1
do
    if [ -z "$(which $pythonX)" ] ; then
	echo "No $pythonX"
	continue
    fi

    run_tests $pythonX
done
