#!/bin/bash

make_dir () {
    dir=$1 ; shift
    if [ -d $dir ] ; then
	rm -rf $dir
    fi
    mkdir $dir
}
for dir in tmp test ; do make_dir $dir ; done

if [ ! -f ../../waf ] ; then
    echo 'Expect to find waf at ../../waf'
    exit 1
fi

cp -a worch.py ../../wscript ../../orch ../../waf	tmp/
cp -a ../../examples/simple-with-patch/		tmp/cfg

pushd tmp/

# fix up hard-coded paths to examples area
sed -ie 's|examples/simple-with-patch|cfg|' cfg/gnuprograms.cfg

zip -q -r cfg.zip cfg
zip -q -r orch.zip orch
zip -q -r worch.zip worch.py wscript waf orch.zip cfg.zip
cat ../zip_header.sh worch.zip > worch
chmod +x worch
popd

cp tmp/worch test/worch

echo 'Made bundle in tmp/ now testing in test/'
pushd test/
set -x 
./worch --prefix=install --out=temp --orch-config=cfg/*.cfg configure
./worch build
set +x
popd 
