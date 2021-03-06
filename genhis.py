#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Felipe Gallego. All rights reserved.
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Generate an historical.
"""

import sys

from ctes import *
from clda import ClDat
from pro import Pro
from pre import Pre
from pdat import PDat
from putil import combine_lo_vi, get_cl_data_for_name
from kfiles import read_res_file, read_input_file, save_data_to_csv

NUM_ARGS = 2

def calc_pro_data(r, cl_data):
    
    calc_lo_data, _ = Pro.get_data_for_pro(r[R_NAME_1_COL], LO_P_RANGE, cl_data)
    
    calc_vi_data, _ = Pro.get_data_for_pro(r[R_NAME_2_COL], VI_P_RANGE, cl_data)
    
    return combine_lo_vi(calc_lo_data, calc_vi_data)

def calc_pre_data(r, cl_data, res_data):
    
    lo_data, lo_target_data = Pre.get_data_for_pre(r[R_NAME_1_COL], cl_data, 
                                                   res_data, True)   
    
    lo_mdl = Pre.get_mdl(r[R_NAME_1_COL])
    
    lo_pre = Pre.get_pre_values(lo_data, lo_target_data, lo_mdl.lo_mdls)  
    
    vi_data, vi_target_data = Pre.get_data_for_pre(r[R_NAME_2_COL], cl_data, 
                                                   res_data, False)
    
    vi_mdl = Pre.get_mdl(r[R_NAME_2_COL])           

    vi_pre = Pre.get_pre_values(vi_data, vi_target_data, vi_mdl.vi_mdls)
    
    return combine_lo_vi(lo_pre, vi_pre)

def gen_hist(res, cl, file_name, p_type):
    
    print "Generating historical data for: %s" % file_name
    
    hist = read_input_file(file_name)
    
    j_res_max = max([ int(r[R_J_COL]) for r in res
                     if int(r[R_J_COL]) >= FIRST_ENTRY_HIST])
    
    for j in range(FIRST_ENTRY_HIST, j_res_max + 1):
        
        res_j = [ r for r in res if int(r[R_J_COL]) == j ]
        
        res_data = [ r for r in res if int(r[R_J_COL]) < j ]
        
        for r in res_j:  
            
            new_row = [int(p_type), r[R_M_COL]] 
            
            if HIST_TYPE:       
                pro_data = calc_pro_data(r, cl)
                pre_data = calc_pre_data(r, cl, res_data)
                p_data = PDat.calc_final_p(pro_data, pre_data, p_type)
                
                new_row = [int(p_type), r[R_M_COL]]
                new_row.extend(pro_data)
                new_row.extend(pre_data)
                new_row.extend(p_data)
                new_row.extend([r[R_NAME_1_COL], r[R_NAME_2_COL]])
            else:
                cl_lo = get_cl_data_for_name(r[R_NAME_1_COL], cl)
                new_row.extend([cl_lo[i] for i in LO_D_RANGE])
                
                cl_vi = get_cl_data_for_name(r[R_NAME_2_COL], cl)
                new_row.extend([cl_vi[i] for i in VI_D_RANGE])
                
            new_row.extend([r[R_NAME_1_COL], r[R_NAME_2_COL]])
            
            hist.append(new_row)
            
    save_data_to_csv(file_name, hist)
    
    return hist

def load_local_data(index, cl_b1, cl_a2):
    
    kdat = KDat(index)
    
    pro = Pro(index, kdat.k, cl_b1, cl_a2)
    
    pre = Pre(index, kdat.k, cl_b1, cl_a2)
    
    pdat = PDat(index, kdat.k, cl_b1, cl_a2)
    
    return kdat.loaded and pro.generated and pre.generated, \
            kdat.k, pro.pro, pre.pre, pdat.p

def generate_final_hist(index, b1_hist, a2_hist, k, pro_data, pre_data, p_data, cldat):
    
    hist = b1_hist + a2_hist
    
    for i, k_elt in enumerate(k):
        
        if k_elt[K_TYPE_COL] == TYPE_1_COL:
            cl = cldat.b1
        else:
            cl = cldat.a2
        
        new_row = [int(k_elt[TYPE_COL]), '']
        
        if HIST_TYPE:             
            new_row.extend(pro_data[i])
            new_row.extend(pre_data[i])
            new_row.extend(p_data[i])
        else:
            cl_lo = get_cl_data_for_name(k_elt[NAME_LO_COL], cl)
            new_row.extend([cl_lo[i] for i in LO_D_RANGE])
            
            cl_vi = get_cl_data_for_name(k_elt[NAME_VI_COL], cl)
            new_row.extend([cl_vi[i] for i in VI_D_RANGE])        
            
        new_row.extend([k_elt[NAME_LO_COL], k_elt[NAME_VI_COL]])
        
        hist.append(new_row)
    
    save_data_to_csv(AP_HIST_FILE, hist)

def main(index = DEFAULT_INDEX):
    
    b1_res = read_res_file(B1_RES_FILE)
    a2_res = read_res_file(A2_RES_FILE)
    
    if len(b1_res) and len(a2_res):
        
        cldat = ClDat()
        
        if cldat.loaded:
            b1_hist = gen_hist(b1_res, cldat.b1, HIST_FILE_B1, TYPE_1_COL)
            a2_hist = gen_hist(a2_res, cldat.a2, HIST_FILE_A2, TYPE_2_COL)
            
            if index != DEFAULT_INDEX:
                
                success, k, pro, pre, p = load_local_data(index, cl.b1, cl.a2)
                
                if success:
                    generate_final_hist(index, b1_hist, a2_hist, k, pro, pre, p, cldat)
                else:
                    print "ERROR: Generation of historical not possible, local data not available."
        else: 
            print "ERROR: Generation of historical not possible, cl not available."
    else:
        print "ERROR: Generation of historical not possible, res not available."

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        main(sys.argv[1])
