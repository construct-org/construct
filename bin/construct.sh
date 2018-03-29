#!/bin/bash

construct () {

    py_entry_point="pyconstruct"
    _tmpdir=$(mktemp -d)
    export SCRIM_AUTO_WRITE="${SCRIM_AUTO_WRITE:=1}"
    export SCRIM_PATH="${SCRIM_PATH:=$_tmpdir/scrim_out.sh}"
    export SCRIM_SCRIPT="${0}"
    export SCRIM_SHELL="${SCRIM_SHELL:=bash}"
    export SCRIM_DEBUG="${SCRIM_DEBUG:=0}"
    debug="test $SCRIM_DEBUG == 1"

    $debug && echo "Variables:"
    $debug && echo "  SCRIM_AUTO_WRITE: $SCRIM_AUTO_WRITE"
    $debug && echo "        SCRIM_PATH: $SCRIM_PATH"
    $debug && echo "      SCRIM_SCRIPT: $SCRIM_SCRIPT"
    $debug && echo "       SCRIM_SHELL: $SCRIM_SHELL"
    $debug && echo "       SCRIM_DEBUG: $SCRIM_DEBUG"
    $debug && echo "executing $py_entry_point"

    $py_entry_point "$@"

    if [ -e "$SCRIM_PATH" ]; then

        source "$SCRIM_PATH"

        if [ $? -ne 0 ]; then
            echo "[scrim] error executing:"
            echo ""
            cat $SCRIM_PATH
            echo
        fi

        $debug && echo "Removing $SCRIM_PATH"
    fi

    $debug && echo "Unset environment variables."
    unset py_entry_point
    unset SCRIM_AUTO_WRITE
    unset SCRIM_PATH
    unset SCRIM_SCRIPT
    unset SCRIM_SHELL
    unset SCRIM_DEBUG
    unset debug
    rm -rf $_tmpdir

}
