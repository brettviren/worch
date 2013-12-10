#!/bin/bash

mydir=$(dirname $(readlink -f $BASH_SOURCE))
worch_test_dir=$(dirname $mydir)
worch_dir=$(dirname $worch_test_dir)

get_waf_from_tarball () {
    waf_version="1.7.13"
    waf_unpacked="waf-$waf_version"
    waf_tarball="${waf_unpacked}.tar.bz2"
    waf_url="https://waf.googlecode.com/files/$waf_tarball"

    if [ ! -f $waf_tarball ] ; then
	wget -q $waf_url
    fi

    if [ -d $waf_unpacked ] ; then
	rm -rf $waf_unpacked
    fi
    tar -xjf $waf_tarball
    cd $waf_unpacked
}

get_waf_from_git () {
    local target=waf.git
    if [ ! -d waf ] ; then
	git clone https://code.google.com/p/waf/ $target
    fi
    if [ ! -d $target/.git ] ; then
	echo "Something is wrong" 1>&2
	exit 1
    fi
    cd $target
}

get_waf () {
    #get_waf_from_tarball
    get_waf_from_git
}


