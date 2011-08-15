GIT="`which git`"
HG="`which hg`"

function checkvcs() {
    base=$1
    if [[ -e "${base}/.git" ]]; then
        VCS=$GIT
    elif [[ -e "${base}/.hg" ]]; then
        VCS=$HG 
    else
        if [[ "${base}" = "/" ]]; then
            exit -1
        fi
        checkvcs "`dirname ${base}`"
    fi
}

checkvcs "`pwd`"
$VCS $@