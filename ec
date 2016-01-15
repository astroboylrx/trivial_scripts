#!/bin/bash
if [ "$(uname)" == "Darwin" ]; then
	# Since using [-a ''] as an argument of emacsclient in Mac OS X fails to start emacs server itself, so I need to start the server by shell
	## 1, check if there is any Emacs server temp file in /var/folders/..., Notice that we use Emacs instead of emacs in Mac OS
	socket_file=$(lsof -c Emacs | grep server | tr -s " " | cut -d' ' -f8)
	if [[ $socket_file == "" ]]; then
		/Applications/MacPorts/Emacs.app/Contents/MacOS/Emacs --daemon > /dev/null 2>&1
	fi
	## 2, now open emacsclient, or just open a new instance if server is still not running.
	/Applications/MacPorts/Emacs.app/Contents/MacOS/bin/emacsclient -a '/Applications/MacPorts/Emacs.app/Contents/MacOS/Emacs' -c -n $* &
	## 3, now try to activate the window of Emacs, use osascript to call AppleScript
	if [[ $socket_file != "" ]]; then
		osascript -e  "try
                           tell application \"Emacs\" to activate
                       end try"
	fi 

elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
	emacsclient -a '' -c -n "$@" &
fi
