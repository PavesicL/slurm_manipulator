#!/usr/bin/env python3
"""
Given a general job name and a list of parameters from nameFile, takes parameter values as an input and appends all requested job names to jobsToSend.txt.
"""

import sys
import re
from help_functions import readNameFile
import itertools

# THIS IS ALL PARSING THE INPUT AND PRINTING/CHECKING IF EVERYTHING IS OK ###########################################################################

name, paramList = readNameFile("nameFile")

print(name)
print(paramList)

#The required input is at least three values for the sweep parameters (min, max, step) and at least one value for the case parameters.
smallestInputLen = 1 #start at 1 as len(sys.argv) is always at least 1 (sys.argv[0] is the name of the script)
outputString = " "
for i in paramList:
	outputString += i[0]+" "
		
	if i[1] == "case":
		smallestInputLen+=1
		outputString += i[0]+"s "

	if i[1] == "sweep":
		smallestInputLen+=3
		outputString += i[0]+"_min " + i[0]+"_max " + i[0]+"_step "

if len(sys.argv) < smallestInputLen:
	print("Usage: " + str(sys.argv[0]) + outputString)
	exit()


#PARSE INPUT
#Iterate over the input, if the input matches the name of the j-th parameter, append all the following numbers casesList[j].
casesList = [[] for i in range(len(paramList))]
for i in range(1, len(sys.argv)):
	skip=False	

	for j in range(len(paramList)):
		
		if sys.argv[i] == paramList[j][0]:
			whichParam = j
			skip = True	#when we find a parameter name, skip this instance of i
	
	if not skip:	#if we have not found a parameter name at this i, append the number to the corresponding list in casesList
		casesList[whichParam].append(float(sys.argv[i]))	

#Now, casesList[j] holds all numbers associated to the parameter paramList[j][0].

#CHECK IF OK
for i in range(len(paramList)):
	if len(casesList[i])==0:
		print("The parameter {0} was given no values!".format(paramList[i][0]))
		exit()

	if paramList[i][1]=="sweep" and len(casesList[i])!=3:
		print("The parameter {0} is type sweep but did not get 3 values!".format(paramList[i][0]))
		exit()


#REWRITE ALL PARAMETERS TO BE CASE-TYPE - write out all cases
for i in range(len(paramList)):
	if paramList[i][1]=="sweep":
		start, stop, step = casesList[i]
		casesList[i] = []
		
		x=start
		while round(x, 8)<stop:
			casesList[i].append(x)
			x+=step

		casesList[i] = [round(k, 8) for k in casesList[i]]

#PRINT WHAT WE ARE DOING
print("The sweep is over parameters: ")
for i in range(len(paramList)):

	param = paramList[i][0]
	paramType = paramList[i][1]
	
	casesString = ""
	for j in range(len(casesList[i])):
		casesString+="{0} ".format(casesList[i][j])

	print(param + ": "+casesString[:-1]) #[:-1] just to take away the last space
 

# GENERATE ALL JOB NAMES AND SAVE THEM TO A FILE ####################################################################################################

allCases = list(itertools.product(*casesList))
count=0
with open("jobsToSend.txt", "a+") as newF:

	for i in allCases:		
		jobname = name.format(*[i[j] for j in range(len(paramList))])
		newF.write(jobname+"\n")
		count+=1

print("{0} jobs added to jobsToSend.txt.".format(count))