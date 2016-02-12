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

"""Composition of different data.
"""

import csv
import numpy as np
from ctes import *
from qscraping import *

class ComposeData(object):
    
    def __init__(self, scr, index_data, pro_data, pre_data):
  
        self._scr = scr
        self._index_data = index_data
        self._pro_data = pro_data
        self._pre_data = pre_data
  
        self._compdata = \
            [[0 for _ in range(TOTAL_NUM_COLS)] for _ in range(NUM_ROWS)]
            
    def _fill_data(self):
        
        max_offset = 0
        
        len_index = len(self._index_data[0])

        # First local names.
        for i in range(NUM_ROWS):
            for j in range(len_index):
                self._compdata[i][j] = self._index_data[i][j]
        
        # Calculate the offset (column) where to start each data block.
        pro_offset = len_index
        pre_offset = pro_offset + len(self._pro_data[0])
        lm_offset = pre_offset + len(self._pre_data[0])
        ve_offset = lm_offset + len(self._scr.lm_data[0])
        qu_offset = ve_offset + len(self._scr.ve_data[0])
        q1_offset = qu_offset + len(self._scr.qu_data[0]) 
        mean_offset = q1_offset + len(self._scr.q1_data[0]) 
        
        for i in range(NUM_ROWS):
            
            # Values to calculate the maximum values of each block.
            max_sign_val = [0] * NUM_EXT_SOURCES
            max_sign_str = [''] * NUM_EXT_SOURCES
            
            for j in range(NUM_COLS):
                
                # Fill with data scraped. 
                self._compdata[i][j + pro_offset] = self._pro_data[i][j]
                self._compdata[i][j + pre_offset] = self._pre_data[i][j]
                self._compdata[i][j + lm_offset] = self._scr.lm_data[i][j]
                self._compdata[i][j + ve_offset] = self._scr._ve_data[i][j]
                self._compdata[i][j + qu_offset] = self._scr._qu_data[i][j]
                self._compdata[i][j + q1_offset] = self._scr._q1_data[i][j]
                
                # Calculate a mean of the data scraped for this column.                
                val_np_arr = np.array([int(self._pro_data[i][j]), \
                                      int(self._pre_data[i][j]), \
                                      int(self._scr.lm_data[i][j]), \
                                      int(self._scr._ve_data[i][j]), \
                                      int(self._scr._qu_data[i][j]), \
                                      int(self._scr._q1_data[i][j])]) 
                                 
                self._compdata[i][j + mean_offset] = np.mean(val_np_arr)
                                
                curr_sign_max = CURRENT_MAX[j]
                
                for k in range(NUM_EXT_SOURCES):
                    if val_np_arr[k] > max_sign_val[k]:
                        max_sign_val[k] = val_np_arr[k]
                        max_sign_str[k] = curr_sign_max   
                        
            # A set of the maximum values.            
            max_sign_set = set()                                                                                
            
            # Fill highest value of each external.        
            max_sign_offset = mean_offset + NUM_COLS   
            
            for k in range(NUM_EXT_SOURCES):
                self._compdata[i][max_sign_offset + k] = max_sign_str[k] 
                max_sign_set.add(max_sign_str[k])
                         
            # Fill summary of highest values.
            self._compdata[i][max_sign_offset + NUM_EXT_SOURCES] = \
                ''.join(list(max_sign_set))
                
            mat_offset = max_sign_offset + NUM_EXT_SOURCES + 1
            
            # Fill data for each name.
            name_lo_data = []
            name_vi_data = []
                
            if self._compdata[i][TYPE_COL] == TYPE_1_COL:
                name_lo_data = self._scr.get_data_from_b1(self._compdata[i][NAME_LO_COL])
                name_vi_data = self._scr.get_data_from_b1(self._compdata[i][NAME_VI_COL], False)
            else:
                name_lo_data = self._scr.get_data_from_a2(self._compdata[i][NAME_LO_COL])
                name_vi_data = self._scr.get_data_from_a2(self._compdata[i][NAME_VI_COL], False)               
                
            for k in range(NAME_DATA_LEN):
                self._compdata[i][mat_offset + k] = int(name_lo_data[k])
                
            for k in range(NAME_DATA_LEN):
                self._compdata[i][mat_offset + k + NAME_DATA_LEN] = int(name_vi_data[k])  
                
            max_offset = mat_offset + 2 * NAME_DATA_LEN
            
        return mat_offset, mean_offset
        
    def _calculate(self, mat_offset, mean_offset):        
        
        # Calculate Ps depending on the data for each one.
        for i in range(NUM_ROWS):
            p_with = 1.0
            
            if self._compdata[i][TYPE_COL] == TYPE_1_COL: 
                p_with = P_WITH_B1
            else:
                p_with = P_WITH_A2
                
            p_lo_sum = 0.0
            p_lo_1 = 0.0
            p_lo_2 = 0.0
            p_lo_3 = 0.0
                   
            p_vi_sum = 0.0  
            p_vi_1 = 0.0
            p_vi_2 = 0.0
            p_vi_3 = 0.0   
                
            for k in range(NAME_DATA_LEN):
                p_lo_sum += self._compdata[i][mat_offset + k]                
                p_vi_sum += self._compdata[i][mat_offset + NAME_DATA_LEN + k]
                
            p_lo_sum *= 1.0
            p_vi_sum *= 1.0

            if p_lo_sum > 0.0:
                p_lo_1 = ( 1.0 * self._compdata[i][mat_offset] ) / p_lo_sum
                p_lo_2 = ( 1.0 * self._compdata[i][mat_offset + 1] ) / p_lo_sum
                p_lo_3 = ( 1.0 * self._compdata[i][mat_offset + 2] ) / p_lo_sum
            
            if p_vi_sum > 0.0:
                p_vi_1 = ( 1.0 * self._compdata[i][mat_offset + NAME_DATA_LEN] ) / p_vi_sum
                p_vi_2 = ( 1.0 * self._compdata[i][mat_offset + NAME_DATA_LEN + 1] ) / p_vi_sum
                p_vi_3 = ( 1.0 * self._compdata[i][mat_offset + NAME_DATA_LEN + 2] ) / p_vi_sum 
            
            p_13 = p_lo_1 * p_vi_3
            p_22 = p_lo_2 * p_vi_2
            p_31 = p_lo_3 * p_vi_1   
                
            p_1 = 0.0
            p_2 = 0.0                 
            p_3 = 0.0
            
            if p_with > 0.0:
                p_1 = p_13 * self._compdata[i][mean_offset] / p_with
                p_2 = p_22 * self._compdata[i][mean_offset + 1] / p_with                     
                p_3 = p_31 * self._compdata[i][mean_offset + 2] / p_with  
            
            p_sum = p_1 + p_2 + p_3
            
            p_1_final = 0.0
            p_2_final = 0.0
            p_3_final = 0.0        
            
            if p_sum > 0.0:
                p_1_final = 100.0 * p_1 / p_sum
                p_2_final = 100.0 * p_2 / p_sum
                p_3_final = 100.0 * p_3 / p_sum 
                
            st_offset = mat_offset + NAME_DATA_LEN * 2 
            
            self._compdata[i][st_offset] = round(p_1_final)
            self._compdata[i][st_offset + 1] = round(p_2_final)  
            self._compdata[i][st_offset + 2] = round(p_3_final) 
            
            # Set the values over the minimum.
            p_dict = { MAX_IS_FIRST : p_1_final, \
                      MAX_IS_SECOND : p_2_final, \
                      MAX_IS_THIRD: p_3_final }
            
            keys_sorted = sorted(p_dict) 
            
            val = keys_sorted[0]   
            
            for i in [1,2]:             
                if p_dict[keys_sorted[i]] > MIN_PER:   
                    val += keys_sorted[i]                   
            
            self._compdata[i][st_offset + 3] = val              
        
    def _write_data(self):
        
        output_file_name = PREFIX_OUTPUT_FILE_NAME + \
            self._scr.index + OUTPUT_FILE_NAME_EXT        
        
        print "Saving results in: %s" % output_file_name    
                    
        with open(output_file_name, "w") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=CSV_DELIMITER)            
            
            for i in range(len(self._compdata)):
                csvwriter.writerow(self._compdata[i])

                         
    def compose(self):
        
        # Fill with source data from index.
        mat_offset, mean_offset = self._fill_data()
        
        # Calculations.
        self._calculate(mat_offset, mean_offset)
        
        # Write results.  
        self._write_data()      