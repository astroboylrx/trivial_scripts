#!/usr/bin/env bash

if [ $# -lt 1 ]
then
    echo "We need one arugment."
    exit
fi

echo "Current time" `date +"%T"`
echo "Checking file numbers"
tmp_num=$(comb_check.py ./ get_num_vtk); 
if [ "$tmp_num" = "-1" ]; then
    min_vtk_num="0"; max_vtk_num="0"; num_vtk_files=0
else
    min_vtk_num=${tmp_num:0:4}; max_vtk_num=${tmp_num:5:4}; num_vtk_files=$(( 10#$max_vtk_num-10#$min_vtk_num+1 ))
fi
echo "vtk_range" $min_vtk_num $max_vtk_num
tmp_num=$(comb_check.py ./ get_num_lis); 
if [ "$tmp_num" = "-1" ]; then
    min_lis_num="0"; max_lis_num="0"; num_lis_files=0
else
    min_lis_num=${tmp_num:0:4}; max_lis_num=${tmp_num:5:4}; num_lis_files=$(( 10#$max_lis_num-10#$min_lis_num+1 ))
fi
echo "lis_range" $min_lis_num $max_lis_num
tmp_num=$(comb_check.py ./ get_num_dpar); 
if [ "$tmp_num" = "-1" ]; then
    min_dpar_num="0"; max_dpar_num="0"; num_dpar_files=0
else
    min_dpar_num=${tmp_num:0:4}; max_dpar_num=${tmp_num:5:4}; num_dpar_files=$(( 10#$max_dpar_num-10#$min_dpar_num+1 ))
fi
echo "dpar_range" $min_dpar_num $max_dpar_num

num_ids=`ls -d ./id* | wc -l`
if [ -d comb ]; then
    num_comb_vtk_files=`ls comb/*[0-9].vtk | wc -l`; num_comb_lis_files=`ls comb/*.all.lis | wc -l`
else
    num_comb_vtk_files=0; num_comb_lis_files=0
fi
if [ -d comb_dparvtk ]; then num_comb_dpar_files=`ls comb_dparvtk/*.dpar.vtk | wc -l`; else num_comb_dpar_files=0; fi

echo "there are $num_vtk_files vtk, $num_lis_files lis, $num_dpar_files dpar.vtk in each of $num_ids id* folder"

echo "Current time" `date +"%T"`
if [ "$2" = "1" ]; then
    echo "Skip combination step"
else
    if [ $num_vtk_files -gt 0 ]; then
        echo "Combining *.vtk"
        if [ $num_vtk_files -eq $num_comb_vtk_files ]; then
            echo "It seems $num_comb_vtk_files vtk files have already been combined. Skip..."
        else
            # either mine_joinvtk or join_vtk can't handle numbers with leading zero (will be treated as octal numbers)
            join_ath $num_ids comb vtk $((10#$min_vtk_num)):$((10#$max_vtk_num)) $1 > ./join_vtk_log.txt 2>& 1 &
            pids[0]=$! # get the PID of the last command launched in background.
            echo "PID for join vtk is ${pids[0]}"
        fi
    fi

    if [ $num_lis_files -gt 0 ]; then
        echo "Combining *.all.lis"
        if [ $num_lis_files -eq $num_comb_lis_files ]; then
            echo "It seems $num_comb_lis_files lis files have already been combined. Skip..."
        else
            join_ath $num_ids comb all.lis $((10#$min_lis_num)):$((10#$max_lis_num)) $1 > ./join_lis_log.txt 2>& 1 &
            pids[1]=$!
            echo "PID for join lis is ${pids[1]}"
        fi
    fi

    if [ $num_dpar_files -gt 0 ]; then
        echo "Combining *.dpar.vtk"
        if [ $num_dpar_files -eq $num_comb_dpar_files ]; then
            echo "It seems $num_comb_dpar_files dpar.vtk files have already been combined. Skip..."
        else
            join_ath $num_ids "comb_dparvtk" dpar.vtk $((10#$min_dpar_num)):$((10#$max_dpar_num)) $1 > ./join_dpar_log.txt 2>& 1 &
            pids[2]=$!
            echo "PID for join dpar.vtk is ${pids[2]}"
        fi
    fi

    echo "Waiting"
    for pid in ${pids[*]}; do
        wait $pid
    done

    echo -e "Current time" `date +"%T"` "\nDone combination" 
fi

echo "Checking combined results"
# the python script already assumes the name "comb"
comb_check.py ./ "comb_dparvtk"

if [ "$3" = "1" ]; then
    echo "Skip asking for deletion permission due to user input."
    key='y'
else
    read -p $'Continue to delete files in ./id*/ ??? [y/n]\n' key
    echo -e "Current time" `date +"%T"` "\nGet input: " $key
fi

if [ "$key" = 'y' ]; then
    echo -e "Permission granted. Proceed..." "\nCurrent time" `date +"%T"`
    let "max_id=$num_ids-1"

    if [ $num_vtk_files -gt 0 ]; then
        echo "Deleting id*/[$min_vtk_num...$max_vtk_num].vtk"
        for ex in `seq -w $min_vtk_num $max_vtk_num`; do rm id0/Parsg_Strat2d.$ex.vtk; for nima in `seq 1 $max_id`; do rm id$nima/Parsg_Strat2d-id$nima.$ex.vtk; done; done &
        pids[0]=$!
        echo "PID for rm vtk is ${pids[0]}"
    fi

    if [ $num_lis_files -gt 0 ]; then
        echo "Deleting id*/[$min_lis_num...$max_lis_num].all.lis"
        for ex in `seq -w $min_lis_num $max_lis_num`; do rm id0/Parsg_Strat2d.$ex.all.lis; for nima in `seq 1 $max_id`; do rm id$nima/Parsg_Strat2d-id$nima.$ex.all.lis; done; done &
        pids[1]=$!
        echo "PID for rm lis is ${pids[1]}"
    fi 
    
    if [ $num_dpar_files -gt 0 ]; then
        echo "Deleting id*/[$min_dpar_num...$max_dpar_num].dpar.vtk"
        for ex in `seq -w $min_dpar_num $max_dpar_num`; do rm id0/Parsg_Strat2d.$ex.dpar.vtk; for nima in `seq 1 $max_id`; do rm id$nima/Parsg_Strat2d-id$nima.$ex.dpar.vtk; done; done &
        pids[2]=$!
        echo "PID for rm dpar.vtk is ${pids[2]}"
    fi

    echo "Waiting"
    for pid in ${pids[*]}; do
        wait $pid
    done

    echo -e "Current time" `date +"%T"` "\nDone deletion"
else
    echo "Permission denied. Abort..."
fi
