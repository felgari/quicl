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

"""Script to get a web page.
"""

import sys
import csv
from ctes import *
from kscraping import *
from compdata import *
    
NUM_ARGS = 2

def read_input_file(input_file_name):
             
    print "Reading local file: %s" % input_file_name
                
    data = []

    try:
        with open(input_file_name, 'rb') as f:
            
            reader = csv.reader(f)
        
            for row in reader:
                if row[0].isdigit():
                    data.append(row)
                else:
                    print "Ignoring line in file %s, maybe a header: %s" % \
                        (input_file_name, row)
        
    except csv.Error:
        print "ERROR: reading file %s" % input_file_name
    except IOError as ioe:
        print "ERROR: reading file %s" % input_file_name
            
    return data  

def main():
    """Main function.
    """    
    
    print "Let's go ..."
    
    # Do scraping.
    scr = KScraping()

    scr.scrap_pre_data()    
    
    # Read local data.
    local_index_file_name = K_FILE_NAME_PREFIX + scr.index + INPUT_FILE_NAME_EXT
    local_index_data = read_input_file(local_index_file_name)
    
    pro_file_name = PRO_FILE_NAME_PREFIX + scr.index + INPUT_FILE_NAME_EXT
    local_pro_data = read_input_file(pro_file_name)
    
    pre_file_name = PRE_FILE_NAME_PREFIX + scr.index + INPUT_FILE_NAME_EXT    
    local_pre_data = read_input_file(pre_file_name)   
    
    if len(local_index_data) > 0 and len(local_pro_data) and \
        len(local_pre_data) > 0:
        
        scr.scrap_post_data()
    
        # Compose data.
        compdat = ComposeData(scr, local_index_data, local_pro_data, local_pre_data)
        
        compdat.compose()
        
    print "Program finished."
    
    return 0

# Where all begins ...
if __name__ == "__main__":
    
    sys.exit(main())
