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
import datetime
import matplotlib as mlab
mlab.use('Agg')
import matplotlib.pyplot as plt



class Interval:

   #Member variables
  
   histogram = np.array([])
   starttime = 0.0
   endtime = 777777777.0
   tp=3000


   def SetTP(self, value):
     self.tp = value

   def SumTP(self, value):
     self.tp = self.tp+value

   def GetTP(self):
     return self.tp
   
   def SetStartTime(self, value):
     self.starttime = value

   def GetStartTime(self):
     return self.starttime
    
   def SetStartTime(self, value):
     self.starttime = value

   def GetStartTime(self):
     return self.starttime
    

def main(argv):
   client_data_list = ([],[])
   TPData = np.array([])
   PCTData = np.array([])
   BinData = np.array([])
   inputfiles = []
   ycsb_json = []
   bucket_format = "linear"

   # CHECK: Have to think about the duration
   start_time=''
   end_time=''
   slice_count=0
   buckets= 1000
   run_duration=30

   noconvert=1 
   zero_time=0
   chkcount=0
   client_cnt=0 
   slice_throughput=0
   previous_st=0
   percentile=0.95
   max_tp=0

   # Store input and output file names


   # Read command line args
   fileoffiles = ''
   dbname = ''
   try:
     opts, args = getopt.getopt(argv,"hi:d:",["ifile=","dbname="])
   except getopt.GetoptError:
     print 'plotReadData.py -i <fileoffiles> -d <dbname>'
     sys.exit(2)

   for opt, arg in opts:
     if opt == '-h':
       print 'plotDiskRIOPS.py -i <fileoffiles> -d <dbname>'
       sys.exit()
     elif opt in ("-i", "--ifile"):
       fileoffiles = arg
     elif opt in ("-d", "--dbname"):
       dbname = arg


###################################################
#   Load Data 
###################################################
   with open(fileoffiles) as f:
     for line in f:
       tmp = line[:-1]
       inputfiles.append(tmp)
 	
   # Initialize Bins to Zero
   

   print "CLIENTS ::::",inputfiles
   # Loop through clients aggregating the data
   for filenames in inputfiles:
     print filenames
     slice_count=0
     previous_st=0
     zero_time=0
     print "CLIENT COUNT: ", client_cnt

     #Have to alter this loop  to handle ranges
     #Open file for aggregation
     with open(filenames) as f:
       for line in f:
         ycsb_json=json.loads(line)
         slice_count +=1 

         st= math.floor(float(ycsb_json['start']))

         #Set a zero_time to adjust index size
         #Python List indexes have limited size and the Epoch can not be used.
         if not zero_time:
           zero_time=st
           data_scale=ycsb_json["scale"]
           print "SCALE!!!:", data_scale;

         #Set slice index
         slice_idx=int(st - zero_time)

#         print "ST = ", slice_idx, "PREV ST = ", previous_st
	 if (slice_idx -previous_st) > 1:
           slice_idx = previous_st+1
           previous_st = slice_idx   
         else:
           previous_st = slice_idx   
         
         #Check if object does not exist insert

         try: 
            chk=client_data_list[client_cnt][slice_idx]
         except IndexError:
            client_data_list[client_cnt].insert(slice_idx, Interval())
            client_data_list[client_cnt][slice_idx].tp=0

         if "linear" in ycsb_json:
            bucket_format="linear"
         elif "range" in ycsb_json:
            bucket_format="range"
         elif "log2" in ycsb_json:
            bucket_format="log2"
		
         # Aggregate the Data 
         if bucket_format == "linear":
            # Need to set up the number of buckets correctly
            for y in range(0, buckets):  
              if str(y) in ycsb_json[bucket_format]:
                 #Insert Data point into histogram array
                 client_data_list[client_cnt][slice_idx].histogram = np.insert(client_data_list[client_cnt][slice_idx].histogram,y, [(ycsb_json["linear"][str(y)])],0)
                 client_data_list[client_cnt][slice_idx].tp += ycsb_json["linear"][str(y)]
              else:
                 client_data_list[client_cnt][slice_idx].histogram=np.insert( client_data_list[client_cnt][slice_idx].histogram, y, [(0)],0)
	 elif bucket_format == "log2":
            print "aggregate log2"
	 elif bucket_format == "range":
            print "aggregate range"

#         print client_data_list[client_cnt][slice_idx].histogram
         print "Get Next Slice: ", slice_count

     client_cnt += 1

###################################################
#    END OF Load Data 
###################################################



###################################################
# Calculate Units
###################################################
   if data_scale == 0.001:
     units = "ms"
   elif data_scale == 0.0001:
     units = "tenths of a ms"
   elif data_scale == 0.00001:
     units = "hundredths of a ms"
   elif data_scale == 0.000001:
     units = "mu seconds"


###################################################
#For The Selected Range Process the Output
###################################################
   # Calculate the Throughput for Each Slice
   for i in range(0, slice_count-1):
     tmpcnt=0
     for j in range(0, client_cnt):
       tmpcnt += client_data_list[j][i].tp
     TPData = np.insert(TPData, i, tmpcnt, 0)
     if tmpcnt > max_tp:
        max_tp = tmpcnt

   # Calculate TOTAL Throughput
   tmpcnt=0
   for i in range(0, slice_count-1):
     tmpcnt += TPData[i]

   print "TOTAL THROUGHPUT:", tmpcnt
   print "SLICE_COUNT :",slice_count

#   print "MAX TP:", max_tp
#   ylim = float(max_tp) / 0.66
#   ylim = round(float(ylim)/10000.0) * 10000.0
#   print "YLIM TP:", ylim
   ylim = 110000


###################################################
# Generate Historgram for whole run
###################################################

   for i in range(0, buckets):
     tmpcnt=0 
     for j in range(0, slice_count-1):
       for k in range(0, client_cnt):
         tmpcnt += client_data_list[k][j].histogram[i]

     # Create bucket
     BinData = np.insert(BinData, i, tmpcnt, 0)



###################################################
# Plot the Histogram 
###################################################

   x1 = []
   y1 = []


   for row in BinData:
#     print row
     y1.append(row)

   for x in range(0,buckets):
     x1.append(x)
   

   y_pos = y1
   performance = x1

   fig, ax = plt.subplots()
   ax.set_yscale('log')
   ax.set_xlim(0,buckets)

   ax.bar(performance, y_pos, 1)


   tmp_title = dbname.upper() + " Latency Histogram(Log Scale)"
   ax.set_title(tmp_title)
   hist_xlabel = "Latency Bins in " + units
   ax.set_xlabel(hist_xlabel)
   ax.set_ylabel('Operations', color='b')

   fname = "ReadLogHist."+dbname+".png"
   plt.savefig(fname)

###################################################
# Normal Histogram
###################################################

   fig, ax = plt.subplots()
   ax.set_xlim(0,buckets)

   ax.bar(performance, y_pos, 1)


   tmp_title = dbname.upper() + " Read Latency Histogram"
   ax.set_title(tmp_title)
   hist_xlabel = "Latency Bins in " + units
   ax.set_xlabel(hist_xlabel)
   ax.set_ylabel('Operations', color='b')

   fname = "ReadHist."+dbname+".png"
   plt.savefig(fname)


###################################################
# Generate
###################################################

   # Generate Percentile 
   # For Each slice fin the 95 pct
   max_lat=0
   for i in range(0, slice_count-1):
     tmp_buckets = np.zeros(buckets)
     tmp_tp = 0
     for j in range(0, client_cnt):
       tmp_tp += client_data_list[j][i].tp
       for k in range(0, buckets):
          tmp_buckets[k] += client_data_list[j][i].histogram[k]

     # Do Calculation
     Pct = percentile * tmp_tp

     #Determine Latency at xPct
     tmp_tot = 0
     bin_num = 0 
     for x in range(0, buckets):
       if tmp_tot > Pct:
         #Set Percenttile and break
         bin_num = x
         if bin_num > max_lat:
            max_lat = bin_num
         break
       else:
         tmp_tot += tmp_buckets[x]

#     print "BIN NUM :", bin_num
     PCTData = np.insert(PCTData, i, bin_num, 0)
       
    
#   print "MAX LAT:", max_lat
#   ylim2 = float(max_lat) / 0.5
#   ylim2 = round(float(ylim2)/10.0) * 10.0
#   print "YLIM TP:", ylim2
   ylim2 = 1000



###################################################
# Plot Read Throughput
###################################################

   i = 1
   x1 = []

   for n in range(0,slice_count-1):
     x1.append(n)

   xv = np.array(x1)

   fig, ax1 = plt.subplots()

   tmp_title = dbname.upper() + " Read Throughput"
   ax1.set_title(tmp_title)
   ax1.set_ylim(0,int(ylim))
   ax1.plot(xv, TPData, 'b-')
   ax1.set_xlabel('time (s)')
   ops='Operations ('+str(percentile*100)+" percentile)"
   ax1.set_ylabel(ops, color='b')


   fname = "ReadThroughput."+dbname+".png"
   plt.savefig(fname)

###################################################
# Plot Read  Latency
###################################################
   i = 1
   x1 = []

   for n in range(0,slice_count-1):
     x1.append(n)

   xv = np.array(x1)

   fig, ax1 = plt.subplots()

   tmp_title = dbname.upper() + " Read Latency"
   ax1.set_title(tmp_title)
   ax1.set_ylim(0,ylim2)
   ax1.plot(xv, PCTData, 'r-')
   ax1.set_xlabel('time (s)')
   lat_label = "Labency for "+str(percentile*100)+" Percentile"+ " in "+ str(units)
   ax1.set_ylabel(lat_label, color='r')

   fname = "ReadLatency."+dbname+".png"
   plt.savefig(fname)
###################################################
# Endof Plot Latency
###################################################


if __name__ == "__main__":
   main(sys.argv[1:])


