#!/bin/bash

set -e

if [ -z "$*" ] ; then
    echo "You need to give me a tag annotation"
    exit 1
fi

gittag=$(git describe)
pyver=$(python setup.py --version)

if [ -n "$(git status -s)" ] ; then
    echo "You dirty git."
    exit 1
fi

if [ "$gittag" = "$pyver" ] ; then
    echo "You need to change the version in setup.py"
    exit 1
fi

git tag -a $pyver -m "$*"
