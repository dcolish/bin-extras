#!/bin/bash

if [ -n "$DEBUG" ] ; then 
    set -x
fi
set -e

unpackJar() {
    echo $1
    FILE=$(python -c "import sys,os.path; print (os.path.abspath(sys.argv[1]))" $1)
    NO_EXT=$(python -c "import sys,os.path; print (os.path.splitext(sys.argv[1])[0])" $1)
    DOC_DIR=target/javadoc/$(basename $NO_EXT)
    mkdir -p $DOC_DIR
    pushd $DOC_DIR
    jar xvf $FILE
    popd
}

export -f unpackJar

mvn dependency:copy-dependencies -Dclassifier=javadoc
find target/dependency -type f -name "*.jar" | xargs -I% bash -ic "unpackJar %"
