#!/bin/bash

# Make a waf bundle with orchlib so a wscript file isn't needed.

mydir=$(dirname $(readlink -f $BASH_SOURCE))
source $mydir/bundle-common.sh

bundle=$mydir/worch-noscript-bundle
rm -f $bundle
rm -rf .waf*

get_waf
rm -f waf
python ./waf-light configure build \
  --tools=$worch_dir/orchlib.py \
  --prelude=$'\tfrom waflib.extras import orchlib\n\torchlib.start(cwd, VERSION, wafdir)\n\tsys.exit(0)'
mv waf $bundle
cd $mydir

# test
rm -rf install-noscript tmp-noscript
export PYTHONPATH=$worch_dir
$bundle --version
ls -l .waf*
$bundle --prefix=instal-noscript --out=tmp-noscript \
    --orch-config=$worch_dir/examples/simple-with-modules/main.cfg \
    configure build

