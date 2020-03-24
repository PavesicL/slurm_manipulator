#!/usr/bin/env python3
"""
Sends all jobs with status Vanished to the cluster.
"""

import os
import sys
import re
from help_functions import nameToParamsVals, readNameFile_batchParams, writeBatchScript


def editInputFile(params, vals):
	"""
	Rewrites the input file inputFile.txt so that the three parameters are set and everything else is the same. 
	This function is specific for the DMRG inputFiles!
	"""

	#DMRG SPECIFIC!!!
	Delta=0.026
	for i in range(len(params)):
		if params[i] == "Ec":
			vals[i] *= Delta


	with open("SAMPLEinputFile.txt", "r") as originalF:
		with open("inputFile.txt", "w+") as newF:
			for line in originalF:
				written=0	#if the line was already written to the new file

				for i in range(len(params)):	#iterate over all params - check if one of them matches the line, then overwrite it
					param = params[i]
					val = vals[i]

					if re.search("\s+"+param+"\s*=", line):
						newF.write("	"+param+" = {0}\n".format(val))
						written=True

				if not written:
					newF.write(line)
	return None				

#####################################################################################################################
os.system("1_slurm_update_jobs.py")

#READ jobsToSend.txt TO A LIST TO A LIST
f = open("vanishedJobs.txt", "r")
jobsToSend = [line.rstrip('\n') for line in f]	#strip the newline characters

count=0
#ITERATE OVER ALL JOBSTOSEND
for i in range(len(jobsToSend)):
	jobname = jobsToSend[i]

	#make a new folder
	os.mkdir("results/{0}".format(jobname))

	#save the input file and move it to the corresponding folder
	params, vals = nameToParamsVals(jobname, nameFile="nameFile")
	editInputFile(params, vals)
	os.system("mv inputFile.txt results/{0}/".format(jobname))

	#write the batch script
	paramsDict, where = readNameFile_batchParams("nameFile")

	writeBatchScript(paramsDict, jobname, where)

	#sbatch to send job
	os.system("sbatch sendJob")

	count+=1

if count>0:
	print("Sent {0} jobs.".format(count))
else:
	print("No jobs to send.")