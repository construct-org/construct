#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    export SCRIM_ADMIN=0
else
    export SCRIM_ADMIN=1
fi

_tmpdir=$(mktemp -d)
export SCRIM_PATH="$_tmpdir/scrim_out.sh"

python -m install "$@"

if [ -e "$SCRIM_PATH" ]; then

    source "$SCRIM_PATH"

    if [ $? -ne 0 ]; then
        echo "Error:"
        echo ""
        cat $SCRIM_PATH
        echo
    fi

fi

unset SCRIM_ADMIN
unset SCRIM_PATH
rm -rf $_tmpdir
