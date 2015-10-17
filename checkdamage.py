#!/usr/bin/env python
# This program is used to check the file loss
#
import subprocess, shlex
import numpy as np


# main function
if __name__ == '__main__':

    # args
    import argparse
    parser = argparse.ArgumentParser(description="This is an script to check file loss.")
    parser.add_argument('-v', '--vtk', dest='vtk', help='Number of vtk files.', type=int, default=1257)
    parser.add_argument('-l', '--lis', dest='lis', help='Numver of lis files.', type=int, default=1257)
    parser.add_argument('-s', '--size', dest='size', help='Size of one vtk file.', type=str, default="513M")
    parser.add_argument('-c', '--cap', dest='cap', help='Size of one lis file.', type=str, default="353M")
    args = parser.parse_args()

    # check vtk file loss
    vtks = subprocess.check_output(shlex.split("ll *.vtk")).decode('utf-8')
    vtks = vtks.split('\n')
    vtks = [item for item in vtks if len(item) != 0]
    j = 0
    for i in range(args.vtk):
        if j < len(vtks):
            if int(vtks[j].split()[-1].split('.')[1]) == i:
                if vtks[j].split()[3] != args.size:
                    print("Damaged file: ", vtks[j].split()[-1])
                j += 1                    
            else:
                print("No vtk: ", i)
        else:
            print("No vtk: ", i)

    # check lis file loss
    liss = subprocess.check_output(shlex.split("ll *.lis")).decode('utf-8')
    liss = liss.split('\n')
    liss = [item for item in liss if len(item) != 0]
    j = 0
    for i in range(args.lis):
        if j < len(liss):
            if int(liss[j].split()[-1].split('.')[1]) == i:
                if liss[j].split()[3] != args.cap:
                    print("Damaged file: ", liss[j].split()[-1])
                j += 1                    
            else:
                print("No lis: ", i)
        else:
            print("No lis: ", i)
