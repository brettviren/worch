#!/bin/bash
# Test ups declare
# Only requirement is that UPS_DIR is set to where the "ups" binary is installed.

if [ -z "$UPS_DIR" ] ; then
    echo "Must set UPS_DIR so \$UPS_DIR/bin/ups points to 'ups' binary"
    exit 1
fi
export UPS_SHELL=bash

cmd () {
    echo "Running command:" 1>&2
    echo "$@" 1>&2
    $@
    err=$?
    if [ "$err" != "0" ] ; then
	echo "Command failed with \"$err\"" 1>&2
	exit $err
    fi
}

dump () {
    filename=$1 ; shift
    echo 
    echo vvvvvv $filename vvvvvv
    cat $filename
    echo ^^^^^^ $filename ^^^^^^
    echo 
}

PATH=$UPS_DIR/bin:$PATH
export PRODUCTS=$(mktemp -d)
echo "Using PRODUCTS=$PRODUCTS"

package=hello
version=2.8
vusstr=v$(echo $version | tr '.' '_')
qualifiers=debug
flavor=$(ups flavor)
#prod_root_dir="$package/$version"
prod_root_dir="$package/$vusstr"
prod_inst_dir="$prod_root_dir/$qualifiers"

# fake an installation
mkdir -p $PRODUCTS/$prod_inst_dir/bin
cat <<EOF > $PRODUCTS/$prod_inst_dir/bin/hello
#!/bin/sh
echo "Hello World"
EOF
chmod +x $PRODUCTS/$prod_inst_dir/bin/hello

# fake a table file generation
mkdir -p $PRODUCTS/$prod_root_dir/ups
table_file=$PRODUCTS/$prod_root_dir/ups/hello.table
cat <<EOF > $table_file
File = Table
Product = hello

Group:
  Flavor = ANY
  Qualifiers = ""

Common:
  Action = SETUP
    setupEnv()
    prodDir()
    pathPrepend(PATH, \${UPS_PROD_DIR}/$qualifiers/bin)
End:
EOF
echo "Table file: \"$table_file\""
dump $table_file

echo "UPS declaring:" 
cmd ups declare $package $vusstr -4 -r $prod_root_dir -m ${package}.table -C
cmd ups declare $package $vusstr -C -c

echo "Results of declare:"
ls -l $PRODUCTS/$package

version_ford=$PRODUCTS/$package/${vusstr}.version
echo "Version file or directory: \"$version_ford\""
if [ -d "$version_ford" ] ; then
    ls -l "$version_ford"
else
    dump $version_ford
fi

chain_ford=$PRODUCTS/$package/current.chain
echo "Chain file or directory: $chain_ford"
if [ -d $chain_ford ] ; then
    ls -l $chain_ford
else
    dump $chain_ford
fi


echo "Testing use:"
cmd ups list -aK+
sufile=$(cmd ups setup $package)
dump $sufile
source $sufile
which hello
hello

#echo "Removing working directory: $PRODUCTS"
#rm -rf $PRODUCTS

