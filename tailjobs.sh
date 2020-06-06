#!/usr/bin/env zsh

coln(){ awk '{print '`echo $1|sed 's/c\([0-9]\+\)/\$\1/g'`'}' $2 ; }

default_prefix="output"
prefix=${1:-$default_prefix}

# get all job id
for ex in `qstat -f -u rixin | coln c1 | tail -n+6`; do
    jobid=${ex%%.*}
    echo "JOB ID: $jobid"

    # get working directory
    # first, grep from the job info (N.B. PBS_O_WORKDIR may cross lines, -A1 gives one more line)
    # second, remove all spaces, tabs, newlines
    # then remove the leading "PBS_O_WORKDIR=" and anything after first comma
    tmp_dir=$(qstat -f $jobid | grep -A1 PBS_O_WORKDIR) # | tr -d '\040\011\012\015'
    tmp_dir=${tmp_dir//[[:space:]]/} # the piping above is an alternative
    tmp_dir=${${tmp_dir#*=}%%,*}
    #tmp_dir=${tmp_dir:0:-1} # remove the last char if needed
    echo "WORK DIR: $tmp_dir"

    # see if any output files exist, escape '*' for zsh
    
    if $(ls $tmp_dir/$prefix* &> /dev/null); then
        latest_out=$(ls -t $tmp_dir/$prefix* | head -n 1)
        echo "tail of $latest_out"
        tail $latest_out
    else
        echo "Desired files not found here."
    fi
done