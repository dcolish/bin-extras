#!/bin/bash

set -e

LOCATION=`dirname $(realpath $0)`
BIN_FILES=`ls bin`
CMD=${1:-""}

function help {
    echo "Usage: deploy.sh: (install)|(uninstall)|(add <cmd>)"
}

function install {
    if [ ! -d $HOME/bin ]
    then
        mkdir $HOME/bin
    fi

    for x in $BIN_FILES
    do
        ln -sf  $LOCATION//bin/${x} $HOME/bin/${x}
    done
}

if [ "$CMD" = 'install' ]
then
    install
elif [ "$CMD" = 'uninstall' ]
then
    for x in $BIN_FILES
    do
        rm -rf $HOME/bin/${x}
    done
else
    echo "Not a proper command"
    help
fi
