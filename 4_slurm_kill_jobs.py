#!/usr/bin/env python3
"""
Kill all jobs of the given batch with a given status.
"""

import os
import sys
import re

if len(sys.argv) != 2:
	print("Usage: " + sys.argv[0] + " status")
	print("Status can be: q (queing), r (running), a (all).")
	exit()


#REFRESH THE job status files again
print("Updating job statuses..")
os.system("1_update_jobs.py")
print()

killRunning, killQueueing = False, False
if sys.argv[1] == "q" or sys.argv[1] == "a":
	killQueueing = True
 
if sys.argv[1] == "r" or sys.argv[1] == "a":
	killRunning = True

countR, countQ = 0, 0
count=0
	
if killRunning:
	with open("runningJobs.txt", "r") as runF:
		for name in runF:
			count+=1
			print("{0}	{1}".format(count, name))
			os.system("scancel -n {0}".format(name))
	
			countR+=1

if killQueueing:
	with open("queingJobs.txt", "r") as runF:
		for name in runF:
			count+=1
			print("{0}	{1}".format(count, name))
			os.system("scancel -n {0}".format(name))
	
			countQ+=1

print("Attempted to kill {0} jobs; {1} running and {2} queing.".format(countQ+countR, countR, countQ))
