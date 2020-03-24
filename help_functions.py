#!/usr/bin/env python3

"""
Functions used within the SLURM_submission scripts.
"""

import os
import sys
import re

def readNameFile(file, regex=False):
	"""
	Reads the nameFile and returns a jobname and a list of parameters and their types.
	If regex = true, instead of a python formatted string, return the name as a regex expression string.  
	INPUT:
	file - relative path to the file with the information about jobname and parameters.
	regex - wheter to return the name as a regex expression string
	OUTPUT:
	name/regexname - a jobname, a python formatted string or a regex type string
	paramsList - a list of all parameters and their types, paramsList[i] = [param, paramtype]
	"""

	paramsCheck = False
	paramsList = []

	with open(file, "r") as f:

		for line in f:

			a = re.search("name\s*=\s*(.*)", line)	
		
			b = re.search("params\s*{", line) 
			c = re.search("}\s*endparams", line) 
			
			d = re.search("\s*(\w*)\s*(\w*)", line)
			
			if line[0] == "#":	#this line is a comment
				pass
			if a:	#this line has the name, save it
				name = a.group(1)
			if b:	#we are in the part of the file with the params info
				paramsCheck=True
				continue
			if c:	#we are past the part of the file with the params info
				paramsCheck=False

			if paramsCheck and d:	#parse parameters
				param, paramtype = d.group(1), d.group(2)
				paramsList.append([param, paramtype])

	if regex:
		regexname = re.sub("{[0-9]+}", "(-*[0-9]+\.*[0-9]*)", name)	#replace all instances of {number} in the name with ([0-9]+.*[0-9]*), which matches floats and ints
		return regexname, paramsList
	
	else:
		return name, paramsList


def nameToParamsVals(jobname, nameFile="nameFile"):
	"""
	Given a job name, return a list of parameters and a list of their values.
	INPUT:
	jobname - the name of the job
	nameFile - relative path to the file with the information about jobname and parameters.
	OUTPUT:
	params - a list of parameters
	vals - a list of their values, in the same order
	"""

	regexname, paramsList = readNameFile(nameFile, regex=True)
	
	params, vals = [], []
	
	a = re.search(regexname, jobname)	#match the regexname with the jobname
	for i in range(len(paramsList)):

		param = paramsList[i][0]
		val = float(a.group(i+1))

		params.append(param)
		vals.append(val)		

	return params, vals


def readNameFile_batchParams(file):
	"""
	Read batch parameters from the nameFile. Also reads NUM_OMP_THREADS.
	"""
	
	batchparamsCheck = False
	dictparams = {}
	with open(file, "r") as f:
		for line in f:

			if line[0] == "#":	#this line is a comment
				pass
			
			aa = re.search("where = (.*)", line)

			a = re.search("batch{", line)
			b = re.search("}endbatch", line)


			d = re.search("time (.*)", line)
			e = re.search("cpus-per-task (.*)", line)
			
			f = re.search("OMP_NUM_THREADS (.*)", line)
			g = re.search("path (.*)", line)
			
			#g = re.search("", line)	add new parameters here
			if aa:
				where = aa.group(1)

			if a:
				batchparamsCheck = True
			if b:
				batchparamsCheck = False

			if batchparamsCheck and d:
				time = d.group(1)
				dictparams["time"] = time

			if batchparamsCheck and e:
				cpusPerTask = e.group(1)
				dictparams["cpus-per-task"] = cpusPerTask

			if batchparamsCheck and f:
				ompThreads = f.group(1)
				dictparams["OMP_NUM_THREADS"] = ompThreads	
	
			if batchparamsCheck and g:
				path = g.group(1)
				dictparams["path"] = path	

	return dictparams, where		


def writeBatchScript(paramsDict, jobname, where):
	"""
	Reads the parameters from the dictionary and writes the batch script. 
	The where parameter takes either MAISTER or SPINON, otherwise fails. On MAISTER, the singularity container is used.
	"""

	#write the jobname into the script - this will format all lines in script which have some type of Python formatting string options, eg. {}, {1}, ...
	with open("SAMPLEscript", "r") as Ss:
		with open("results/{0}/script".format(jobname), "w+") as s:
			for line in Ss:
				s.write(line.format(jobname) + "\n")

	os.system("chmod +x results/{0}/script".format(jobname))			

	with open("sendJob", "w") as job:

		job.writelines('#!/bin/bash\n')
		job.writelines('#SBATCH --mem-per-cpu=4000\n')
		job.writelines('#SBATCH --job-name={0}\n'.format(jobname))


		if "time" in paramsDict:
			job.writelines('#SBATCH --time={0}\n'.format(paramsDict["time"]))
		else:
			job.writelines('#SBATCH --time=47:00:00\n')

		if "cpus-per-task" in paramsDict:
			job.writelines('#SBATCH --cpus-per-task={0}\n'.format(paramsDict["cpus-per-task"]))		
		else:	
			job.writelines('#SBATCH --cpus-per-task=1\n')
		

		if where == "MAISTER":
			if "path" in paramsDict and "OMP_NUM_THREADS" in paramsDict:
				job.writelines("SINGULARITYENV_OMP_NUM_THREADS={0} SINGULARITYENV_PREPEND_PATH={1} singularity exec /ceph/sys/singularity/gimkl-2018b.simg {2}\n"
																												.format(paramsDict["OMP_NUM_THREADS"], paramsDict["path"], script))	
			elif "path" in paramsDict:
				job.writelines("SINGULARITYENV_PREPEND_PATH={0} singularity exec /ceph/sys/singularity/gimkl-2018b.simg {1}\n".format(paramsDict["path"], script))	
			elif "OMP_NUM_THREADS" in paramsDict:
				job.writelines("SINGULARITYENV_OMP_NUM_THREADS={0} singularity exec /ceph/sys/singularity/gimkl-2018b.simg {1}\n".format(paramsDict["OMP_NUM_THREADS"], script))				
							
			else:
				job.writelines("singularity exec /ceph/sys/singularity/gimkl-2018b.simg {0}\n".format(script))				
		
		elif where == "SPINON":
			if "path" in paramsDict:
				job.writelines("export PATH={0}:$PATH\n".format(paramsDict["path"]))
			if "OMP_NUM_THREADS" in paramsDict:
				job.writelines("export OMP_NUM_THREADS={0}\n".format(paramsDict["OMP_NUM_THREADS"]))	

			job.writelines("touch results/{0}/START\n".format(jobname))	
			job.writelines("results/{0}/script\n".format(jobname))	
			job.writelines("touch results/{0}/DONE\n".format(jobname))

		else:
			print("SPECIFY WHERE!")
			exit()		

	return None