#!/bin/bash
if [ "$(uname)" == "Darwin" ]; then
	/Applications/MacPorts/Emacs.app/Contents/MacOS/Emacs "$@"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
	emacs "$@" &
fi
