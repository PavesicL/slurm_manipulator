#!/usr/bin/env python3
"""
Sends all jobs with status Vanished to the cluster.
"""

import os
import sys
import re
from help_functions import nameToParamsVals, readNameFile_batchParams, writeBatchScript
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="name of the input file", default="inputFile")
parser.add_argument("-Si", help="name of the SAMPLE input file", default="SAMPLEinputFile")

args = parser.parse_args()

inputFile = args.i
SAMPLEinputFile = args.Si

def editInputFile(params, vals, inputFile, SAMPLEinputFile):
	"""
	Rewrites the input file inputFile.txt so that the three parameters are set and everything else is the same. 
	This function is specific for the DMRG inputFiles!
	"""

	#####################################
	#DMRG SPECIFIC!!!					#
	Delta=0.026							#
	for i in range(len(params)):		#
		if params[i] == "Ec":			#
			vals[i] *= Delta			#
	#####################################		

	with open(SAMPLEinputFile, "r") as originalF:
		with open(inputFile, "w+") as newF:
			for line in originalF:
				written=0	#if the line was already written to the new file

				for i in range(len(params)):	#iterate over all params - check if one of them matches the line, then overwrite it
					param = params[i]
					val = vals[i]

					if re.match("\s*"+param+"\s*=", line):
						#newF.write("	"+param+" = {0}\n".format(val))
						newF.write(param+" = {0}\n".format(val))
						written=True

				if not written:
					newF.write(line)
	return None				

#####################################################################################################################
os.system("1_slurm_update_jobs.py")

#READ jobsToSend.txt TO A LIST TO A LIST
f = open("failedJobs.txt", "r")
jobsToSend = [line.rstrip('\n') for line in f]	#strip the newline characters

count=0
#ITERATE OVER ALL JOBSTOSEND
for i in range(len(jobsToSend)):
	jobname = jobsToSend[i]

	#check if the folder exists
	if os.path.exists("results/{0}".format(jobname)):
		#if it exists, the job has failed, remove it:
		os.system("rm -rf results/{0}/".format(jobname))	

	#make an empty folder
	os.mkdir("results/{0}".format(jobname))

	#save the input file and move it to the corresponding folder
	params, vals = nameToParamsVals(jobname, nameFile="nameFile")
	#make an inputFile and move it to the job folder
	editInputFile(params, vals, inputFile, SAMPLEinputFile)
	os.system("mv {0} results/{1}/".format(inputFile, jobname))

	paramsDict, where = readNameFile_batchParams("nameFile")
	#write the batch script
	writeBatchScript(paramsDict, jobname, where)

	#change the current directory to the job folder
	os.chdir("results/{0}".format(jobname))
	#sbatch to send job	
	os.system("sbatch sendJob".format(jobname))

	#change the current directory back
	os.chdir("../..") 


	count+=1


if count>0:
	print("Sent {0} jobs.".format(count))
else:
	print("No jobs to send.")
