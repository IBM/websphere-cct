##########################################################################################
# 
# Copyright International Business Machines Corp. 2014, 2020.
# 
# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership. Licensed under the Apache License,
# Version 2.0 (the "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
##########################################################################################
# Author: Dennis Riddlemoser
# This script has library functions for ConfigDump.py and ConfigUtils.py
##########################################################################################
# Change history:
# Date        Ref  Who  Comments
# 2018/01/17  0001 DWR  Added logic to handle unsupported configuration types.
# 2018/05/18  0004 DWR  Added functions in support of a WebSphere variables report
# 2018/05/26  0005 DWR  Added support for ignoring certain strings in match values.  
# 2018/05/27  0005 DWR  Alow for disabling matching of cell, node and server names.
# 2018/05/28  0007 DWR  Replace all server, node and cell names with .* for matching by default.
# 2018/05/29  0009 DWR  replace characters for display in HTML
# 2018/06/01  0011 DWR  Specify multiple poperties files and properties on command line.
# 2018/06/02  0013 DWR  Implemented comprehensive thread pool report.
# 2018/06/02  0014 DWR  Removed thread hack in acquiring a coonfig dump.
# 2018/08/02  0016 DWR  Accontiung for variables that do not have name and scope attributes.
# 2018/11/13  0021 DWR  Implemented Application reports
# 2018/11/20  0022 DWR  Implemented outputing of sample wsadmin scripts to correct configurtion differences.
# 2019/01/08  0023 DWR  Restructuring code.  Moving report output functions to ConfigUtils.py
# 2019/01/15  0024 DWR  Adding logic to skip configuration files during properties processing
# 2019/01/29  0025 DWR  Implementing built-in clusters report
# 2019/01/30  0026 DWR  Using AdminConfig.types() to get configuration elements instead of hard coded list
# 2019/01/30  0027 DWR  Adding logic to generate file system reports
# 2019/03/22  0028 DWR  Hard coded a delimiter for CellSuffix for Trust Association Interceptor report
# 2019/04/24  0029 DWR  Hard coded a delimiter for CellSuffix for Trust Association Interceptor report
# 2019/05/25  0030 DWR  Makeing date/time stapms a conditional match in file system comparisons 
# 2019/05/26  0031 DWR  Report key for file system reports
# 2019/06/05  0032 DWR  Disable errors messages when getting #Key_ configuration types as current parsing has issues.  BUGBUG
# 2019/06/06  0033 DWR  Minor updates to file system report format
# 2019/08/07  0035 DWR  Adding AIX support for file comparisons
# 2019/08/19  0037 DWR  Adding command line setting of CellSuffix
# 2019/08/19  0038 DWR  Limiting data gathered to specificed scope(s)
# 2019/09/25  0039 DWR  Adding debug messages to writeRepositoryFile
# 2020/08/30  0042 DWR  Default ConfigurationDumpFiles to *.cfg
#

import WAuJ_utilities as WAuJ
import sys
import time
import re
import glob
import os
import threading
import traceback
#Ref0027 the tarfile module is not needed for ConfigDump.py and will fail to load if jython is in use
try:                #Ref0027
	import tarfile  #Ref0027
except:             #Ref0027
	None            #Ref0027

True=1
False=0
Debug=False

RepositoryFile=''

MasterDict = {}
PropertiesDict = {}
OriginalCellNameList = [] #Ref0005
CellSuffixList = []
CellSuffix = ''  #Ref0037

#lists all configuration elements that are effectively collections of name/value pairs
PropertyAttributes=['properties','customProperties','systemProperties','environment']

#########################################################################################################
#prints a message to stdout.  There are two levels of messages, standard and debug.
#the latter are only printed if Debug is set to true
#########################################################################################################
def printMsg(msg,dbg):
	global Debug
	if Debug or not dbg:
		print time.strftime('[%y/%m/%d %H:%M:%S] ') + str(msg)

#Ref0002 Begin: Added to improve exception reporting 
#########################################################################################################
#prints a message to stdout.  There are two levels of messages, standard and debug.
#the latter are only printed if Debug is set to true
#########################################################################################################
def printException(msg,exceptionInfo):
	global Debug
	(type,emsg,etb) = exceptionInfo
	printMsg('ERROR: %s (%s)' % (msg,emsg),False)
	printMsg('\tException %s' % type,True)
	if Debug:
		printMsg('\tStack:',True)
		lines = traceback.extract_stack()[:-2] + traceback.extract_tb(etb)
		for line in lines:
			(fileName, lineNumber, functionName, codeLine) = line
			print '  File "%s", line %i, in %s ' % (fileName, lineNumber, functionName)
			print '    %s' % codeLine
#Ref0002 End


#########################################################################################################
# Strips off the end characters of a string.
#
# str = String to strip end characters from
#
# return new string minus end characters
#########################################################################################################
def stripEndChars(str):
	return str[1:-1]

#########################################################################################################
# Converts a string into a list of items
#
# str = String to strip end characters from
#
# return new string minus end characters
#########################################################################################################
def stringListAsList(strList):
	strList=stripEndChars(strList).strip()
	rtnVal = []
	if len(strList) > 0:
		rtnVal = strList.split(' ')
	return rtnVal

#Ref0021 Begin
#########################################################################################################
# Converts a string into a list of items using WAuJ_utilities
#
# str = String to strip end characters from
#
# return new string minus end characters
#########################################################################################################
def stringListAsList1(strList):
	return WAuJ.stringListAsList(strList)
#Ref0021 End

#########################################################################################################
# Returns True if the string represents a configuration ID
#
# cfg = String which may or may not be a configuration element ID
#
# return true is cfg is a configuration element ID
#BUGBUG should use regular expressions, needs to be rewritten
#########################################################################################################
def isConfigID(cfg):
	printMsg('isConfigID => '+cfg, True)
	rtnVal = False
	try:
		rtnVal = cfg.find('(') > -1 and cfg.find('#') > -1 and cfg.find('|') > -1 and cfg.find(')') > -1
	except:
		'Do Nothing'
	printMsg('isConfigID <= '+str(rtnVal), True)
	return rtnVal

#########################################################################################################
# Returns true if element is equal to the value that is most common in the list. 
#
# element = value to check in the list
# list = arbitrary list of values
#
# return true is cfg is a configuration element ID
#########################################################################################################
def isMostCommon(element,list):
	count=0
	for x in list:
		if element == x:
			count=count+1
	rtnVal = True
	for x in list:
		i=0
		for y in list:
			if x==y:
				i=i+1
		if count < i:
			rtnVal = False
	return rtnVal

#Ref0001 Begin
#########################################################################################################
# Uses AdminConfig to iterate through a list of top level configuration elements to retrieve
#########################################################################################################
def getConfigElements(configElements,AdminConfig,regexList):
# Ref0014 Removed as it does not serve a purpose and slows down the config dump.
# The following is a hack as a com.ibm.websphere.management.exception.InvalidConfigDataTypeException cannot be caught
#	for configElement in configElements:
#		t = threading.Thread(name=configElement,target=getConfigElements2, args=(configElement,AdminConfig,))
#		printMsg('Getting all elements of type ' + configElement[1],False)
#		t.start()
#		while t.isAlive():
#			time.sleep(1)

	for configElement in configElements:
		try:
			elements = AdminConfig.list(configElement).splitlines()                      #Ref0026
			filteredElements = elements                                                      #Ref0038
			if len(regexList) > 0:                                                           #Ref0038
				filteredElements = []                                                        #Ref0038
				for element in elements:                                                     #Ref0038
					for regex in regexList:                                                  #Ref0038
						if re.match(regex,element):                                          #Ref0038
							filteredElements.append(element)                                 #Ref0038
							break                                                            #Ref0038
			printMsg('Reading %i %s elements out of %i found' % (len(filteredElements),configElement,len(elements)),False) #Ref0038	
			for element in filteredElements:
				#printMsg(configElement[0] + element,False)                      #Ref0026
				getConfigAsDict(element,AdminConfig)
		except:
			printMsg('ERROR: ' + configElement + ' cannot be read.',False)
			for msg in sys.exc_info():
				printMsg(msg,False)

#def getConfigElements2(configElement,AdminConfig):
#	elements = AdminConfig.list(configElement[1]).splitlines()
#	printMsg('Found ' + str(len(elements)) + ' ' + configElement[1],False)
#	for element in elements:
#		printMsg(configElement[0] + element,False)
#		getConfigAsDict(element,AdminConfig)
#Ref0001 End
	

#########################################################################################################
# Uses AdminConfig to get the attributes of the given configuration object then makes a Dictionary object 
# from the information.  Recursively gathers all referenced configuration IDs using the same algorithm.
#
# return the resulting dictionary
#########################################################################################################
def getConfigAsDict(cfg,AdminConfig):
	global MasterDict
	cDict = {}
	if not MasterDict.has_key(cfg):
		try:
			printMsg('Getting ' + cfg,True)
			attrs=AdminConfig.show(cfg)
			if attrs == None:
				attrs = []
			else:
				attrs = attrs.splitlines()
			printMsg(attrs,True)
			for attr in attrs:
				attr = stripEndChars(attr)
				idx=attr.find(' ')
				key=attr[:idx]
				value=attr[idx+1:]
				cDict.update({key:value})
			MasterDict.update({cfg:cDict})
			keys=cDict.keys()
			for key in keys:
				try:
						printMsg('key == '+key+' value == '+cDict[key],True)
						if isConfigID(cDict[key]):
							if cDict[key].find('[') == 0:
								cfgIDList = WAuJ.stringListAsList(cDict[key])
								printMsg('cfgIDList-->'+str(cfgIDList),True)
								while len(cfgIDList)>0:
									getConfigAsDict(cfgIDList.pop(),AdminConfig)
							else:
								getConfigAsDict(cDict[key],AdminConfig)
				except:
					printMsg("ERROR: Getting child configurations for ID: " + cfg,False)
					for msgLine in sys.exc_info():
						printMsg('\t'+str(msgLine),False)
		except:
			if not cfg.find(',') == -1 and not cfg.find('#Key_') == -1:
				printMsg("ERROR: Getting configurations for ID: " + cfg,False)
				for msgLine in sys.exc_info():
					printMsg('\t'+str(msgLine),False)
	else:
		printMsg("Master Dictionary contains " + cfg,True)
		cDict=MasterDict[cfg]
	debug=False
	return cDict

#########################################################################################################
# Ref0011  This function was significantly modified to support multiple properties files and individual 
#          properties.
# Read properties from files and/or command line.  Files aree similar to a Java properties file but not 
# nearly as robust.  Key/value # from the properties file are stored as key/value pairs in the 
# PropertiesDict dictionary.  An '=' in the parameter indicates an individual property value in the form 
# of propName=propValue
# Example:
#    Properties File:
#        key=value
#    PropertiesDict:
#        PropertiesDict[key]=value
#########################################################################################################
def readProperties(propertiesList,scriptPath):
	global PropertiesDict
	if not scriptPath == None:
		propertiesList.append('%sConfigReportAttributes.properties' % scriptPath)
	for propInput in propertiesList:
		if propInput.find('=') > 0:
			idx = propInput.find('=')
			propName=propInput[:idx]
			propValue=propInput[idx+1:]
			printMsg('Setting property %s to %s' % (propName,propValue),False)
			PropertiesDict[propName] = propValue
		else:
			#Begin Ref0024
			if propInput.find('.tar.gz') > -1:
				printMsg('ERROR: File %s is a configuration dump file.' % propInput,False)
				printMsg('\tThis file should be referenced in the ConfigurationTarFiles property.',False)
				sys.exit(1)
			#End Ref0024
			printMsg('Reading properties from %s' % propInput,False)
			f = open(propInput,'r')
			lines = f.readlines()
			f.close()
			key='NOT_INITIALIZED'
			append=False
			for line in lines:
				#Begin Ref0024
				if line.find('CellSuffix') == 0:
					printMsg('ERROR: File %s is a configuration dump file.' % propInput,False)
					printMsg('\tThis file should be referenced in the ConfigurationReportOutputPath property.',False)
					sys.exit(1)
				#End Ref0024
				line=line.strip()
				if len(line) > 0 and not line[0] == '#':
					if append:
						if line[len(line)-1]=='\\':
							append=True
							line=line[:-1].strip()
						else:
							append=False
						PropertiesDict[key]=PropertiesDict[key]+line
					if line.find('#') == 0:
						continue
					elif line.find('=') > 0:
						idx=line.find('=')
						key=line[:idx].strip()
						value=line[idx+1:].strip()
						if len(value) > 0 and value[len(value)-1]=='\\':
							append=True
							value=value[:-1].strip()
						PropertiesDict[key]=value
					elif len(line.strip()) == 0:
						printMsg('Invalid line: '+line,False)
	printMsg('readProperties => %s' % str(PropertiesDict),True)
	
#########################################################################################################
# Stores the repository file name or directory input from the command line
#########################################################################################################
def setRepositoryConfigFileName(name):
	global RepositoryFile
	RepositoryFile=name

#########################################################################################################
# Sets CellSuffix to override default time stamp
#########################################################################################################
def setCellSuffix(suffix):
	global CellSuffix
	CellSuffix=suffix

#########################################################################################################
# Writes the cell configuration out to a file.  The format is config IDs are not indented.  Attributes
# associated with coinfig IDs follw the config ID and are indented with a tab.
# Example:
# ConfigID1
# \tAttribute1=value
# \tAttribute2=value
# ConfigID2
# \tAttribute1=value
# \tAttribute2=value
# \tAttribute3=value
#########################################################################################################
def writeRepositoryFile():
	global MasterDict
	global RepositoryFile
	global CellSuffix   #Ref0037
	timeStamp=time.strftime('%y%m%d%H%M%S') #Ref0028
	defaultFile='ConfigDump'+time.strftime('-%y-%m-%d-%H-%M-%S')+'.cfg'
	try:
		#Try to get the cell name WAS property
		defaultFile=getCellNames(MasterDict)[0]+time.strftime('-%y-%m-%d-%H-%M-%S')+'.cfg'
	except:
		try:
			defaultFile=getConfigIDCell(MasterDict.keys()[0])+time.strftime('-%y-%m-%d-%H-%M-%S')+'.cfg'
		except:
			None
	if RepositoryFile=='':
		RepositoryFile=defaultFile
	elif os.path.exists(RepositoryFile):
		if os.path.isdir(RepositoryFile):
			RepositoryFile = RepositoryFile + os.sep + defaultFile
		elif os.path.isfile(RepositoryFile):
			printMsg('File '+RepositoryFile+' exists, cannot write output file.',False)
			sys.exit(2)
	printMsg('Writing repository config file to '+RepositoryFile,False)
	try:
		f = open(RepositoryFile,'w')
		#Begin Ref0037
		if CellSuffix=='':
			f.write('CellSuffix='+timeStamp+'\n')
		else:
			f.write('CellSuffix='+CellSuffix+'\n')
		#End Ref0037
		mkeys = MasterDict.keys()
		while len(mkeys)>0:
			mkey = mkeys.pop()
			f.write(mkey+'\n')
			printMsg('Key ' + mkey + '\n' + str(MasterDict[mkey]),True)
			keys = MasterDict[mkey].keys()
			while len(keys)>0:
				key = keys.pop()
				f.write('\t'+key+'='+MasterDict[mkey][key]+'\n')
		f.close()
	except:
		printException('Exception in writeRepositoryFile',sys.exc_info())
		

#########################################################################################################
# Adds a cell suffix onto all configuration IDs, otherwise, just trims
#########################################################################################################
#Ref0028 Function significantly rewritten
def addCellSuffix(value,cellSuffix):
	if value.find('\r') == len(value) - 1:  #Ref0029
		value = value[:-1]                  #Ref0029
	if value.find('\n') == len(value) - 1:  #Ref0029
		value = value[:-1]                  #Ref0029
	idx = 0
	replacementList = ['cells/','waspolicies/'] 
	if isConfigID(value):
		for repVal in replacementList:         
			while value.find(repVal,idx) > -1:
				idx=value.find(repVal,idx) + len(repVal)
				idx1=value.find('/',idx)
				idx2=value.find('|',idx)
				if idx1>-1 and idx1<idx2:
					idx=idx1
				else:
					idx=idx2
				value=value[0:idx]+'-'+cellSuffix+value[idx:] 
	return value

#########################################################################################################
# Reads the cell config from a file per the format defined in writeConfig()
#########################################################################################################
def readConfigs():
	global MasterDict
	global PropertiesDict
	global OriginalCellNameList
	global CellSuffixList								#Ref0022
	fileNames=[]
	try:
		for fileSpec in PropertiesDict['ConfigurationDumpFiles'].split(','): #Ref0042
			for fileName in glob.glob(fileSpec.strip()):
				fileNames.append(fileName)
	except:
		fileNames=glob.glob('*.cfg')
	if len(fileNames) == 0:
		printMsg('ERROR: No configuration files found',False)
		sys.exit(1)
	for fileName in fileNames:
		fileName =  str(fileName)
		printMsg('Reading repository config from ' + fileName,False)
		f = open(fileName,'r')
		lines = f.readlines()
		f.close()
		currentKey='NOT_INITILIZED'
		currentDict={}
		debug = False
		cellSuffix=''
		lineNumber = 0
		for line in lines:
			lineNumber = lineNumber + 1
			if line.find('CellSuffix') == 0:
				idx=line.find('=')
				cellSuffix=line[idx+1:-1].strip()
				CellSuffixList.append(cellSuffix)		#Ref0022
			elif line.find('\t')==0:
				idx=line.find('=')
				key=line[1:idx]
				value=line[idx+1:-1]
				currentDict[key]=addCellSuffix(value,cellSuffix)
			else:
				#Begin Ref0007
				idx1 = line.find('(cells/') 
				if idx1 > -1 :
					idx1 = idx1 + len('(cells/')
					idx2 = line.find('/',idx1)
					if idx2 > -1:
						originalCellName=line[idx1:idx2]
						if OriginalCellNameList.count(originalCellName) == 0:
							OriginalCellNameList.append(originalCellName)
				#End Ref0007
				if not currentKey=='NOT_INITILIZED':
					MasterDict[currentKey]=currentDict
				currentKey=line[:-1]
				if not isConfigID(currentKey) and not currentKey == '(null)':
					printMsg('WARNING: File %s may be corrupted at line %i.  Invalid value "%s" found.' % (fileName,lineNumber,currentKey), False)
					currentKey='ERROR-%i-%s' % (lineNumber,fileName)
				currentKey=addCellSuffix(currentKey,cellSuffix)
				currentDict={'CONFIG_ID':currentKey}  #Ref0022
		MasterDict[currentKey]=currentDict
	#BUGBUG detect for cell name collision
	MasterDict['CellList'] = getCellNames(MasterDict);

#########################################################################################################
# cluster = cluster configuration ID
#
# return the config IDs for all cluster members in a cluster
#########################################################################################################
def getClusterServerList(cluster):
	printMsg('getClusterServerList => '+cluster, True)
	members = WAuJ.stringListAsList(MasterDict[cluster]['members'])
	serverConfigIDs = []
	serverExcludeList=''
	try:
		PropertiesDict['ServerExcludeList'].split(',')
	except:
		None
	servers=findConfigIDs('.*\#Server_.*',True,MasterDict)
	for member in members:
		for server in servers:
			if not MasterDict[member]['memberName'] in serverExcludeList and \
				MasterDict[member]['memberName'] == MasterDict[server]['name'] and \
				getConfigIDCell(cluster)==getConfigIDCell(server):
				serverConfigIDs.append(server)
	printMsg('getClusterServerList <= '+str(serverConfigIDs), True)
	return serverConfigIDs

#Ref0007 Begin
#########################################################################################################
# returns a list of all server, node and cell names
#########################################################################################################
def getSrvNodeCellNames():
	global OriginalCellNameList
	rtnVal = OriginalCellNameList
	scopes = ['/nodes','/servers']
	keys = MasterDict.keys()
	for key in keys:
		for scope in scopes:
			idx1 = key.find(scope) 
			if idx1 > -1:
				idx1 = idx1 + len(scope) + 1
				idx2a = key.find('/',idx1)
				idx2b = key.find('|',idx1)
				idx2 = 0
				if idx2a == -1:
					idx2 = idx2b 
				else:
					idx2 = idx2a 
				name = key[idx1:idx2]
				if rtnVal.count(name) == 0:
					rtnVal.append(name)
	rtnVal.sort()
	return rtnVal
#Ref0007 End
		
#Ref0005 Begin
#########################################################################################################
# Generates the replacement string list.
#########################################################################################################
ReplacedStringList=None 
def getReplacedStringList():
	global ReplacedStringList
	global PropertiesDict
	if ReplacedStringList == None:
		ReplacedStringList = []
		#Ref0007 Begin
		replaceNames = True
		try:
			if PropertiesDict['DoNotMatchNames'].lower() == 'true':
				replaceNames = False
		except:
			None
		if replaceNames:
			names = getSrvNodeCellNames()
			for name in names:
				ReplacedStringList.append([name,'.*'])
		#Ref0007 End
		keys = getAllPropKeys('ReplaceForMatch:',None) #Ref0025
		for key in keys:
			s = PropertiesDict[key]
			id=key.split(":")[1]
			r = '.*'
			try:
				r = PropertiesDict['ReplaceWith:'+id]
			except:
				None
			ReplacedStringList.append([s,r])
			printMsg('replacedStringList = '+str(ReplacedStringList), True)
	return ReplacedStringList
#Ref0005 End
#########################################################################################################
# Determines if all elements in a list are equal.
#
# returns "Yes" if all elements are equal, otherwise "No"  "N/A" is returned if the list has 0 or 1 elements
#########################################################################################################
def listElementsMatch(matchList):
	printMsg('listElementsMatch => '+str(matchList), True)
	rtnVal = 'Yes'
	replacedStringList = getReplacedStringList() #Ref0005
	if len(matchList) < 2:
		rtnVal = 'N/A'
	else:
		if replacedStringList == None or len(replacedStringList) == 0: #Ref0005
			val=matchList[0]
			for nextVal in matchList:
				if not val == nextVal:
					rtnVal = 'No'
				val = nextVal
#Ref0005 Begin
		else:
			reLst = []
			for s in matchList:
				s = re.escape(s)
				for replacedString in replacedStringList:
					s = s.replace(re.escape(replacedString[0]),replacedString[1])
				reLst.append(s)
			for idx in range (0,len(matchList) - 1):
#				print '%i\t%s\n\t%s\n\t%s\n\t%s' % (idx,matchList[idx],reLst[idx],matchList[idx+1],reLst[idx+1])
				if not (re.match(reLst[idx],matchList[idx+1]) and re.match(reLst[idx+1],matchList[idx])):
					rtnVal = 'No'
					break					
				if rtnVal == 'Yes' and not matchList[idx] == matchList[idx+1]:
					rtnVal = 'Yes*' 
#Ref0005 End
	printMsg('listElementsMatch <= '+str(rtnVal), True)
	return rtnVal

#Begin Ref0030
#########################################################################################################
# Determines if all elements in a list are equal.
#
# returns "Yes" if all elements are equal, otherwise "No"  "N/A" is returned if the list has 0 or 1 elements
#########################################################################################################
def fileListElementsMatch(matchList):  
	printMsg('fileListElementsMatch => '+str(matchList), True)
	rtnVal = 'Yes'
	if len(matchList) < 2:
		rtnVal = 'N/A'
	else:
		regex = 'Date\:[0-9]{4}\-[0-9]{2}\-[0-9]{2}\<br\>Time\:[0-9]{2}\:[0-9]{2}\:[0-9]{2}\.[0-9]{9}'
		sizeCRCList=[]
		dateTimeList=[]
		for s in matchList:
			idx = s.find('<')
			idx = s.find('<',idx+1)
			dateTime = s[:idx-1]
			sizeCRC = s[idx:]
			sizeCRCList.append(sizeCRC)
			dateTimeList.append(dateTime)
		for idx in range (0,len(matchList) - 1):
			if not sizeCRCList[idx] == sizeCRCList[idx+1]:
				rtnVal = 'No'
				break					
			if rtnVal == 'Yes' and not dateTimeList[idx] == dateTimeList[idx+1]:
				rtnVal = 'Yes*' 
	printMsg('fileListElementsMatch <= '+str(rtnVal), True)
	return rtnVal
#End Ref0030

#########################################################################################################
# Finds a matching element in the list
#
# Return the last item in the list which matches the pattern or "NOT_FOUND"
#########################################################################################################
def getMatchingItemFromList(pattern,lst):
	printMsg('getMatchingItemFromList => '+pattern+'  '+str(lst), True)
	rtnVal='NOT_FOUND'
	for val in lst:
		if val.find(pattern) >-1:
			rtnVal=val
	printMsg('getMatchingItemFromList <= '+str(rtnVal), True)
	return rtnVal

#Begin Ref0013
#########################################################################################################
# Returns the config ID from the list based on an attribute value
#########################################################################################################
def getMatchingItemFromListByAttr(list,attrName,attrValue):
	rtnVal = 'NOT_FOUND'
	for element in list:
		try:
			if MasterDict[element][attrName] == attrValue:
				rtnVal = element
				break
		except:
			printException('Exception in getMatchingItemFromListByAttr',sys.exc_info())
	return rtnVal
#End Ref0013

#########################################################################################################
# Navigates through config element references and returns the one specified.
# Example:
#   ['processDefinitions->JavaProcessDef_','execution']
#   This will find the config ID within processDefinitions matching "JavaProcessDef_" then return the
#   dictionary for the config ID in "execution"
#
# pathElements = list of path elements to navigate
#
# returns an empty dictionary if not found, otherwise the config ID dictionary.  
# BUGBUG, needs to be designed to be recursive and evaluate one element at a time
#########################################################################################################
def getConfigFromPath(pathElements):
	printMsg('getConfigFromPath => '+str(pathElements), True)
	absPath=re.compile('.*/__.*__/.*')
	rtnVal = {}
	if len(pathElements) > 1 and type({}) == type(pathElements[1]):
		newPath = pathElements[1]['function'](pathElements[0],pathElements[1]['args'])
		if len(pathElements) > 2:
			newPath=newPath+pathElements[2:]
		rtnVal = getConfigFromPath(newPath)
	elif len (pathElements) == 2 and absPath.match(pathElements[1]):
		configID=pathElements[1].replace('__SERVER__',MasterDict[pathElements[0]]['name'])
		configID=configID.replace('__NODE__',getConfigIDNode(pathElements[0]))
		configID=findConfigIDs(configID,False,MasterDict)
		if len(configID) > 0:
			rtnVal=MasterDict[configID]
	else:
		for pathElement in pathElements:
			idx = pathElement.find('->')
			idx1 = pathElement.find('::') #Ref0013
			try:
				if idx > 0:
					rtnVal = MasterDict[getMatchingItemFromList(pathElement[idx+2:],WAuJ.stringListAsList(rtnVal[pathElement[:idx]]))]
				#Begin Ref0013
				elif idx1 > 0:  
					idx2 = pathElement.find('::',idx1+2)
					listAttr=pathElement[:idx1]
					attrName=pathElement[idx1+2:idx2]
					attrValue=pathElement[idx2+2:]
#					print '%i %i %s %s %s' % (idx1,idx2,listAttr,attrName,attrValue)
					rtnVal = MasterDict[getMatchingItemFromListByAttr(WAuJ.stringListAsList(rtnVal[listAttr]),attrName,attrValue)]
				#End Ref0013
				elif isConfigID(pathElement):
					rtnVal = MasterDict[pathElement]
				else:  #BugBug ??
					rtnVal = MasterDict[rtnVal[pathElement]]
			except KeyError:
				None
			except:
				#printException('Exception in getConfigFromPath',sys.exc_info())
				None
#				printMsg('WARNING: path not found ' + str(pathElements), False)
				rtnVal = {}
	printMsg('getConfigFromPath <= '+str(rtnVal), True)
	return rtnVal

#########################################################################################################
# Returns the scope for sorting column headers
#########################################################################################################
def getScope(configID):
	rtnVal = ''
	scopeStr=configID[configID.find('cells/'):configID.find('|')]
	name=False
	for element in scopeStr.split('/'):
		if name:
			rtnVal = rtnVal + element + ' '
		else:
			rtnVal = rtnVal + element[:-1] + ": "
		name = not name
	return rtnVal

#########################################################################################################
# Returns the name attribute and scope for sorting column headers
#########################################################################################################
def getNameAndScopeSort(configID,nameAttr):  #Ref0015
	return '(' + getScopeSort(configID,None) + ') ' + MasterDict[configID][nameAttr] #Ref0015

#########################################################################################################
# Returns the scope for inclusion in the Summary report
#########################################################################################################
def getScopeSort(configID,ignoreThisParm):  #Ref0015
	rtnVal = ''
	scopeStr=configID[configID.find('cells/'):configID.find('|')]
	for element in scopeStr.split('/'):
		rtnVal = rtnVal + element + ' '
	return rtnVal

#########################################################################################################
# Returns the name attribute and scope for inclusion in the Summary report
#########################################################################################################
def getNameAndScope(configID):
	nameAttrList = ['name','alias']  #Ref0015
	rtnVal = 'NAME_NOT_FOUND'        #Ref0015
	for nameAttr in nameAttrList:    #Ref0015
		if MasterDict[configID].keys().count(nameAttr) > 0: #Ref0015
			rtnVal = MasterDict[configID][nameAttr] + ' (' + getScope(configID) + ')'
	return rtnVal  #Ref0015

#########################################################################################################
# Returns the node of a config ID
#########################################################################################################
def getConfigIDCell(configID):
	printMsg('getConfigIDCell => '+ configID, True)
	rtnVal = 'getConfigIDCell_error_cell_not_found'
	idx = configID.find("cells/")
	if  idx > -1:
		rtnVal = configID[idx+6:]
		if rtnVal.find("/") > -1:
			rtnVal = rtnVal.split("/")[0]
		if rtnVal.find("|") > -1:
			rtnVal = rtnVal.split("|")[0]
	printMsg('getConfigIDCell <= '+rtnVal, True)
	return rtnVal

#Begin Ref0022
#########################################################################################################
# Returns original cell name and the cell suffix
#########################################################################################################
def stripCellSuffix(configID):
	global CellSuffixList
	printMsg('getConfigIDCell => '+ configID, True)
	rtnVal = ('','')
	cellName = getConfigIDCell(configID)
	for suffix in CellSuffixList:
		idx = configID.find(suffix)
		if idx > -1:
			originalConfigID = configID[:idx]+configID[idx+len(suffix):]
			rtnVal = (originalConfigID,suffix)
			break
	return rtnVal
#End Ref0022

#########################################################################################################
# Returns the node of a config ID
#########################################################################################################
def getConfigIDNode(configID):
	printMsg('getConfigIDNode => '+configID, True)
	rtnVal=configID.split('/')[3]
	printMsg('getConfigIDNode <= '+rtnVal, True)
	return rtnVal

#########################################################################################################
# Returns the server of a config ID
#########################################################################################################
def getConfigIDServer(configID):
	printMsg('getConfigIDServer => '+configID, True)
	rtnVal=configID.split('/')[5].split('|')[0]
	printMsg('getConfigIDServer <= '+rtnVal, True)
	return rtnVal

#########################################################################################################
# Returns config IDs based on a regular expression.  
#########################################################################################################
def findConfigIDs(regexStr, all, dict):
	printMsg('findConfigIDs => '+regexStr, True)
	global MasterDict
	if dict == None:
		dict = MasterDict
	keys=dict.keys()
	regex=re.compile(regexStr)
	rtnVal=[]
	for key in keys:
		if regex.match(key):
			rtnVal.append(key)
	if all:
		printMsg('findConfigIDs <= '+str(rtnVal), True)
		return rtnVal
	else:
		if len(rtnVal) > 1:
			None #BugBug
			#printMsg('findConfigIDs WARNING regex "' + regexStr + '" has more than one matching value. ' + str(rtnVal),False)
		elif len(rtnVal) == 0:
			printMsg('findConfigIDs WARNING regex "' + regexStr + '" did not find a matching value. ',False)
			return ''
		printMsg('findConfigIDs <= '+ str(rtnVal), True)
		return rtnVal[0]

#########################################################################################################
# Returns the PMI config for a given server
#########################################################################################################
def getPMIConfig(moduleName,server):
	printMsg('getPMIConfig => '+moduleName+' '+server, True)
	global MasterDict
	serverName=MasterDict[server]['name']
	nodeName=getConfigIDNode(server)
	rtnVal={'NOT_FOUND':'NOT_FOUND'}
	keys=findConfigIDs('.*/'+nodeName+'/.*/'+serverName+'.pmi-config.xml.PMIModule_.*',True,MasterDict)
	for key in keys:
		if MasterDict[key].has_key('moduleName') and MasterDict[key]['moduleName'] == moduleName:
			rtnVal=MasterDict[key]
			break
	printMsg('getPMIConfig <= '+str(rtnVal), True)
	return rtnVal

#########################################################################################################
# Returns the PMI enable attribute sorted 
#########################################################################################################
def getPMICellValue(pmiConfig):
	rtnVal='not configured'
	if pmiConfig.has_key('enable'):
		enable=pmiConfig['enable']
		if enable=='[]':
			enable='not configured'
		if not enable=='not configured':
			enableVals=enable.split(',')
			intVals=[]
			for val in enableVals:
				intVals.append(int(val))
			intVals.sort()
			rtnVal=''
			for i in intVals:
				rtnVal=rtnVal+str(i)+', '
			rtnVal=rtnVal[:-2]
	return rtnVal

#########################################################################################################
# 
#########################################################################################################
def getCellNames(configDict):
	if configDict==None:
		configDict=MasterDict
	rtnVal = []
	keys = configDict.keys()
	for key in keys:
		idx = key.find("cells/")
		if  idx > -1:
			cell = getConfigIDCell(key)
			if rtnVal.count(cell) < 1:
				rtnVal.append(cell)
#	vars = findConfigIDs('.*VariableSubstitutionEntry.*',True,configDict)
#	for var in vars:
#		if configDict[var]['symbolicName']=='WAS_CELL_NAME':
#			cellName=configDict[var]['value']
#			if rtnVal.count(cellName) > 0:
#				printMsg('ERROR: Duplicate cell names found.  '+cellName, False)
#				sys.exit(0)
#			rtnVal.append(cellName)
	printMsg('getCellNames => '+str(rtnVal), True)
	return rtnVal

#########################################################################################################
# Converts a list to a string using the provided delimeter 
#########################################################################################################
def listToString(list,delimeter):
	rtnVal=''
	for element in list:
		rtnVal = rtnVal+element+delimeter
	return rtnVal[:len(delimeter) * -1]

#########################################################################################################
# Returns the config ID based on an attribute value from the specified dictionary
#########################################################################################################
def getConfigIDsByAttrValueFromDict(regexStr,attrValue,attrName,singleton,dictionary):
	printMsg('getConfigIDsByAttrValueFromDict => '+regexStr+','+attrValue+','+attrName, True)
	rtnVal = []
	configIDs=findConfigIDs(regexStr,True,dictionary)
	regex=re.compile('.*'+attrValue+'.*')
	for configID in configIDs:
		if regex.match(dictionary[configID][attrName]):
			rtnVal.append(configID)
	if singleton:
		if len(rtnVal) == 0:
			printMsg('WARNING no ID found => '+regexStr+','+attrValue+','+attrName, True)
			rtnVal='NOT_FOUND'
		elif len(rtnVal) == 1:
			rtnVal = rtnVal[0]
		elif len(rtnVal) > 1:
			printMsg('WARNING no ID found => '+regexStr+','+attrValue+','+attrName, True)
			rtnVal = rtnVal[0]
	printMsg('getConfigIDsByAttrValueFromDict <= '+str(rtnVal), True)
	return rtnVal

#########################################################################################################
# Returns the config ID based on an attribute value
#########################################################################################################
def getConfigIDByAttrValue(regexStr,attrValue,attrName):
	rtnVal = getConfigIDsByAttrValueFromDict(regexStr,attrValue,attrName,True,MasterDict)
	return rtnVal

#########################################################################################################
# Returns the config IDs of servers in a cell
#########################################################################################################
def getServerConfigIDs(cell,node,name):
	servers = getConfigIDsByAttrValueFromDict('.*/'+cell+'.*/'+node+'/.*'+re.escape('#Server_')+'.*',name,'name',False,MasterDict)
	rtnVal = []
	for server in servers:
		try:
			if MasterDict[server]['serverType'] == 'APPLICATION_SERVER':
				rtnVal.append(server)
		except:
			None
	return rtnVal

#Begin Ref0012
#########################################################################################################
# Returns the nodeagent IDs
#########################################################################################################
def getNodeAgentConfigIDs():
	servers = getConfigIDsByAttrValueFromDict('.*'+re.escape('#Server_')+'.*','nodeagent','name',False,MasterDict)
	rtnVal = []
	for server in servers:
		try:
			if MasterDict[server]['serverType'] == 'NODE_AGENT':
				rtnVal.append(server)
		except:
			None
	return rtnVal
#End Ref0012

#########################################################################################################
# Returns the config ID of a cluster in a cell
#########################################################################################################
def getClusterConfigIDs(cell,name):
	#print cell + ' : ' + name
	rtnVal = getConfigIDsByAttrValueFromDict('.*/'+cell+'/.*'+re.escape('#ServerCluster_')+'.*',name,'name',False,MasterDict)
	#print 'rtn: ' + str(rtnVal)
	return rtnVal

#########################################################################################################
# Returns all properties matching the regex from from passed in properties dict or from PropertiesDict
#########################################################################################################
def getAllPropKeys(regex,propertiesDict): #Ref0025
	if propertiesDict == None:            #Ref0025
		propertiesDict = PropertiesDict   #Ref0025
	regex=re.compile(regex)
	rtnVal=[]
	keys=propertiesDict.keys()            #Ref0025
	for key in keys:
		if regex.match(key):
			rtnVal.append(key)
	return rtnVal

#########################################################################################################
# Returns the Data Source with the given JNDI name
#########################################################################################################
def getDataSourceByJNDI(cell,node,server,name):
	return getConfigIDsByAttrValueFromDict('.*'+cell+'/nodes/'+node+'/servers/'+server+'.*DataSource_.*',name,'jndiName',False,MasterDict)

#########################################################################################################
# Returns the Data Source for a servver report
#########################################################################################################
def getDataFromConfigPath(server,path):
	path.insert(0,server)
	return getDataSourceByJNDI(getConfigIDCell(server),getConfigIDNode(server),getConfigIDServer(server),getConfigFromPath(path)['datasourceJNDIName'])

#########################################################################################################
# Returns the specified attribute for all configuration IDs of the given type
#########################################################################################################
def getUniqueConfigAttrValues(configType,attr):
	configIDs = findConfigIDs('.*'+re.escape('#'+configType+'_')+'.*', True, MasterDict)
	values = []
	for configID in configIDs:
		if values.count(MasterDict[configID][attr]) == 0:
			values.append(MasterDict[configID][attr])
	values.sort()
	return values

#########################################################################################################
# Sorts the input list by the scope function 
#########################################################################################################
def sortByCellAndScope(list,scopeFunc,nameAttr):  #Ref0015
	tempList = []
	idx=0
	for resource in list:
		scope = scopeFunc(resource,nameAttr) #Ref0015
		tempList.append(scope+'%'+str(idx))
		idx = idx + 1
	tempList.sort()
	sortedList = []
	for resource in tempList:
		idx = int(resource.split('%')[1])
		sortedList.append(list[idx])
	return sortedList

#Ref0004 Begin
#################################################################################
# Sets up data structures for looking up variable names and values 
#########################################################################################################
variablesDictList = []
variableNames = []
def getVariableData():
	if len(variablesDictList) == 0:
		variableIDList = findConfigIDs(".*VariableSubstitutionEntry.*",True,None)
		for variableID in variableIDList:
			varDict = {}
			varDict['symbolicName'] = MasterDict[variableID]['symbolicName']
			try:                                             #Ref0017
				varDict['value'] = MasterDict[variableID]['value']
			except:                                          #Ref0017
				varDict['value'] = 'Attribute not defined'   #Ref0017
			try:                                             #Ref0017
				varDict['scope'] = getScope(variableID)
			except:                                          #Ref0017
				varDict['scope'] = 'Attribute not defined'   #Ref0017
			if variableNames.count(MasterDict[variableID]['symbolicName']) < 1:
				variableNames.append(MasterDict[variableID]['symbolicName'])
			variablesDictList.append(varDict)
		variableNames.sort()

#########################################################################################################
# resolves a variable name to a values pased on the input scope 
#########################################################################################################
def resolveVariable(name,server):
	getVariableData()
	scope = getScope(server)
	bestMatch = name
	bestMatchLen = 0
	for varDict in variablesDictList:
		if name == varDict['symbolicName']:
			if scope == varDict['scope']:
				bestMatch = varDict['value']
				break
			else:
				if scope.find(varDict['scope']) == 0 and len(varDict['scope']) > bestMatchLen:
					bestMatch = varDict['value']
					bestMatchLen = len(varDict['value'])
	return bestMatch
	
#########################################################################################################
# resolves a variable name to a values pased on the input scope 
#########################################################################################################
def getVariableNames():
	getVariableData()
	return variableNames
#Ref0004 End

#Begin Ref0009 
#########################################################################################################
# Returns the HTML equivelent of a given character
#########################################################################################################
htmlCharDict = {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}  #Bugbug this is a small subset of possible special characters.
def replaceHTMLChar(char):
	global htmlCharDict
	rtnVal = char
	try:
		rtnVal = htmlCharDict[char]
	except:
		None
	return rtnVal

#########################################################################################################
# Replaces characters with meaning in HTML documents with the HTML equivelents
#########################################################################################################
def encodeHTML(string):
	rtnVal = ''
	for char in string:
		rtnVal = rtnVal + replaceHTMLChar(char)
	return rtnVal
#End Ref0009 

#Begin Ref0023
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
# Functions for report and script generation
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

TimeStamp=time.strftime('_%y%m%d%H%M%S')
TitleTimeStamp=time.strftime(' %m/%d/%y %H:%M:%S')
ReportFileHTML='HTML'
ReportFileHTMLName=''
SampleScriptContents=''
SampleScriptFileName=''
SampleScriptWrite=False

#color attributes for tables in the HTML reports
tableHeaderColor=' bgcolor="#cccccc" '
tableTitleColor=' bgcolor="#999999" '
tableNotMatchColor=' bgcolor="#dd0000" '
tableMatchColor=' bgcolor="#00dd00" '
tableFlagColor=' bgcolor="#eeee33" '
tableFlagColorIgnore=' bgcolor="#00ffff" '

#table column widths 
headerColWidthNum=350
valueColWidthNum=200
matchColWidthNum=65
headerColWidth=' width="'+str(headerColWidthNum)+'" '
valueColWidth=' width="'+str(valueColWidthNum)+'" '
matchColWidth=' width="'+str(matchColWidthNum)+'" '

def matchColumn(dict):
	if 'MatchColumn' in dict and dict['MatchColumn']=='ignore':
		return False
	else:
		return True

#########################################################################################################
# Opens report files and writes out initial report data.  
#########################################################################################################
def reportInitialize(title,baseFileName):
	printMsg('reportInitialize => '+title, True)
	global TimeStamp
	global TitleTimeStamp
	global ReportFileHTML
	global ReportFileHTMLName
	global SampleScriptFileName
	global SampleScriptContents
	global SampleScriptWrite
	
	basePath = ''
	try:
		basePath = PropertiesDict['ConfigurationReportOutputPath'].strip()
		if not basePath[len(basePath)-1:] == os.sep and len(basePath) > 0:  #Ref0016
			basePath = basePath+os.sep                                      #Ref0016
	except:
		None 
	baseFileName = basePath + baseFileName
	
	#Ref0003 Create output directory if it does not exist.
	if len(basePath) > 0:  #Ref0016
		try:
			os.stat(basePath)
		except:
			os.mkdir(basePath)
	#Ref0003 End
	#initialize HTML file report
	ReportFileHTMLName = baseFileName+TimeStamp+'.html'
	ReportFileHTML = open(ReportFileHTMLName,'w')
	ReportFileHTML.write('<html>\n<head>\n<meta http-equiv="content-type" content="text/html; charset=UTF-8">\n<title>'+ \
	                     title+'</title>\n</head>\n<body>')
	ReportFileHTML.write('<div class="wrap content">\n<style>\n.normal\n{white-space:\nnormal;}\n.wrapped\n{white-space: pre;\nwhite-space: pre-wrap;\n'\
	                     'white-space: pre-line;\nwhite-space: -pre-wrap;\nwhite-space: -o-pre-wrap\nwhite-space: -moz-pre-wrap;\nwhite-space: -hp-pre-wrap;\nword-wrap: break-word;\n'\
	                     '}</style>\n')
	ReportFileHTML.write('<br><big><big><big><b>'+title+TitleTimeStamp+'</b></big></big></big><br><br><br>\n')
	
	#Ref0006 Begin Added a key at the top of the report
	disableKey = False
	try:
		if PropertiesDict['DisableReportKey'].lower() == 'true':
			disableKey=True
	except:
		None
	if title.find('Cell Summary') == 0:
		disableKey=True
	if not disableKey:
		keyCol1width = 'width="150"'
		keyCol2width = 'width="1050"'
		keyTablewidth = 'width="1200"'
		descr1 = "Only one configuration item, no matching done."
		descr2 = "At least one item in the row does not match with the rest."
		descr3 = "All values match."
		descr4 = "All values match with some literals replaced or ignored."
		descr5 = "Background color indicating value is the most common in the row.  (Note, there could be multiple values most common)."
		descr6 = "Background color indicating all values match due to some literals being repaced."
		descr7 = "Background color indicating value does not match and is not the most common in the row."
		#Begin Ref0031
		if title == 'File System Report':
			descr1 = "Only one file found, no matching done."
			descr2 = "At least one file in the row does not match with the rest."
			descr3 = "All files match."
			descr4 = "File size and CRC match but the date and/or time stamp do not."
			descr5 = "Background color indicating file is the most common in the row.  (Note, there could be multiple differnt files equally most common)."
			descr6 = "Background color indicating file size and CRC match but the date and/or time stamp do not."
			descr7 = "Background color indicating files do not match and this file is not the most common in the row."
		#End Ref0031
		ReportFileHTML.write('<table style="table-layout:fixed" border="2" cellpadding="2" cellspacing="0" %s>\n' % keyTablewidth)
		ReportFileHTML.write('<td colspan="7" rowspan="1" %s  valign="top"><big><big><b>Report Key</b></big></big><br></td></tr>\n' % tableTitleColor)
		ReportFileHTML.write('<col %s />' % keyCol1width)
		ReportFileHTML.write('<col %s />\n' % keyCol2width)
		ReportFileHTML.write('<tr><td class="wrapped" %s  %s  valign="top"><b>Cell Contents</b><b><br></b>\n' % (tableHeaderColor,keyCol1width))
		ReportFileHTML.write('</td><td class="wrapped" %s  %s  valign="top"><b>Description</b><b><br></b> </td></tr>\n' % (tableHeaderColor,keyCol2width))
		ReportFileHTML.write('<tr><td class="wrapped" %s  %s  valign="top"><b>%s</b><b><br></b> </td>\n' % (tableFlagColor,keyCol1width,"N/A"))
		ReportFileHTML.write('<td class="wrapped" %s  valign="top"><b>%s</b><b><br></b> </td></tr>\n' % (keyCol2width,descr1))
		ReportFileHTML.write('<tr><td class="wrapped" %s  %s  valign="top"><b>%s</b><b><br></b> </td>\n' % (tableNotMatchColor,keyCol1width,"No"))
		ReportFileHTML.write('<td class="wrapped" %s valign="top"><b>%s</b><b><br></b> </td></tr>\n' % (keyCol2width,descr2))
		ReportFileHTML.write('<tr><td class="wrapped" %s  %s valign="top"><b>%s</b><b><br></b> </td>\n' % (tableMatchColor,keyCol1width,"Yes"))
		ReportFileHTML.write('<td class="wrapped" %s valign="top"><b>%s</b><b><br></b> </td></tr>\n' % (keyCol2width,descr3))
		ReportFileHTML.write('<tr><td class="wrapped" %s %s valign="top"><b>%s</b><b><br></b> </td>\n' % (tableMatchColor,keyCol1width,"Yes*"))
		ReportFileHTML.write('<td class="wrapped" %s valign="top"><b>%s</b><b><br></b> </td></tr>\n' % (keyCol2width,descr4))
		ReportFileHTML.write('<tr><td class="wrapped"  %s valign="top"><b></b><b><br></b> </td>\n' % keyCol1width)
		ReportFileHTML.write('<td class="wrapped"  %s valign="top"><b>%s</b><b><br></b> </td></tr>\n' % (keyCol2width,descr5))
		ReportFileHTML.write('<tr><td class="wrapped" %s  %s  valign="top"><b></b><b><br></b> </td>\n' % (keyCol1width,tableFlagColorIgnore))
		ReportFileHTML.write('<td class="wrapped"  %s valign="top"><b>%s</b><b><br></b> </td></tr>\n' % (keyCol2width,descr6))
		ReportFileHTML.write('<tr><td class="wrapped" %s %s  valign="top"><b></b><b><br></b> </td>\n' % (keyCol1width,tableFlagColor))
		ReportFileHTML.write('<td class="wrapped"  %s valign="top"><b>%s</b><b><br></b> </td></tr>\n' % (keyCol2width,descr7))
		ReportFileHTML.write('</tbody></table><br>\n')
		replacedStringList = getReplacedStringList()
		if not replacedStringList == None and len(replacedStringList) > 0:
			keyCol1width = 'width="300"'
			keyCol2width = 'width="300"'
			keyTablewidth = 'width="600"'
			ReportFileHTML.write('<table style="table-layout:fixed" border="2" cellpadding="2" cellspacing="0" %s>\n' % keyTablewidth)
			ReportFileHTML.write('<td colspan="7" rowspan="1" %s  valign="top"><big><big><b>Replacement values for matching</b></big></big><br></td></tr>\n' % tableTitleColor)
			ReportFileHTML.write('<col %s />' % keyCol1width)
			ReportFileHTML.write('<col %s />\n' % keyCol2width)
			ReportFileHTML.write('<tr><td class="wrapped" %s  %s  valign="top"><b>Value</b><b><br></b>\n' % (tableHeaderColor,keyCol1width))
			ReportFileHTML.write('</td><td class="wrapped" %s  %s  valign="top"><b>Is replaced with</b><b><br></b> </td></tr>\n' % (tableHeaderColor,keyCol2width))
			for replacementPair in replacedStringList:
				ReportFileHTML.write('<tr><td class="wrapped"  %s  valign="top"><b>%s</b><b><br></b> </td>\n' % (keyCol1width,replacementPair[0]))
				ReportFileHTML.write('<td class="wrapped"  valign="top"><b>%s</b><b><br></b></td></tr>\n' % (replacementPair[1]))
			ReportFileHTML.write('</tbody></table><br>\n')
	#Ref0006 End Added a key at the top of the report
	#Begin Ref0022
	SampleScriptWrite = False
	if OutputScripts:
		SampleScriptFileName = baseFileName+TimeStamp+'.py'
		fn = SampleScriptFileName.split(os.sep)
		fn = fn[len(fn)-1]
		scriptHeader = '######################################################################\n'+\
					   '# This is a sample script created by the WebSphere Configuration     #\n'+\
					   '# Comparison Tool (CCT).  This script provides sample code utilizing #\n'+\
					   '# AdminConfig to correct differences in configuration items          #\n'+\
					   '# identified by CCT.                                                 #\n'+\
					   '#                                                                    #\n'+\
					   '# Notes:                                                             #\n'+\
					   '# - Some differences are expected and should not be corrected        #\n'+\
					   '# - CCT is in beta and provided "as is"                              #\n'+\
					   '# - Test in a lower environment before running in production         #\n'+\
					   '# - Search for "REVIEW:" for areas that may need to be customized    #\n'+\
					   '# - Script samples for WebSphere variables not implemented           #\n'+\
					   '#                                                                    #\n'+\
					   '# *** Please review carefully before being run ***                   #\n'+\
					   '#                                                                    #\n'+\
					   '# Please report any defects or suggestions to:                       #\n'+\
					   '#     Dennis Riddlemoser                                             #\n'+\
					   '#     riddlemo@us.ibm.com                                            #\n'+\
					   '######################################################################\n\n'+\
					   '# Create a repository checkpoint to revert changes if necessary\n'
		chkpt = "print 'Creating repository checkpoint %s'\nAdminTask.createFullCheckpoint('[-checkpointName %s -checkpointDesc \"Created to restore changes made by %s\"]')\n\n" % (fn,fn,fn)
		SampleScriptContents = scriptHeader+chkpt
	#End Ref0022

#########################################################################################################
# writes out final report info and closes report files.  
#########################################################################################################
def reportFinalize():
	printMsg('reportFinalize', True)
	global reportFormat
	global ReportFileHTML
	global ReportFileHTMLName
	global SampleScriptContents
	global SampleScriptFileName
	global SampleScriptWrite
	ReportFileHTML.write('</div>Note, if there is no output, check to ensure there were resources found to compare and ' + \
	                      'ReportOnlyMismatched is either not present or set to False.</body>\n</html>')
	ReportFileHTML.close()
	printMsg('Created report %s' % ReportFileHTMLName,False)
	#Begin Ref0022
	if OutputScripts and SampleScriptWrite:
		scriptFooter = '# REVIEW:  Uncomment when all other modifications have been made\n'      +\
					   '#print "Saving configuration changes"\n'                                 +\
					   '#AdminConfig.save()   # Saves all changes to the master repository\n'    +\
					   '######################################################################\n'+\
					   '################### End sample script. ###############################\n'+\
					   '######################################################################\n'
		sampleScriptFile = open(SampleScriptFileName,'w')
		sampleScriptFile.write(SampleScriptContents+scriptFooter)
		sampleScriptFile.close()
		printMsg('Created script %s' % SampleScriptFileName,False)
	else:
		if OutputScripts:
			printMsg('No configuration differences found.  A sample script was not created.',False)

	#End Ref0022

#Begin Ref0022
#########################################################################################################
# Set OutputScripts controlling output of sample wsadmin jython scripts
#########################################################################################################
OutputScripts=False
def setOutputScripts(report):
	global OutputScripts
	OutputScripts=False
	value = 'false'
	try:
		value = PropertiesDict['OutputScripts'].lower()
	except:
		None
	try:
		value = PropertiesDict[report+':OutputScripts'].lower()
	except:
		None
	if value == 'true':
		OutputScripts=True
	elif value == 'false':
		OutputScripts=False
#	Debug = True
#	printException('Exception in setOutputScripts',sys.exc_info())
#	Debug = False
#End Ref0022

#Begin Ref0010
#########################################################################################################
# Set ReportOnlyMismatched uses in isEligableForOutput()
#########################################################################################################
ReportOnlyMismatched='false'
def setReportOnlyMismatched(report):
	global ReportOnlyMismatched
	ReportOnlyMismatched='false'
	if ['true','false','all'].count(report.lower()) == 1:
		ReportOnlyMismatched = report.lower()
	else:
		try:
			ReportOnlyMismatched = PropertiesDict['ReportOnlyMismatched'].lower()
		except:
			None
		try:
			ReportOnlyMismatched = PropertiesDict[report+':ReportOnlyMismatched'].lower()
		except:
			None
#		Debug = True
#		printException('Exception in setReportOnlyMismatched',sys.exc_info())
#		Debug = False

#########################################################################################################
# Returns "No" if list has any "No values", returns "Yes*" is there are no "No values and a "Yes*" value,
# otherwise returns "Yes"
#########################################################################################################
def relevantMatchColumnValue(matchList):
	rtnVal = 'Yes'
	if matchList.count('No') > 0:
		rtnVal = 'No';
	elif matchList.count('Yes*') > 0:
		rtnVal = 'Yes*'
	return rtnVal

#########################################################################################################
# Returns true if the row should be output based on ReportOnlyMismatched and match value
#########################################################################################################
def isEligableForOutput(matchList):
	rtnVal = True
	listVal = relevantMatchColumnValue(matchList)
	if ReportOnlyMismatched == 'all' and not (listVal == 'Yes*' or listVal == 'No'):
		rtnVal = False
	elif ReportOnlyMismatched == 'true' and not listVal == 'No':
		rtnVal = False
	return rtnVal

#########################################################################################################
# Returns true if the row should be output based on ReportOnlyMismatched and match value
#########################################################################################################
def isRowEligableForOutput(matchValue):
	return isEligableForOutput([matchValue])

#########################################################################################################
# Returns true if the table should be output based on ReportOnlyMismatched value and table data
#########################################################################################################
def isTableEligableForOutput(table):
	rtnVal = True
	if matchColumn(table):
		rtnVal = isEligableForOutput(table['Match'])
	return rtnVal

#########################################################################################################
# Returns true if the table should be output based on ReportOnlyMismatched value and all report table data
#########################################################################################################
def isReportEligableForOutput(rptParms):
	rtnVal = False
	reportTables=rptParms['Tables']
	for table in reportTables:
		rtnVal = rtnVal or isTableEligableForOutput(table)
	return rtnVal
#End Ref0010

#########################################################################################################
# begins an individual report
#
# rptParms see writeReport()
#########################################################################################################
def reportBegin(rptParms):
	global ReportFileHTML
	if isReportEligableForOutput(rptParms):  #Ref0010
		printMsg('reportBegin => '+str(rptParms), True)
		#write HTML config report title
		width=headerColWidthNum+matchColWidthNum
		if matchColumn(rptParms):
			width=headerColWidthNum
		for col in rptParms['ColumnHeaders']:
			width=width+valueColWidthNum+2+2+0
		ReportFileHTML.write('<table style="table-layout:fixed" border="2" cellpadding="2" cellspacing="0" width='+str(width)+'>\n')
		ReportFileHTML.write('<col'+headerColWidth+'/>\n')
		if matchColumn(rptParms):
			ReportFileHTML.write('<col'+matchColWidth+'/>\n')
		for col in rptParms['ColumnHeaders']:
			ReportFileHTML.write('<col'+valueColWidth+'/>\n')
		printMsg('reportBegin <='+str(rptParms), True)
	else:                                                            #Ref0010
		printMsg('reportBegin (no output)<='+str(rptParms), True) #Ref0010

#########################################################################################################
# ends an individual report
#
# rptParms see writeReport()
#########################################################################################################
def reportEnd(rptParms):
	global ReportFileHTML
	if isReportEligableForOutput(rptParms):  #Ref0010
		printMsg('reportEnd => '+str(rptParms), True)
		#end HTML table
		ReportFileHTML.write('</tbody></table><br>\n')
		printMsg('reportEnd <='+str(rptParms), True)
	else:                                                          #Ref0010
		printMsg('reportEnd (no output)<='+str(rptParms), True) #Ref0010

#########################################################################################################
# Writes an individual report based on report parameters passed in.
#
# rptParms = report parameters dictionary
#
# The dictionary needs to have the following keys defined.
# [Tables] = List of output table dictionaries (see below)
# [ColumnHeaders] = Column headers for output tables
#
#########################################################################################################
def reportWrite(rptParms):
	printMsg('reportWrite => '+str(rptParms), True)

	reportBegin(rptParms)

	reportTables=rptParms['Tables']
	columnHeaders=rptParms['ColumnHeaders']
	
	for table in reportTables:
		reportWriteTable(table,columnHeaders)

	reportEnd(rptParms)

#########################################################################################################
# writes table for a report
#
# table = a table dictionary (see below)
# ColumnHeaders = Column headers for the table report
#
# A table dictionary has the following keys:
# [Title] = The title of this table report
# [RowHeaders] = The row headers for the table
# [TableData] = A list of lists.  Each list contains an entry for each server for the specific header.
# [Match] = Indicates is all values in the corresponding row are equal.  "ignore" indicates to omit the match column
# [FirstColumnHeader] = Title for the attributes or properties for the table
# 
#########################################################################################################
def reportWriteTable(table,columnHeaders):
	global SampleScriptWrite
	global SampleScriptContents
	printMsg('reportWriteTable => '+str(table), True)
	if isTableEligableForOutput(table):  #Ref0010
		title=table['Title']
		match = []
		if matchColumn(table):
			match=table['Match']
		firstColumnHeader=table['FirstColumnHeader']
		rowHeaders=table['RowHeaders']
		tableData=table['TableData']
		configDifferences=False

		#write HTML config report title
		x=1
		if matchColumn(table):
			x=2
		ReportFileHTML.write('<tbody><tr align="left">\n<td colspan="'+str(len(columnHeaders)+x)+  '" rowspan="1"'+tableTitleColor+' valign="top"><big><big><b>'+ \
							 title+'</b></big></big><br></td></tr>\n')

		#write HTML column headers for attributes
		if matchColumn(table):
			ReportFileHTML.write('<tr><td class="wrapped"'+tableHeaderColor+headerColWidth+' valign="top"><b>'+firstColumnHeader+'</b><b><br></b> </td>'\
								'<td class="wrapped"'+tableHeaderColor+matchColWidth+' valign="top"><b>Config Matches</b><b><br></b> </td>\n')
		else:
			ReportFileHTML.write('<tr><td class="wrapped"'+tableHeaderColor+headerColWidth+' valign="top"><b>'+firstColumnHeader+'</b><b><br></b> </td>\n')

		for header in columnHeaders:
			ReportFileHTML.write('<td class="wrapped"'+tableHeaderColor+valueColWidth+' valign="top"><b>' +\
								  header + '</b><b><br></b> </td>\n')
		ReportFileHTML.write('</tr>')

		#Write attribute rows
		idx=0
		lastRowHeader = ''
		numHeaderOccurences = 1
		for header in rowHeaders:
			outputRow = True
			if matchColumn(table) and not isRowEligableForOutput(match[idx]):   #Ref0010
				idx=idx+1                                                       #Ref0010
				continue                                                        #Ref0010
			suffix = ''
			if header == lastRowHeader:
				numHeaderOccurences = numHeaderOccurences + 1
				suffix = ' (' + str(numHeaderOccurences) + ')'
			else:
				lastRowHeader = header
				numHeaderOccurences = 1
			#write HTML row header
			ReportFileHTML.write('<tr><td class="wrapped"'+tableHeaderColor+headerColWidth+' valign="top"><b>'+header+suffix+'</b><b><br></b> </td>\n')

			#write HTML match value
			if matchColumn(table):
				color = tableMatchColor
				if match[idx] == 'No':
					color = tableNotMatchColor
					configDifferences = True
					SampleScriptWrite = True
				elif match[idx] == 'N/A':
					color = tableFlagColor
				ReportFileHTML.write('<td class="wrapped"' + color + matchColWidth + 'valign="top">' + match[idx] + '<br></td>\n')

			#write attribute values
			for value in tableData[idx]:
				color=""

				#Ref0005 Begin added check for match change color if a mismatch was ignored
				if matchColumn(table) and match[idx] == 'Yes*':
					color = tableFlagColorIgnore
					#Ref0005 End
				elif matchColumn(table) and not isMostCommon(value,tableData[idx]):
					color = tableFlagColor
				#write HTML value
				#Begin Ref0009
				encodeValue = True
				try:
					encodeValue = table['EncodeHTML']
				except:
					None
				if encodeValue:
					value = encodeHTML(value)
				#End Ref0009
				ReportFileHTML.write('<td class="wrapped"'+valueColWidth+color+'valign="top">' + value + '<br></td>\n') 
			
			#end HTML row
			ReportFileHTML.write('</tr>\n')
			idx=idx+1
			
		#Begin Ref0022
		if OutputScripts and configDifferences:
			tblHdr = ('##############################################################################\n'+\
					 '# Sample script for table title "%s"\n'+\
					 '##############################################################################\n' +\
					 'print "Making updates identified in table \\\"%s\\\""\n') % (title,title)
			SampleScriptContents = '%s%s' % (SampleScriptContents,tblHdr)
			if table['Type'] == 'Properties':
				idx = 0
				varStr = '# REVIEW: Modify to select the proper value for the property %s\n%s\n' % (rowHeaders[idx],scriptOutputVariables(table))
				propNotSet=False
				if varStr.find('property not set') > -1:
					propNotSet=True
					varStr = '%s# REVIEW: WARNING, some properties are not set on all servers.  Logic to add or remove properties may be necesssay.\n' % varStr
					varStr = '%s# REVIEW:          Logic to update properties has been commentd out due to likelihood of inconsistent update.\n' % varStr
				SampleScriptContents = '%s\n%s' % (SampleScriptContents,varStr)
				for matchValue in table['Match']:
					if matchValue == 'No':
						configIDs = []
						for configID in table['ConfigIDs']:
							if MasterDict[configID]['name'] == rowHeaders[idx]:
								configIDs.append(configID)
						cfgIDStr = scriptOutputConfigID(configIDs)
						modStr = "for configID in configIDs:" 
						modStr = "%s\n\tAdminConfig.modify(configID,'[[value \"' + attr_%s_value + '\"]]')\n" % (modStr,rowHeaders[idx])
						if propNotSet:
							modStr = '#%s' % modStr.replace('\n','\n#')[:-1]
							cfgIDStr = '#%s' % cfgIDStr.replace('\n','\n#')[:-1]
						SampleScriptContents = '%s\n%s\n%s\n' % (SampleScriptContents,cfgIDStr,modStr)
					idx = idx + 1 
			elif table['Type'] == 'Attributes' or table['Type'] == 'JVMArguments':
				varStr = '# REVIEW: Modify as necessary to select the proper attribute value for the environment\n%s ' % (scriptOutputVariables(table))
				cfgIDStr = scriptOutputConfigID(table['ConfigIDs'])
				idx = 0
				modStr = ''
				for matchValue in table['Match']:
					if matchValue == 'No':
						modStr = "%s\n\t\t'[%s \"' + attr_%s_value + '\"]' +\\" % (modStr,rowHeaders[idx],rowHeaders[idx])
					if table['Type'] == 'JVMArguments':
						varStr = '# REVIEW: Modify to create the proper generic JVM arguments for the environment\n%s\n' % (varStr.splitlines()[1])
						break
					idx = idx + 1
				modStr = "for configID in configIDs:\n\tAdminConfig.modify(configID,'[' +\\%s' +\\\n\t\t']')\n" % modStr[:-4]				
				SampleScriptContents = '%s\n%s\n%s\n%s\n' % (SampleScriptContents,cfgIDStr,varStr,modStr)
		#End Ref0022
		printMsg('reportWriteTable <='+str(table), True)
	else:                                                              #Ref0010
		printMsg('reportWriteTable (no output)<='+str(table), True) #Ref0010
		
#Begin Ref0022
def scriptOutputConfigID(configIDs):
	cfgIDStr = '# REVIEW: Make sure the configuration elements on the servers and nodes listed are correct\n' +\
				'configIDs = [ \\\n' 
	prevCellSuffix = '_FIRST_ITERATION_'
	for cfgID in configIDs:
		(configID,cellSuffix) = stripCellSuffix(cfgID)
		if not cellSuffix == prevCellSuffix:
			cfgIDStr = '%s# Configuration ID list corresponding to columns in report with "%s" cell name\n' \
						% (cfgIDStr,getConfigIDCell(cfgID))
			prevCellSuffix = cellSuffix
		cfgIDStr = "%s\t'%s',\\\n" % (cfgIDStr,configID)
	cfgIDStr = '%s\t]\n' % cfgIDStr
	return cfgIDStr
	
def scriptOutputVariables(table):
	varStr = ''
	tableData=table['TableData']
	rowHeaders=table['RowHeaders']
	idx = 0
	for matchValue in table['Match']:
		if matchValue == 'No':
			outputValue = 'NOT_FOUND'
			allValues = []
			for value in tableData[idx]:
				if allValues.count(value) == 0:
					allValues.append(value)
				if isMostCommon(value,tableData[idx]):
					outputValue = value
			varStr = "%sattr_%s_value = '%s'\t\t#Diffrent values for %s:" % \
				(varStr,rowHeaders[idx],outputValue,rowHeaders[idx])
			allValues.sort()
			for value in allValues:
				varStr = '%s "%s"' % (varStr,value)
			varStr = varStr + '\n'
		idx = idx + 1
	return varStr
#End Ref0022
#End Ref0023

#Begin Ref0027

#########################################################################################################
# 
#########################################################################################################
def ReportFileSystem(ServerDataList):
	printMsg('Generating File System Report',False)
	fileLists = []
	columnHeaders = []
	#Read all of the file lists create row headers
	for serverData in ServerDataList:
		if serverData['TarFile'] == None:
			f = open(serverData['FQFileName'],'r')
			lines = f.readlines()
			f.close()
			fileLists.append(lines)
		else:
			fileLists.append(readFileFromTarAsLines(serverData['TarFile'],'file-list.txt'))
		columnHeaders.append(serverData['ColumnHeader'])
	
	allFilesList = []
	serverFileList = []
	for fileList in fileLists:
		serverFileDict = {}
		for line in fileList:
			fields = line.split('|')
			fileName = fields[2].strip()
			if fileName.find('./') == 0:
				fileName = fileName[2:]
#Begin Ref0035 Adding AIX support
			fileCRC = ""
			fileSize = ""
			fileDate = ""
			fileTime = ""
			if line.find('Modify:') == 0:  #New format for GNU stat output from CollectFileData.sh
				fileCRC = fields[1].split(' ')[0]
				fileSize = fields[1].split(' ')[1]
				fileDate = fields[0][8:].split(' ')[0]
				fileTime = '%s GMT %s' % (fields[0][8:].split(' ')[1],fields[0][8:].split(' ')[2])
			elif line.find('Last modified:') == 0:  #Format for AIX istat output from CollectFileData.sh
				fileCRC = fields[1].split(' ')[0]
				fileSize = fields[1].split(' ')[1]
				fileDate = fields[0][15:26]+fields[0][39:]
				fileTime = fields[0][26:38]
			else:
				try:  #Original format for GNU stat output from CollectFileData.sh
					fields = line.split('|')
					fileCRC = fields[1].split(' ')[0]
					fileSize = fields[1].split(' ')[1]
					fileDate = fields[0].split(' ')[0]
					fileTime = '%s GMT %s' % (fields[0].split(' ')[1],fields[0].split(' ')[2])
				except:
					print line
					printMsg('ERROR: Unsupported file listing format.',False)
					sys.exit(1)
#End Ref0035 Adding AIX support
			fileCellValue = 'Date:%s<br>Time:%s<br>Size:%s<br>CRC:%s' % (fileDate,fileTime,fileSize,fileCRC)
			serverFileDict[fileName] = {'Date':fileDate,'Time':fileTime,'CRC':fileCRC,'Size':fileSize,'CellValue':fileCellValue}
			if allFilesList.count(fileName) == 0:
				allFilesList.append(fileName)
		serverFileList.append(serverFileDict)
	
	allFilesList.sort()
	tableData = []
	matchColumn = []
	for file in allFilesList:
		rowData = []
		for serverFileDict in serverFileList:
			try:
				rowData.append(serverFileDict[file]['CellValue'])
			except:
				rowData.append('NOT FOUND')
		matchColumn.append(fileListElementsMatch(rowData)) #Ref0030
		tableData.append(rowData)
	
	tableParms = {'Title':'File System Report',\
					'FirstColumnHeader':'File Name',\
					'EncodeHTML':False,\
					'TableData':tableData,\
					'RowHeaders':allFilesList,\
					'Match':matchColumn}
	rptParms = {'ColumnHeaders':columnHeaders,'Tables':[tableParms]}
	reportWrite(rptParms)

##########################################################################################
# 
##########################################################################################
def createServerFileDataList(fileSpecs):
	rtnVal = []
	printMsg('Files used for this report:',False)
	for fileSpec in fileSpecs:
		for name in glob.glob(fileSpec.strip()):
			printMsg('\t%s' % name,False)
			fileDate = "No Date"
			fileTime = "No Time"
			fileName = name[name.rfind(os.sep)+1:]
			if re.match('.*\.[0-9]{8}\.[0-9]{6}\.',fileName):
				fields = name.split('.')
				fileDate = '%s-%s-%s' % (fields[1][0:4],fields[1][4:6],fields[1][6:8])
				fileTime = '%s:%s:%s' % (fields[2][0:2],fields[2][2:4],fields[2][4:6])
			columnHeader = 'Data file: %s<br>Date: %s<br>Time: %s' % (fileName,fileDate,fileTime)
			tarFile = None
			if name.find(".tar") > -1:
				tarFile = tarfile.open(name,'r')
			rtnVal.append({'FQFileName':name,'TarFile':tarFile,'FileName':fileName,'FileDate':fileDate,'FileTime':fileTime,'ColumnHeader':columnHeader})
	return rtnVal

##########################################################################################
# 
##########################################################################################
def readFileFromTarAsLines(tarFile,fileName):
	file = tarFile.extractfile(fileName)
	rtnVal = []
	while True:
		line=file.readline()
		if line == "":
			break
		else:
			rtnVal.append(line.strip())
	file.close()
	return rtnVal

#End Ref0027
