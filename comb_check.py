#!/usr/bin/env python3

import os, glob, sys
import pyridoxine.utility as rxu
import numpy as np
from time import sleep

def quick_check(data_dir, problem_id, out_num, ext=".all.lis", sub_dir='comb'):
    if sub_dir is None: sub_dir = 'comb'
    print("checking", data_dir+"/"+sub_dir+"/"+problem_id+".{:04d}".format(out_num)+ext)
    if ext[-3:] == 'lis':
        b = rxu.AthenaMultiLIS(data_dir, problem_id, "{:04d}".format(out_num)+ext, silent=False)
        bc = rxu.AthenaLIS(data_dir+"/"+sub_dir+"/"+problem_id+".{:04d}".format(out_num)+ext, silent=False)
        for name in ['pos', 'vel', 'den', 'property_index', 'id', 'cpu_id']:
            rxu.minmax(b[name] - bc[name])
    if ext[-3:] == 'vtk':
        b = rxu.AthenaMultiVTK(data_dir, problem_id, "{:04d}".format(out_num)+ext, silent=False)
        bc = rxu.AthenaVTK(data_dir+"/"+sub_dir+"/"+problem_id+".{:04d}".format(out_num)+ext, silent=False)
        for name in b.names:
            rxu.minmax(b[name] - bc[name])

def get_problem_id(data_dir):
    files = glob.glob(data_dir+"/*.phst"); 
    phst_path = glob.glob(data_dir+"/*.phst")[0]
    problem_id = phst_path[phst_path.find('/')+1:-5]
    return problem_id

def get_file_num(data_dir, ext=".lis", problem_id="Parsg_Strat2d"):
    files = glob.glob(data_dir+"/id1/*"+ext); 
    if len(files) > 0:
        files.sort()
        e = ".vtk" if ext=="[0-9].vtk" else ext
        print(str(files[0][-len(e)-4:-len(e)])+' '+str(files[-1][-len(e)-4:-len(e)]))
    else:
        print("-1")

def check_file_size(data_dir, ext=".all.lis", sub_dir='comb'):
    files = glob.glob(data_dir+"/"+sub_dir+"/*"+ext); files.sort()
    e = ".vtk" if ext=="[0-9].vtk" else ext
    out_ids = np.array([int(x[-len(e)-4:-len(e)]) for x in files]); #print(out_ids)
    sizes = [os.path.getsize(x) for x in files]
    if len(sizes) > 0:
        rxu.minmax(sizes); print("# of files:", len(sizes))
    else:
        print('no file found with ext: '+ext)
    return len(files), out_ids

def comb_check(data_dir, dpar_dir=None, selected_id=None):
    files = glob.glob(data_dir+"/*.phst"); 
    phst_path = glob.glob(data_dir+"/*.phst")[0]
    problem_id = phst_path[phst_path.find('/')+1:-5]
    random_id_flag = True if selected_id is None else False
    print("Checking file size:")
    print("vtk")
    num_vtk, vtk_ids = check_file_size(data_dir, ext="[0-9].vtk")
    print("lis")
    num_lis, lis_ids = check_file_size(data_dir)
    print("dpar.vtk")
    if dpar_dir is None:
        num_dpar, dpar_ids = check_file_size(data_dir, ext='.dpar.vtk')
    else:
        num_dpar, dpar_ids = check_file_size(data_dir, ext='.dpar.vtk', sub_dir=dpar_dir)
    
    print("Checking file content:")
    if num_vtk > 0:
        num_file = num_vtk; e = ".vtk"; print(e)
        if os.path.exists(data_dir+"/id0/"+problem_id+"."+"{:04d}".format(vtk_ids[0])+e) > 0:
            if random_id_flag: selected_id = np.random.choice(vtk_ids, 3)
            for item in selected_id: quick_check(data_dir, problem_id, item, ext=e)
        else:
            print("no such file in id0, skip check:", data_dir+"/id0/"+problem_id+"."+"{:04d}".format(vtk_ids[0])+e)
    if num_lis > 0:
        num_file = num_lis; e = ".all.lis"; print(e)
        if os.path.exists(data_dir+"/id0/"+problem_id+"."+"{:04d}".format(lis_ids[0])+e) > 0:
            if random_id_flag: selected_id = np.random.choice(lis_ids, 3)
            for item in selected_id: quick_check(data_dir, problem_id, item, ext=e)
        else:
            print("no such file in id0, skip check", data_dir+"/id0/"+problem_id+"."+"{:04d}".format(lis_ids[0])+e)
    if num_dpar > 0:
        num_file = num_dpar; e = ".dpar.vtk"; print(e)
        if os.path.exists(data_dir+"/id0/"+problem_id+"."+"{:04d}".format(dpar_ids[0])+e) > 0:
            if random_id_flag: selected_id = np.random.choice(dpar_ids, 3)
            for item in selected_id: quick_check(data_dir, problem_id, item, ext=e, sub_dir=dpar_dir)
        else:
            print("no such file in id0, skip check", data_dir+"/id0/"+problem_id+"."+"{:04d}".format(dpar_ids[0])+e)

if __name__ == "__main__":

    if len(sys.argv) == 2:
        comb_check(sys.argv[1])
    elif len(sys.argv) == 3:
        if sys.argv[2] == "get_num_vtk":
            get_file_num(sys.argv[1], ext='[0-9].vtk')
        elif sys.argv[2] == "get_num_lis":
            get_file_num(sys.argv[1], ext='.all.lis')
        elif sys.argv[2] == "get_num_dpar":
            get_file_num(sys.argv[1], ext='.dpar.vtk')
        else:
            comb_check(sys.argv[1], dpar_dir=sys.argv[2])