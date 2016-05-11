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

"""Class to get and store cl data.
"""

import os
import glob

from ctes import *
from kscrap import KScrap
from kfiles import extract_list_text

class ClDat(object):
    
    def __init__(self, index = DEFAULT_INDEX):
        
        self._index = index
        self._b1 = []
        self._a2 = []
        
        # Try read data from a local file.
        self._read_cldata()
            
        # If not read from local, retrieve from external source.
        if not self.loaded:
            self._b1, self._a2 = KScrap.scrap_cl_data()
            
            if self.loaded:
                self._save_cldata()
            else:
                # If data isn't retrieved, update the index with the value 
                # received.
                self._index = index
                
                
    def _get_file_to_read(self):
        
        file_name = ''
        
        if self._index != DEFAULT_INDEX:
            file_name = PREFIX_CL_FILE_NAME + self._index + SCRAPPED_DATA_FILE_EXT
        else:
            cl_files = glob.glob("%s*" % PREFIX_CL_FILE_NAME)
            
            if len(cl_files):
            
                cl_files.sort()
            
                file_name = cl_files[-1]         
            
        return file_name
                
    def _read_cldata(self):
        
        lines = []   
        
        file_name = self._get_file_to_read()
        
        if len(file_name):
            print "Reading data from file: %s" % file_name
            
            try:
                with open(file_name, "r") as f:
                    for l in f:
                        
                        # Process text line.        
                        l_txt = l[:-1].strip()
                        
                        if len(l_txt):    
                                          
                            if l_txt.find(B1_TEXT) >= 0:
                                
                                l_text = extract_list_text(l_txt, NUM_COLS_CL)
                                
                                for l in l_text:
                                    self._b1.append([l[i] for i in CL_ORDER])
                                
                                print "Read %dx%d from file for B1" % \
                                    (len(self._b1), len(self._b1[0]))
                                
                            elif l_txt.find(A2_TEXT) >= 0:
                                
                                l_text = extract_list_text(l_txt, NUM_COLS_CL)
                                
                                for l in l_text:
                                    self._a2.append([l[i] for i in CL_ORDER])
                                
                                print "Read %dx%d from file for A2" % \
                                    (len(self._a2), len(self._a2[0]))
                                    
            except IOError as ioe:
                print "ERROR: Reading file '%s'" % file_name  
                self._b1 = []
                self._a2 = []
        else:
            print "No file found to read cl."
            
    def _save_cldata(self):
        
        out_file_name = PREFIX_CL_FILE_NAME + self._index + SCRAPPED_DATA_FILE_EXT
        
        try:
            
            with open(out_file_name, 'w') as f:
            
                f.write("%s %s %s\n\n" % (B1_TEXT, SCR_TXT_DELIM, str(self._b1)))
                f.write("%s %s %s\n" % (A2_TEXT, SCR_TXT_DELIM, str(self._a2))) 
            
            print "Data scrapped saved in: %s" % out_file_name
            
        except IOError as ioe:
             print "Error saving file: '%s'" % out_file_name  
        
    @property
    def b1(self):
        return self._b1
    
    @property
    def a2(self):
        return self._a2
    
    @property
    def index(self):
        return self._index
    
    @property
    def loaded(self):
        return len(self._b1) and len(self._a2)