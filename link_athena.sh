#!/usr/bin/env bash
if [ $# -ne 1 ]
then
	echo "We need one path as argument."
	exit
fi

current=`pwd`
rm *.c *.h Makefile.in
link_dir.sh $1
for ex in `ls -d */`; do cd $ex; rm *; link_dir.sh $1/${ex%%/}; cd ..; done
rm defs.h config.h; mv $1/defs.h $1/config.h .; cd $1; ln -s $current/defs.h; ln -s $current/config.h

