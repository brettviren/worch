#!/bin/bash

# Make a wscript'less waf bundle with orchlib and worch orch and extras modules and orch configuration

mydir=$(dirname $(readlink -f $BASH_SOURCE))
source $mydir/bundle-common.sh

bundle=$mydir/worch-configured-bundle
rm -f $bundle
rm -rf .waf*

get_waf
rm -f waf

# prep waf source area for our abuse
cp wscript wscript.factory
diff -u wscript $mydir/wscript.bundle-code | patch -p0
cp -a $worch_dir/orch .
cp -a $worch_dir/extras .
cp -a $worch_dir/examples/simple-with-modules/main.cfg orch.cfg

python ./waf-light configure build \
  --tools=$worch_dir/orchlib.py \
  --prelude=$'\tfrom waflib.extras import orchlib\n\torchlib.start(cwd, VERSION, wafdir)\n\tsys.exit(0)'
mv waf $bundle

# clean up
rm -rf orch extras wscript
mv wscript.factory wscript

cd $mydir

# test
rm -rf install-configured tmp-configured .waf* .lock-waf*
$bundle --prefix=instal-configured --out=tmp-configured \
    configure build

