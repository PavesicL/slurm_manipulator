#!/usr/bin/env python3
"""
Counts the finished jobs - those that have an empty file called DONE in the folder - and appends their names to a file.
"""

import os
import sys
import re
from help_functions import readNameFile, readNameFile_batchParams

################################
_, where = readNameFile_batchParams("nameFile")

if where == "MAISTER":
	username = "lukap"
elif where == "SPINON":
	username = "pavesic"
else: 
	print("Specify where!")
	exit()
################################

#get a regex general form of the name
regexName, _ = readNameFile("nameFile", regex=True)

#READ THE FILE WITH ALL REQUESTED JOBS TO A LIST
f = open("jobsToSend.txt", "r")
jobsToSend = [line.rstrip('\n') for line in f]	#strip the newline characters


#PARSE THE QUEUE
os.system('squeue -u {0} -o "%.100j" -h > statJobs.txt'.format(username))
f = open("statJobs.txt", "r")
queue = [line.rstrip('\n').strip() for line in f]	#strip the newline characters and whitespace

#GET FINISHED JOBS:
done, start = [], []
#RUN OVER ALL SUBFOLDERS
#for all folders, if the job has already created DONE, put the jobname in list done, else if it has created the START file, put it into start
all_in_folder = os.listdir("results")
for folder in all_in_folder:
	if os.path.isdir("results/"+folder):
		#list everything in folder
		allFiles = os.listdir("results/"+folder)
		if "DONE" in allFiles:
			#this job is finished
			done.append(folder)	
		elif "START" in allFiles:
			#this job is running
			start.append(folder)	
		

#COUNT THE JOBS
queingJobs, runningJobs, finishedJobs, failedJobs = [], [], [], []
for i in range(len(jobsToSend)):
	job = jobsToSend[i]
	
	#if jobname is found in queue, it is either queing or running
	if job in queue:
		if job in start:
			runningJobs.append(job)
		else:
			queingJobs.append(job)

	#if jobname is not foud in queue, it is either finished or failed
	else:
		if job in done:
			finishedJobs.append(job)
		else:
			failedJobs.append(job)	


#WRITE THE NAMES OF THE FINISHED JOBS TO FILE
with open("finishedJobs.txt", "w") as ff:
	ff.writelines([i+"\n" for i in finishedJobs])

#WRITE THE NAMES OF THE VANISHED JOBS TO FILE
with open("failedJobs.txt", "w") as ff:
	ff.writelines([i+"\n" for i in failedJobs])

#WRITE THE NAMES OF THE RUNNING JOBS TO FILE
with open("runningJobs.txt", "w") as ff:
	ff.writelines([i+"\n" for i in runningJobs])

print("There is {0} jobs queueing, {1} running, {2} finished and {3} failed jobs.".format(len(queingJobs), len(runningJobs), len(finishedJobs), len(failedJobs)))
