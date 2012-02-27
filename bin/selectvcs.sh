#!/bin/bash
# selectvcs.sh : should select the vcs command for a finite number of vcs's
function selectvcs() {
    case `stat -qn -f "%N" $1/.{git,hg,/}` in
        *.git) echo "git" ;;
        *.hg) echo "hg" ;;
        //./) exit -1 ;;
        *) $(selectvcs "`dirname ${1}`") ;;
    esac
}
$(selectvcs $PWD) $@