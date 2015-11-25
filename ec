#!/bin/bash
if [ "$(uname)" == "Darwin" ]; then
	/Applications/MacPorts/Emacs.app/Contents/MacOS/bin/emacsclient -c -n $* &
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
	emacsclient -c -n "$@" &
fi
