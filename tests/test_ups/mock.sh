#!/bin/bash

uutarball="$1" ; shift
PRODUCTS="$1" ; shift

usage () { 
    echo "mock.sh ups_upd-X.Y.Z-source.tar.bz2 [/path/to/directory]"
    exit 1
}

if [ -z "$uutarball" ] ; then
    usage
fi
uutarball=$(readlink -f $uutarball)
uu_version="$(echo $uutarball|sed -e 's|.*/ups-upd-||' -e 's|-source.tar.bz2||')"
uu_vusstr="v$(echo $uu_version | tr '.' '_')"
uu_xyzver="$(echo $uu_version | tr -d '.')"

my_products=no
if [ -z "$PRODUCTS" ] ; then
    PRODUCTS=$(mktemp -d)
    my_products=yes
fi


cmd () {
    echo "Running command in $(pwd):" 1>&2
    echo "$@" 1>&2
    $@
    err=$?
    if [ "$err" != "0" ] ; then
	env | sort
	echo "Command failed with \"$err\"" 1>&2
	echo $@
	exit $err
    fi
}

export PRODUCTS
cmd rm -rf $PRODUCTS
cmd mkdir -p $PRODUCTS

echo "Using PRODUCTS=$PRODUCTS"

dump () {
    filename=$1 ; shift
    echo 
    echo vvvvvv $filename vvvvvv
    cat $filename
    echo ^^^^^^ $filename ^^^^^^
    echo 
}

export UPS_SHELL=bash

cd $PRODUCTS
cmd tar -xjf $uutarball
tmp_flav="$(uname)-$(uname -r)"
tmp_build_dir="ups/$uu_vusstr/$tmp_flav"
cmd mkdir $tmp_build_dir
cmd tar -xzf ups/$uu_vusstr/source/ups${uu_xyzver}.tar.gz -C $tmp_build_dir
cd $tmp_build_dir
tmp_ups_dir=$PRODUCTS/$tmp_build_dir 
export UPS_DIR=$tmp_ups_dir
cmd make all
ups_flavor=$(./bin/ups flavor)
cd $PRODUCTS

new_ups_dir=$PRODUCTS/ups/$uu_vusstr/$ups_flavor
echo "Pivot UPS from:"
echo "   $tmp_ups_dir"
echo "to"
echo "   $new_ups_dir"
cmd mv $tmp_ups_dir $new_ups_dir
UPS_DIR=$new_ups_dir

echo "Declare UPS"
${UPS_DIR}/bin/ups declare ups ${uu_vusstr} -r ups/${uu_vusstr}/${ups_flavor} -4 -m ups.table -C -z ${PRODUCTS}
${UPS_DIR}/bin/ups declare ups ${uu_vusstr} -C -c

echo "Sourcing $PRODUCTS/setup"
source $PRODUCTS/setup

echo "Now mock install a package"

package=hello
version=2.8
vusstr=v$(echo $version | tr '.' '_')
qualifiers=debug

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
table_file=$PRODUCTS/$prod_root_dir/ups/${package}.table
cat <<EOF > $table_file
File = Table
Product = $package

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



