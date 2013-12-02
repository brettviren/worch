#!/bin/bash


run () {
    echo "Running $@"
    $@
    if [ "$?" != "0" ] ; then
	echo "Failed to run: $@"
	exit 1
    fi
}

run_unit_tests () {
    local python=$1 ; shift
    local ut
    for ut in tests/test_*.py
    do
	log="$ut-${python}.log"
	#echo "running: $python $ut --> $log"
	$python $ut > $log 2>&1
	local err=$?
	if [ "$err" = "0" ] ; then
	    #echo "...passed"
	    continue
	fi
	echo "FAILED: $python $ut > $log 2>&1"
    done
}

run_test_builds () {
    local python=$1 ; shift
    
    rm -rf .waf-* install tmp
    echo "Testing with $python"
    run $python waf --version

    for config in \
	examples/python/main.cfg \
	examples/simple-with-modules/main.cfg \
	tests/configs/deps.cfg 'examples/simple-with-patch/*.cfg'
    do
	run $python waf --prefix=install --out=tmp --orch-config=$config configure build
    done
}	

loop_on_pythons () {
    for pythonX in python2.6 python2.7 python3.0 python3.1 python3.2
    do
	if [ -z "$(which $pythonX)" ] ; then
	    echo "No $pythonX"
	    continue
	fi
	$@ $pythonX
    done
}

#loop_on_pythons run_test_builds
loop_on_pythons run_unit_tests
