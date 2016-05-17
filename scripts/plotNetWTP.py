#!/usr/bin/env python
#
#  Copyright 2012-2016 Aerospike, Inc.
#
#  Portions may be licensed to Aerospike, Inc. under one or more contributor
#  license agreements WHICH ARE COMPATIBLE WITH THE APACHE LICENSE, VERSION 2.0.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not
#  use this file except in compliance with the License. You may obtain a copy of
#  the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations under
#  the License.
#
#################################################################################
#
#  Purpose: This application graphs output from dstat.
#           Dstat must be used with the following options:
#
#           dstat -Tcmndr --output  dstat.out
#
#################################################################################
# import modules
import json
import math
import glob
import os
import sys
import getopt
import time
import datetime
import numpy as np
import csv
import datetime
import matplotlib as mlab
mlab.use('Agg')
import matplotlib.pyplot as plt

def main(argv):

   # initialize some variable to be lists:
   i = 1
   x1 = []
   y1 = []

   # Read command line args
   inputfile = ''
   outputfile = ''
   try:
     opts, args = getopt.getopt(argv,"hi:o:d:",["ifile=","ofile="])
   except getopt.GetoptError:
     print 'plotNetWTP.py -i <inputfile> -o <outputfile>'
     sys.exit(2)

   for opt, arg in opts:
     if opt == '-h':
       print 'plotNetWTP.py -i <inputfile> -o <outputfile>'
       sys.exit()
     elif opt in ("-i", "--ifile"):
       inputfile = arg
     elif opt in ("-o", "--ofile"):
       outputfile = arg
     elif opt in ("-d"):
       dbname = arg

   with open(inputfile,'r') as csvfile:
       plots = csv.reader(csvfile, delimiter=',')
    
       seconds = 0
       for row in plots:
           x1.append(seconds)
           y1.append(float(row[12]))
           seconds +=1

   fig = plt.figure(figsize=[10,9])
   tmp_title = dbname.upper() + " Net Write Throughput"
   fig.suptitle(tmp_title, fontsize=18)
   plt.xlabel('Time(s)', fontsize=16)
   plt.ylabel('Bytes', fontsize=16)
   plt.tick_params(labelsize=10)
   plt.xticks(rotation=70)

    
   xv = np.array(x1)
   yv = np.array(y1)


   plt.plot(xv, yv,color=[0.0/255,0.0/255,255.0/255])

   plt.savefig(outputfile)

if __name__ == "__main__":
   main(sys.argv[1:])

