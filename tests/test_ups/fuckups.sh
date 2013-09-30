#!/bin/bash
export UPS_SHELL=bash

products=`pwd`/install-ups
ups_dir=/data3/bv/w/worch/install-ups/ups/5.0.0/debug
tag=debug

ups_cmd () {
    $ups_dir/bin/ups "$@"
}

ups_prime() {
    upsfilesdir="$products/.upsfiles"
    if [ -d "$upsfilesdir" ] ; then
	return
    fi
    mkdir -p $upsfilesdir
    cat <<EOF > $upsfilesdir/dbconfig
FILE = DBCONFIG
AUTHORIZED_NODES = *
VERSION_SUBDIR = 1
PROD_DIR_PREFIX = \${UPS_THIS_DB}
#UPD_USERCODE_DIR = \${UPS_THIS_DB}/.updfiles
EOF
}

ups_declare () {
    local name="$1" ; shift
    local version="$1" ; shift
    local vstr="v$(echo $version | tr '.' '_')"

    rm -rf $products/$name/current.chain
    rm -rf $products/$name/${vstr}.version

    local prod_root_dir="$name/$version/$tag"
    local table_file="${name}.table"
    local prod_ups_dir=$products/$prod_root_dir/ups

    if [ "$name" != "ups" ] ; then
	echo "Removing $prod_ups_dir"
	rm -rf $prod_ups_dir
    fi
    if [ ! -d $prod_ups_dir ] ; then
	mkdir -p $prod_ups_dir
    fi

    local table_path="$prod_ups_dir/$table_file"
    if [ -f "$table_path" ] ; then
	echo "table file exists: $table_path"
    else
	cat <<EOF >$prod_ups_dir/$table_file
File = Table
Product = $name
Group:
  Flavor = ANY
  Qualifiers = ""

Common:
    Action = SETUP
        setupEnv()
        proddir()
        pathPrepend(PATH, \${UPS_PROD_DIR}/bin)
End:
EOF
    fi

    ups_cmd declare $name $vstr \
	-f ANY \
	-z $products \
	-r $prod_root_dir \
	-U ups \
	-m $table_file \
	-c

}

test_use () {
    export PRODUCTS=$products
    export UPS_DIR=$ups_dir
    PATH=$UPS_DIR/bin:$PATH
    echo 
    echo testing
    echo
    #ups help    
    echo "LISTING:"
    ups list -aK+
    echo "FLAVOR:"
    ups flavor

    echo "HELLO"
    f=$(ups setup hello)
    cat $f
    echo "from: $f"

    echo "UPS"
    f=$(ups setup ups)
    cat $f
    echo "from: $f"

    echo "Sourcing ups setup"
    source $f

    echo "Setting up 'hello'"
    setup hello
    which hello
    hello
    env|grep -i hello
}


ups_prime
ups_declare ups 5.0.0
ups_declare hello 2.8


test_use
