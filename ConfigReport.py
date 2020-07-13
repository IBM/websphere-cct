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
# This script generates reports based on output from ConfigDump.py
##########################################################################################
# Change history:
# Date        Ref  Who  Comments
# 4/9/2018    0003 DWR  Create output directory if it does not exist.
# 2018/05/18  0004 DWR  Added WebSphere variables report
# 2018/05/26  0005 DWR  Added support for ignoring certain strings in match values.  
# 2018/05/27  0006 DWR  Added a report key.  
# 2018/05/28  0007 DWR  Replace all server, node and cell names with .* for matching by default.
# 2018/05/29  0008 DWR  Broke up servers into application servers and web servers in Cell Summary report
# 2018/05/29  0009 DWR  replace characters for display in HTML
# 2018/05/30  0010 DWR  Generate a second report with only items that don't match or match with replacements.
# 2018/06/01  0011 DWR  Specify multiple poperties files and properties on command line.
# 2018/06/01  0012 DWR  Implemented node agent report, removed file transfer and syncronization from server report
# 2018/06/02  0013 DWR  Implemented comprehensive thread pool report.
# 2018/06/16  0015 DWR  Implemented SSL reports. 
# 2018/08/02  0016 DWR  Fixing Windows path dependencies. 
# 2018/08/02  0018 DWR  Creeated ResourceEnvironmentProvider and ResourceEnvEntry reports
# 2018/09/21  0019 DWR  Fixed exception in jvm arguments report
# 2018/10/30  0020 DWR  Corrected character truncation in reporting JVM arguments and consolidated end character checking logic
# 2018/11/13  0021 DWR  Implemented Application reports
# 2018/11/20  0022 DWR  Implemented outputing of sample wsadmin scripts to correct configurtion differences.
# 2019/01/08  0023 DWR  Restructuring code.  Moving report output functions to ConfigUtils.py
# 2019/01/29  0025 DWR  Implementing built-in clusters report
# 2019/03/22  0028 DWR  Implementing Trust Association Interceptor report
# 2019/05/22  0033 DWR  Errors in Trust Association report and script generation.
# 2019/07/30  0034 DWR  Corrected row matching error in SSL ciphers report.  
# 2020/01/28  0040 DWR  Put error checking in place if user defined report matches an internal one
# 2020/01/28  0041 DWR  Default ReportList to All
# 2020/01/28  0043 DWR  Reworked algorithm to collect server config IDs for server reports.
# 2020/01/28  0045 DWR  Added JMS Provider report
# 2020/01/28  0046 DWR  Added Generic JMS Connection Factory report 
# 2020/01/28  0047 DWR  Added Generic JMS Destination report 
# 2020/01/28  0048 DWR  Added Generic J2C Activation Spec 
# 2020/01/29  0049 DWR  Added Generic JAAS Alias 
# 2020/01/29  0050 DWR  Removed duplicate resource property sub report and added some missing properties
# 2020/02/17  0051 DWR  All properties are optional as they have been given default values, may now be run without any parameters

import ConfigUtils as cu
import sys
import time
import re
import os
import traceback
#Load libraries from where the path they are installed.
path = os.getenv('IBM_JAVA_COMMAND_LINE')
if path == None or len(path) == 0:
	path=sys.argv[0]
else:
	path=path[path.find("-f") + 2:].strip()
path=path.split(' ')[0]
if path.find(os.sep) > -1:
	path=path.split(' ')[0]
	path=path[:path.rfind(os.sep)+1]
else:
	path = ''

sys.path.append(path)
ScriptPath=path #Ref0011

import ConfigUtils as cu
True=1
False=0

#########################################################################################################
# Creates a report table of jvm arguments and adds the table to rptParms
#########################################################################################################
def reportJvmArguments(rptParms):
	cu.printMsg('reportJvmArguments => '+str(rptParms), True)
	servers=rptParms['ServerList']
	uniqueArgList=[]
	argList=[]
	configIDs=[]  #Ref0022
	for server in servers:
		argLine='No_JVM_arguments_present'   #Ref0012 Not all Node Agents have JVM arguments
		args=[]                              #Ref0012
		try:                                 #Ref0012
			argLine = cu.getConfigFromPath([server]+rptParms['ConfigPath'])['genericJvmArguments']
			if checkForBrackets(argLine):           #Ref0020
				argLine = cu.stripEndChars(argLine)
			args=argLine.split(' ')
			configID = cu.getConfigFromPath([server]+rptParms['ConfigPath'])	#Ref0022
			if configIDs.count(configID['CONFIG_ID']) == 0:									#Ref0022
				configIDs.append(configID['CONFIG_ID'])										#Ref0022
		except:   #Ref0012
			#None  #Ref0012
			cu.printException('Exception in reportJvmArguments',sys.exc_info())
		for arg in args:
			if len(arg) > 0:
				argDict=getArg(arg,server)
				argList.append(argDict)
				if uniqueArgList.count(argDict['arg'])==0:
					cu.printMsg('reportJvmArguments => appending '+argDict['arg'],True)
					uniqueArgList.append(argDict['arg'])
	args=[]
	for arg in uniqueArgList:
		maxArgCount = getMaxArgCountForServers(arg,argList,servers)
		for x in range(0, maxArgCount):
			args.append(arg)
	if len(args) > 0:  #Ref0012
		args.sort()
		cu.printMsg('reportJvmArguments => args = '+str(args), True)
		tableData=[]
		lastArg=''
		numRepeat=0
		for arg in args:
			row=[]
			if arg == lastArg:
				numRepeat=numRepeat+1
			else:
				lastArg=arg
				numRepeat=0
			for server in servers:
				argLine='No_JVM_arguments_present'   #Ref0012 Node Agents do not have JVM arguments
				try:                                 #Ref0012
					argLine = cu.getConfigFromPath([server]+rptParms['ConfigPath'])['genericJvmArguments'].strip() #Ref0020
					if checkForBrackets(argLine):                                                                  #Ref0020
						argLine = cu.stripEndChars(argLine)
					serverArg=getServerArg(arg,server,argList,numRepeat)
					row.append(serverArg['value'])
				except:            #Ref0012
					#cu.Debug = True
					#cu.printException('JVM Args',sys.exc_info())
					#cu.Debug = False
					row.append('') #Ref0012
			tableData.append(row)
		#insert the entire generic JVM arguments at the top
		args.insert(0,'genericJvmArguments')
		row=[]
		for server in servers:
			try:                                                                                           #Ref0019
				serverArgs = cu.getConfigFromPath([server]+rptParms['ConfigPath'])['genericJvmArguments'].strip()  #Ref0019 Ref0020
				if checkForBrackets(serverArgs):                                                           #Ref0019 Ref0020
					serverArgs=cu.stripEndChars(serverArgs)                                                #Ref0019
				row.append(serverArgs)                                                                     #Ref0019
			except:                                                                                        #Ref0019
				row.append('')                                                                             #Ref0019
		match=[]
		tableData.insert(0,row)
		for row in tableData:
			match.append(cu.listElementsMatch(row))
		argsDict = {'RowHeaders':args,'TableData':tableData,'Match':match,'Title':'JVM Arguments' ,'FirstColumnHeader':'', \
					'ConfigIDs':configIDs,'Type':'JVMArguments'}  #Ref0022
		rptParms['Tables'].append(argsDict)

def checkForBrackets(args):
	rtnVal = False
	if len(args) > 0:
		endChars = [['[',']'],['"','"']]
		for endChar in endChars:
			if args[0] == endChar[0] and args[-1:] == endChar[1]:
				rtnVal = True
	return rtnVal
				
#########################################################################################################
# parses a JVM argument into argument and value returns a dictionary.
#
# return a dictionary with [arg] and [value] keys
#########################################################################################################
def getArg(arg,server):
	cu.printMsg('getArg => '+str(arg), True)
	idx=arg.find(':')
	idx1=arg.find('=')
	if idx == -1 and idx1 > 0 or not idx1 == -1 and idx > idx1:
		idx=idx1
	value=''
	if idx > 0:
		value=arg[idx+1:].strip()
		arg=arg[:idx].strip()
	if len(value) == 0:
		value = 'is set'
	rtnVal={'arg':arg,'value':value,'server':server}
	cu.printMsg('getArg <= '+str(rtnVal), True)
	return rtnVal

#########################################################################################################
# Counts the number of occurrences of a given argument for an individual server in the server list
#########################################################################################################
def getMaxArgCountForServers(argToCheck,argList,servers):
	cu.printMsg('getMaxArgCountForServers => '+ argToCheck, True)
	rtnVal=0
	for server in servers:
		num=0
		for arg in argList:
			if arg['arg'] == argToCheck and arg['server'] == server:
				num=num+1
		if num > rtnVal:
			rtnVal = num
	cu.printMsg('getMaxArgCountForServers <= "'+ argToCheck + '" ' + str(rtnVal), True)
	return rtnVal

#########################################################################################################
# Returns the server argument from the list of arguments
#########################################################################################################
def getServerArg(argToCheck,server,argList,numRepeat):
	cu.printMsg('getServerArg => '+str(argToCheck) + ' ' + str(numRepeat), True)
	numFound = 0
	for arg in argList:
		if arg['arg'] == argToCheck and arg['server'] == server:
			if numFound >= numRepeat:
				return arg
			else:
				numFound = numFound + 1
	return {'arg':argToCheck,'value':'is not set','server':server}

#lists all configuration elements that are effectively collections of name/value pairs
PropertyAttributes=[{'PropName':'properties','PropPath':[]},\
					{'PropName':'customProperties','PropPath':[]},\
					{'PropName':'systemProperties','PropPath':[]},\
					{'PropName':'environment','PropPath':[]},\
					#{'PropName':'properties','PropPath':['adminObjectTemplateProps']},\  BUGBUG some properties may not be being reported.
					{'PropName':'additionalTrustManagerAttrs','PropPath':[]},\
					{'PropName':'webAuthAttrs','PropPath':[]},\
					{'PropName':'trustProperties','PropPath':[]}, #Ref0028\
#Ref0050			{'PropName':'resourceProperties','PropPath':['connectionDefTemplateProps','resourceProperties']},\
					{'PropName':'resourceProperties','PropPath':['propertySet']},\
					{'PropName':'resourceProperties','PropPath':['activationSpecTemplateProps']},#Ref0050\
				   ]

#########################################################################################################
# Creates a report table of properties and adds the table to rptParms
# If a given configuration element does not have a properties attribute, a report is not generated.
#########################################################################################################
def reportProperties(rptParms):
	cu.printMsg('reportProperties => '+ str(rptParms), True)
	global PropertyAttributes
	servers=rptParms['ServerList']
	clusterDict = {}
	configIDs = [] #Ref0022
	for propAttr in PropertyAttributes:
		names=[]
		for server in servers:
			serverDict = {}
			clusterDict.update({server:serverDict})
			try:
				config=cu.getConfigFromPath([server]+rptParms['ConfigPath']+propAttr['PropPath'])
				props = config[propAttr['PropName']]
				if cu.isConfigID(props):
					props=cu.stringListAsList(props)
					for prop in props:
						found = False
						try:
							for name in names:
								if name == cu.MasterDict[prop]['name']:
									found = True
							if not found:
								names.append(cu.MasterDict[prop]['name'])
							value = 'present but null'
							try:
								value = cu.MasterDict[prop]['value']
							except:
								value = 'present but null'
							serverDict.update({cu.MasterDict[prop]['name']:value})
							if configIDs.count(cu.MasterDict[prop]['CONFIG_ID']) == 0:				#Ref0022
								configIDs.append(cu.MasterDict[prop]['CONFIG_ID'])					#Ref0022
						except KeyError as ke:
							#print 'KeyError ' + str(ke)
							None
						except:
							#print "Unexpected error:", sys.exc_info()[0]
							None
			except KeyError as ke:
				#print 'KeyError ' + str(ke)
				continue
			except:
				cu.printException('Excpetion in reportProperties',sys.exc_info())
				continue
		if len(names) > 0:
			names = sorted(names, key=str.lower)
			tableData=[]
			match=[]
			for name in names:
				row=[]
				for server in servers:
					if server == 'NOT_FOUND':
						row.append('Interceptor not configured in domain')
					else:
						try:
							row.append(clusterDict[server][name])
						except:
							row.append('property not set')
				match.append(cu.listElementsMatch(row))
				tableData.append(row)
			propsDict = {'RowHeaders':names,'TableData':tableData,'Match':match,'Title':propAttr['PropName'] + ' for ' + rptParms['Title'],\
			             'FirstColumnHeader':propAttr['PropName'],'ConfigIDs':configIDs,'Type':'Properties'}  #Ref0022
			rptParms['Tables'].append(propsDict)

#########################################################################################################
# Creates a report table of attributes and adds the table to rptParms
#########################################################################################################
def reportConfigElementAttrList(rptParms):
	cu.printMsg('reportConfigElementAttrList => '+str(rptParms), True)
	rptParms['Attributes']=cu.PropertiesDict[rptParms['ReportName']+':attributes'].split(',')
	attrs=rptParms['Attributes']
	path=rptParms['ConfigPath']
	servers=rptParms['ServerList']
	attrTable=[]
	match=[]
	tableData=[]
	columnHeaders=[]
	rowHeaders=[]
	configIDs=[]  #Ref0022
	
	for server in servers:
		if 'ColumnHeaderFunc' not in rptParms:
			columnHeaders.append(cu.MasterDict[server]['name']+' ('+cu.getConfigIDNode(server)+', '+cu.getConfigIDCell(server)+')' )
		else:
			columnHeaders.append(rptParms['ColumnHeaderFunc'](server))
	for attr in attrs:
		attrVals = []
		for server in servers:
			config = {}
			try:
				config=cu.getConfigFromPath([server]+path)
				if configIDs.count(config['CONFIG_ID']) == 0:					#Ref0022
					configIDs.append(config['CONFIG_ID'])			#Ref0022
			except KeyError as ke:
				#printMsg('ERROR: ' + str(ke),False)
				None
			if len(config.keys()) == 0:
				attrVals.append('configuration not defined')
			else:
				if attr in config.keys():
					attrVals.append(config[attr])
				else:
					attrVals.append('attribute not set')
		attrSet=False
		for val in attrVals:
			if val.find(' not ') == -1:
				attrSet=True
				break
		if attrSet:
			rowHeaders.append(attr)
			match.append(cu.listElementsMatch(attrVals))
			tableData.append(attrVals)
	attrDict = {'RowHeaders':rowHeaders,'TableData':tableData,'Match':match,'Title':rptParms['Title'],'FirstColumnHeader':'Attribute',\
	            'ConfigIDs':configIDs,'Type':'Attributes'}  #Ref0022
	rptParms['ColumnHeaders']=columnHeaders
	if 'Tables' in rptParms.keys():
		rptParms['Tables'].append(attrDict)
	else:
		rptParms['Tables']=[attrDict]

#########################################################################################################
# Creates a report table for the PMI stat provider configuration and adds it to rptParms
#########################################################################################################
def reportPMIStatProviders(rptParms):
	cu.printMsg('reportPMIConfig => '+str(rptParms), True)
	servers=rptParms['ServerList']
	pmiModuleNames=cu.PropertiesDict['pmiModuleReport.statProviders'].split(',')
	tableData=[]
	match=[]
	rowHaeaders=[]
	configIDs = []  #Ref0022
	for name in pmiModuleNames:
		row=[]
		for server in servers:
			row.append(cu.getPMICellValue(cu.getPMIConfig(name,server)))
			#print '1: %s' % cu.getPMIConfig(name,server)
			#configIDs.append(cu.getPMIConfig(name,server)['CONFIG_ID'])  #Ref0022
		if not len(row) == row.count('not configured'):
			rowHaeaders.append(name)
			match.append(cu.listElementsMatch(row))
			tableData.append(row)
	pmiDict = {'RowHeaders':rowHaeaders,'TableData':tableData,'Match':match,'Title':'PMI Stats Providers','FirstColumnHeader':'Module Name',\
			   'ConfigIDs':configIDs,'Type':'PMI'}  #Ref0022
	rptParms['Tables'].append(pmiDict)

#########################################################################################################
# Creates a report table for the PMI stat group configuration and adds it to rptParms
#########################################################################################################
def reportPMIStatGroups(rptParms):
	cu.printMsg('reportPMIStatGroups => '+str(rptParms), True)
	servers=rptParms['ServerList']
	pmiModuleNames=cu.PropertiesDict['pmiModuleReport.statGroup'].split(',')
	tableData=[]
	match=[]
	rowHaeaders=[]
	configIDs = []  #Ref0022
	for name in pmiModuleNames:
		row=[]
		for server in servers:
			config=cu.getPMIConfig(name,server)
			cellValue = 'not configured'
			if config.has_key('pmimodules'):
				cellValue=[]
				pmiMods=cu.stringListAsList(config['pmimodules'])
				for pmiMod in pmiMods:
					cellValue.append(cu.MasterDict[pmiMod]['moduleName'])
				cellValue.sort()
				cellValue = str(cellValue)[1:-1].strip()
			row.append(cellValue)
		if not len(row) == row.count('not configured'):
			rowHaeaders.append(name)
			match.append(cu.listElementsMatch(row))
			tableData.append(row)
	pmiDict = {'RowHeaders':rowHaeaders,'TableData':tableData,'Match':match,'Title':'PMI Stats Groups','FirstColumnHeader':'Stat Group Name',\
			   'ConfigIDs':configIDs,'Type':'Attributes'}  #Ref0022
	rptParms['Tables'].append(pmiDict)


#########################################################################################################
# Most configuration elements have a a single set of attributes and possibly properties.
# This is a convenience function that generates a report based on that criteria.
#########################################################################################################
def reportConfiguration(rptParms):
	cu.printMsg('reportConfiguration => '+str(rptParms), True)
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	cu.reportWrite(rptParms)

#########################################################################################################
# Generates a report of JVM attributes, system properties, JVM arguments,  and 
#########################################################################################################
def jvmReportSrv(serverList):
	cu.printMsg('jvmReportSrv => '+ str(serverList), True)
	configPath = ['processDefinitions->JavaProcessDef_','jvmEntries->JavaVirtualMachine_']
	rptParms = {'Title':'JVM Configuration','ServerList':serverList,'ReportName':'jvmReportSrv','ConfigPath':configPath}
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	reportJvmArguments(rptParms)
	cu.reportWrite(rptParms)

#########################################################################################################
# Generates a report of the JVM process definition
#########################################################################################################
def processDefinitionReportSrv(serverList):
	cu.printMsg('processDefinitionReportSrv => '+ str(serverList), True)
	configPath = ['processDefinitions->JavaProcessDef_']
	rptParms = {'Title':'Process Definition','ServerList':serverList,'ReportName':'processDefinitionReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the JVM execution config
#########################################################################################################
def processExecutionReportSrv(serverList):
	cu.printMsg('processExecutionReportSrv => '+ str(serverList), True)
	configPath = ['processDefinitions->JavaProcessDef_','execution']
	rptParms = {'Title':'Process Execution','ServerList':serverList,'ReportName':'processExecutionReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the monitoring policy for servers
#########################################################################################################
def processMonitoringPolicyReportSrv(serverList):
	cu.printMsg('processMonitoringPolicyReportSrv => '+ str(serverList), True)
	configPath = ['processDefinitions->JavaProcessDef_','monitoringPolicy']
	rptParms = {'Title':'Process Monitoring Policy','ServerList':serverList,'ReportName':'processMonitoringPolicyReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the trace service config for servers
#########################################################################################################
def traceServiceReportSrv(serverList):
	cu.printMsg('traceServiceReportSrv => '+ str(serverList), True)
	configPath = ['services->TraceService_']
	rptParms = {'Title':'Trace Service Configuration','ServerList':serverList,'ReportName':'traceServiceReportSrv','ConfigPath':configPath}
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['services->TraceService_','traceLog']
	rptParms['Title'] = 'Trace log'
	rptParms['ReportName'] = 'traceLogSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	cu.reportWrite(rptParms)

#########################################################################################################
# Generates a report of the NCSA access log config for servers
#########################################################################################################
def httpAccessLogServiceReportSrv(serverList):
	cu.printMsg('httpAccessLogServiceReportSrv => '+ str(serverList), True)
	configPath = ['services->HTTPAccessLoggingService_']
	rptParms = {'Title':'HTTP Access Log Service','ServerList':serverList,'ReportName':'httpAccessLogServiceReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the Transaction Service
#########################################################################################################
def transactionServiceReportSrv(serverList):
	cu.printMsg('transactionServiceReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','services->TransactionService_']
	rptParms = {'Title':'Transaction Service','ServerList':serverList,'ReportName':'transactionServiceReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the trace service config for servers
#########################################################################################################
def ejbContainerSrv(serverList):
	cu.printMsg('ejbContainerSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','components->EJBContainer_']
	rptParms = {'Title':'EJB Container','ServerList':serverList,'ReportName':'ejbContainerSrv','ConfigPath':configPath}
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','components->EJBContainer_','cacheSettings']
	rptParms['Title'] = 'EJB Cache Settings'
	rptParms['ReportName'] = 'ejbCacheSrv'
	reportConfigElementAttrList(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','components->EJBContainer_','services->MessageListenerService_']
	rptParms['Title'] = 'Messenge Listener Service'
	rptParms['ReportName'] = 'messageListenerServiceSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','components->EJBContainer_','services->MessageListenerService_','threadPool']
	rptParms['Title'] = 'Messenge Listener Service Thread Pool'
	rptParms['ReportName'] = 'threadPoolSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','components->EJBContainer_','timerSettings']
	rptParms['Title'] = 'EJB Timer Settings'
	rptParms['ReportName'] = 'ejBTimerSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = [{'function':cu.getDataFromConfigPath,'args':['components->ApplicationServer_','components->EJBContainer_','timerSettings']}]
	rptParms['Title'] = 'EJB Timer DataSource'
	rptParms['ReportName'] = 'dataSourceRsc'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = [{'function':cu.getDataFromConfigPath,'args':['components->ApplicationServer_','components->EJBContainer_','timerSettings']},'provider']
	rptParms['Title'] = 'EJB Timer DataSource Provider'
	rptParms['ReportName'] = 'providerReportRsc'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = [{'function':cu.getDataFromConfigPath,'args':['components->ApplicationServer_','components->EJBContainer_','timerSettings']},'relationalResourceAdapter']
	rptParms['Title'] = 'EJB Timer DataSource Relational Resource Adapter'
	rptParms['ReportName'] = 'resourceAdapterRsc'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	cu.reportWrite(rptParms)

# Generates a report of the ORB service for servers
#########################################################################################################
def orbServiceReportSrv(serverList):
	cu.printMsg('orbServiceReportSrv => '+ str(serverList), True)
	configPath = ['services->ObjectRequestBroker_']
	rptParms = {'Title':'ORB','ServerList':serverList,'ReportName':'orbServiceReportSrv','ConfigPath':configPath}
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['services->ObjectRequestBroker_','threadPool']
	rptParms['Title'] = 'ORB Thread Pool'
	rptParms['ReportName'] = 'threadPoolSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	cu.reportWrite(rptParms)

#########################################################################################################
# Generates a report of the web container config for servers
#########################################################################################################
def webContainerReportSrv(serverList):
	cu.printMsg('webContainerReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','components->WebContainer_']
	rptParms = {'Title':'Web Container','ServerList':serverList,'ReportName':'webContainerReportSrv','ConfigPath':configPath}
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['services->ThreadPoolManager_','threadPools->WebContainer']
	rptParms['Title'] = 'Web Container Thread Pool'
	rptParms['ReportName'] = 'threadPoolSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	cu.reportWrite(rptParms)

#########################################################################################################
# Generates a report of the web container thread pool for servers
#########################################################################################################
def webContainerThreadPoolReportSrv(serverList):
	cu.printMsg('threadPoolSrv => '+ str(serverList), True)
	configPath = ['services->ThreadPoolManager_','threadPools->WebContainer']
	rptParms = {'Title':'Web Container Thread Pool','ServerList':serverList,'ReportName':'threadPoolSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the server class loading policies
#########################################################################################################
def applicationServerReportSrv(serverList):
	cu.printMsg('applicationServerReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_']
	rptParms = {'Title':'Application Server','ServerList':serverList,'ReportName':'applicationServerReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the server class loading policies
#########################################################################################################
def httpPluginReportSrv(serverList):
	cu.printMsg('httpPluginReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','webserverPluginSettings']
	rptParms = {'Title':'HTTP Plugin settings','ServerList':serverList,'ReportName':'httpPluginReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the monitoring policy for servers
#########################################################################################################
def sessionManagerReportSrv(serverList):
	cu.printMsg('sessionManagerReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','components->WebContainer_','services->SessionManager_']
	rptParms = {'Title':'Session Manager Configuration','ServerList':serverList,'ReportName':'sessionManagerReportSrv','ConfigPath':configPath}
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','components->WebContainer_','services->SessionManager_','defaultCookieSettings']
	rptParms['Title'] = 'Session Default Cookie Settings'
	rptParms['ReportName'] = 'defaultCookieSettingsSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','components->WebContainer_','services->SessionManager_','tuningParams']
	rptParms['Title'] = 'Session Manager Tuning Parameters'
	rptParms['ReportName'] = 'sessionManagerTuningParmsReportSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','components->WebContainer_','services->SessionManager_','tuningParams','invalidationSchedule']
	rptParms['Title'] = 'Session Manager Invalidation Schedule'
	rptParms['ReportName'] = 'sessionInvalidationScheduleReportSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','components->WebContainer_','services->SessionManager_','sessionDatabasePersistence']
	rptParms['Title'] = 'Session Database Persistence'
	rptParms['ReportName'] = 'sessionDBPersistenceReportSrv'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = [{'function':cu.getDataFromConfigPath,'args':['components->ApplicationServer_','components->WebContainer_',\
	                           'services->SessionManager_','sessionDatabasePersistence']}]
	rptParms['Title'] = 'Session DataSource'
	rptParms['ReportName'] = 'dataSourceRsc'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = [{'function':cu.getDataFromConfigPath,'args':['components->ApplicationServer_','components->WebContainer_',\
	                           'services->SessionManager_','sessionDatabasePersistence']},'provider']
	rptParms['Title'] = 'Session DataSource Provider'
	rptParms['ReportName'] = 'providerReportRsc'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = [{'function':cu.getDataFromConfigPath,'args':['components->ApplicationServer_','components->WebContainer_',\
	                           'services->SessionManager_','sessionDatabasePersistence']},'relationalResourceAdapter']
	rptParms['Title'] = 'Session DataSource Relational Resource Adapter'
	rptParms['ReportName'] = 'resourceAdapterRsc'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	cu.reportWrite(rptParms)

#########################################################################################################
# Generates a report of the dynacache config (only base cache and memory cache)
#########################################################################################################
def dynamicCacheReportSrv(serverList):
	cu.printMsg('dynamicCacheReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','services->DynamicCache']
	rptParms = {'Title':'Dynamic Cache','ServerList':serverList,'ReportName':'dynamicCacheReportSrv','ConfigPath':configPath}
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','services->DynamicCache','diskCacheCustomPerformanceSettings']
	rptParms['Title'] = 'Disk Cache Custom Performance Settings'
	rptParms['ReportName'] = 'diskCacheCustomPerformanceSettingsRsc'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	rptParms['ConfigPath'] = ['components->ApplicationServer_','services->DynamicCache','diskCacheEvictionPolicy']
	rptParms['Title'] = 'Disk Cache Eviction Policies'
	rptParms['ReportName'] = 'diskCacheEvictionPolicyRsc'
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	cu.reportWrite(rptParms)

#########################################################################################################
# Generates a report of the PMI config for servers
#########################################################################################################
def pmiServiceReportSrv(serverList):
	cu.printMsg('pmiServiceReportSrv => '+ str(serverList), True)
	configPath = ['services->PMIService_']
	rptParms = {'Title':'PMI Configuration','ServerList':serverList,'ReportName':'pmiServiceReportSrv','ConfigPath':configPath}
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	reportPMIStatProviders(rptParms)
	reportPMIStatGroups(rptParms)
	cu.reportWrite(rptParms)

#########################################################################################################
# Generates a report of the monitoring policy for servers
#########################################################################################################
def sipContainerReportSrv(serverList):
	cu.printMsg('sipContainerReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','components->SIPContainer_']
	rptParms = {'Title':'SIP Container','ServerList':serverList,'ReportName':'sipContainerReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the SIP stack config for servers
#########################################################################################################
def sipStackReportSrv(serverList):
	cu.printMsg('sipStackReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','components->SIPContainer_','stack']
	rptParms = {'Title':'SIP Stack','ServerList':serverList,'ReportName':'sipStackReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of SIP timers for servers
#########################################################################################################
def sipTimersReportSrv(serverList):
	cu.printMsg('sipTimersReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','components->SIPContainer_','stack','timers']
	rptParms = {'Title':'SIP Timers','ServerList':serverList,'ReportName':'sipTimersReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the portlet container for servers
#########################################################################################################
def portletContainerReportSrv(serverList):
	cu.printMsg('portletContainerReportSrv => '+ str(serverList), True)
	configPath = ['components->ApplicationServer_','components->PortletContainer_']
	rptParms = {'Title':'Portlet Container','ServerList':serverList,'ReportName':'portletContainerReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the file transfer service for the node agent of the servers 
#########################################################################################################
def fileTransferServiceReportSrv(serverList):
	cu.printMsg('fileTransferServiceReportSrv => '+ str(serverList), True)
	configPath = ['components->NodeAgent_','fileTransferService'] #Ref0012
	rptParms = {'Title':'File Transfer Service','ServerList':serverList,'ReportName':'fileTransferServiceReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of the file synchronization service for the node agent of the servers 
#########################################################################################################
def fileSynchServiceReportSrv(serverList):
	cu.printMsg('fileSynchServiceReportSrv => '+ str(serverList), True)
	configPath = ['components->NodeAgent_','fileSynchronizationService'] #Ref0012
	rptParms = {'Title':'File Synchronization Service','ServerList':serverList,'ReportName':'fileSynchServiceReportSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)

#########################################################################################################
# Generates a report of transport channel services and related transport chains
#########################################################################################################
def reportTransportChannelServiceSrv(serverList):
	cu.printMsg('reportTransportChannelService => '+ str(serverList), True)
	configPath = ['services->TransportChannelService_']
	rptParms = {'Title':'Transport Channel Service','ServerList':serverList,'ReportName':'reportTransportChannelServiceSrv','ConfigPath':configPath}
	reportConfiguration(rptParms)
	#Get all Transport Chains
	chains=[]
	#get path elements for server transport chains
	for server in serverList:
		srvChains=''
		try:
			srvChains = cu.stringListAsList(cu.getConfigFromPath([server]+configPath)['chains'])
		except:
			cu.printMsg('WARNING: chains not present in '+ str([server]+configPath), False)
		for chain in srvChains:
			chain=chain.split('(')[0]
			if not chain in chains:
				chains.append(chain)
	chains.sort()
	for chain in chains:
		rptParms['Tables']=[]
		enableRow=[]
		channelRow=[]
		channelList=[]
		for server in serverList:
			configPath=[server,'services->TransportChannelService_','chains->'+chain]
			config=cu.getConfigFromPath(configPath)
			if len(config.keys()) == 0:
				enableRow.append('configuration not defined')
				channelRow.append('configuration not defined')
			else:
				enableRow.append(config['enable'])
				channels=cu.stringListAsList(config['transportChannels'])
				channelCell=''
				for channel in channels:
					channel=channel.split('(')[0]
					channel=channel[:channel.rfind('_')]
					channelCell=channelCell+channel+', '
					if not channel in channelList:
						channelList.append(channel)
				channelRow.append(channelCell[:-2])
		match = [cu.listElementsMatch(enableRow),cu.listElementsMatch(channelRow)]
		tableData = [enableRow,channelRow]
		chainDict={'RowHeaders':['enable','transportChannels'],'Match':match,'Title':'Transport chain: '+chain,'FirstColumnHeader':'Attribute','TableData':tableData}
		rptParms['Tables'].append(chainDict)
		for channel in channelList:
			configPath=['services->TransportChannelService_','chains->'+chain,'transportChannels->'+channel]
			#define transport channel specific attributes
			rptParms.update({'Title':'Channel '+channel,'ServerList':serverList,'ReportName':'reportTransportChannelChainSrv','ConfigPath':configPath})
			reportConfigElementAttrList(rptParms)
			reportProperties(rptParms)
		cu.reportWrite(rptParms)

#Ref0004 Begin
#########################################################################################################
# Resolves variables to the value for the specific server.
#########################################################################################################
def variablesReport(serverList):
	variableNameList = cu.getVariableNames()
	rptParms = {'ColumnHeaders':serverList,'Title':'WebSphere Variables','ReportList':'variablesReport'}
	tableData = []
	match = []
	rowHeaders = []
	configIDs = []  #Ref0022
	title = 'Variable name<br> (Note, variables that have no value for all servers are omitted.)'
	for variableName in variableNameList:
		rowData = []
		append = False
		for server in serverList:
			value = cu.resolveVariable(variableName,server)
			rowData.append(value)
			if len(value) > 0 and not value == "[]":
				append = True
		if append:
			tableData.append(rowData)
			match.append(cu.listElementsMatch(rowData))
			rowHeaders.append(variableName)
	tableDict = {'RowHeaders':rowHeaders,'Match':match,'FirstColumnHeader':title,'TableData':tableData,'Title':'WebSphere Variables', \
				 'ConfigIDs':configIDs,'Type':'Variables'}  #Ref0022
	rptParms['Tables'] = [tableDict]
	cu.reportWrite(rptParms)
#Ref0004 End

#Ref0013 Begin
#########################################################################################################
# Compares the threas pool manager and all thread pools
#########################################################################################################
def threadPoolManagerSrv(serverList):
	cu.printMsg('threadPoolManagerSrv => '+ str(serverList), True)
	configPath = ['services->ThreadPoolManager_']
	rptParms = {'Title':'Thread Pool Manager','ServerList':serverList,'ReportName':'threadPoolManagerSrv','ConfigPath':configPath}
	reportConfigElementAttrList(rptParms)
	reportProperties(rptParms)
	srvDict = {}
	threadPoolNames = []
	for server in serverList:
		threadPoolList = cu.getConfigFromPath([server,'services->ThreadPoolManager_'])['threadPools']
		threadPoolList = cu.stringListAsList(threadPoolList)
		for threadPool in threadPoolList:
			name = cu.MasterDict[threadPool]['name']
			if threadPoolNames.count(name) == 0:
				threadPoolNames.append(name)
		#srvDict['%s::%s' % (threadPool['name'],server)] = threadPool
	threadPoolNames.sort()
	for threadPoolName in threadPoolNames:
		rptParms['ConfigPath'] = ['services->ThreadPoolManager_','threadPools::name::%s' % threadPoolName]
		rptParms['Title'] = 'Thread Pool %s' % threadPoolName
		rptParms['ReportName'] = 'threadPoolSrv'
		reportConfigElementAttrList(rptParms)
		reportProperties(rptParms)
	cu.reportWrite(rptParms)
	cu.printMsg('threadPoolManagerSrv <= '+ str(serverList), True)
#Ref0013 End

#Ref0015 Begin
def getSSLConfigCipherList(configID):
	rtnVal = ''
	try:
		rtnVal = cu.getConfigFromPath([configID,'setting'])['enabledCiphers']
		if rtnVal[0] == '"':
			rtnVal = rtnVal[1:-1]
		if rtnVal[0] == '[':
			rtnVal = rtnVal[1:-1]
		rtnVal = rtnVal.split()
	except:
		None
	return rtnVal

#########################################################################################################
# Detailed ciphers report indicating mismattched cipher selections.  
#########################################################################################################
def ciphersReport(rptParms):
	sslConfigs = rptParms['ServerList']
	allCiphers = []
	for sslConfig in sslConfigs:
		ciphers = getSSLConfigCipherList(sslConfig)
		for cipher in ciphers:
			if allCiphers.count(cipher) == 0:
				allCiphers.append(cipher)
	allCiphers.sort()
	tableData = []
	for cipher in allCiphers:
		rowData = []
		for sslConfig in sslConfigs:
			ciphers = getSSLConfigCipherList(sslConfig)
			if ciphers.count(cipher) > 0:
				rowData.append('present')
			else:
				rowData.append('not present')
		tableData.append(rowData)
	
	match=[]
	for row in tableData:
		match.append(cu.listElementsMatch(row))
	ciphersDict = {'RowHeaders':allCiphers,'TableData':tableData,'Match':match,'Title':'Enabled Ciphers','FirstColumnHeader':'cipher'} #Ref0034
	rptParms['Tables'].append(ciphersDict)
#Ref0015 End

#########################################################################################################
# Executes all server centric reports
#########################################################################################################
def ServerReport(report,propsDict):                                                                      #Ref0025
	cu.printMsg('Running server report ' + report,False)
	serverList=[]
	propertiesDict = cu.PropertiesDict #Ref0025
	if not propsDict == None:          #Ref0025
		propertiesDict = propsDict     #Ref0025
	clusterPropList = cu.getAllPropKeys(report+':Clusters:',propertiesDict)  #Ref0043
	serverPropList=cu.getAllPropKeys(report+':Servers:',propertiesDict)      #Ref0043
	clusterLookup=False
	for propList in [serverPropList,clusterPropList]:                        #Ref0043
		for prop in propList:
			prop = prop.strip()
			value = propertiesDict[prop].split('::')   #Ref0025
			if len(value) > 1:
				if clusterLookup:
					configIDs = cu.getClusterConfigIDs(value[0],value[1])
					#print configIDs
					for configID in configIDs:
						srvList = cu.getClusterServerList(configID)
						#BUGBUG Likely the cluster logic is returning servers from multiple cells. 
						for srv in srvList:
							if serverList.count(srv) == 0:
								serverList.append(srv)
				else:
					if len(value) == 2:
						value.insert(1,".*")
					serverList = serverList + cu.getServerConfigIDs(value[0],value[1],value[2])
		clusterLookup=True
	#print serverList
	#sys.exit(2)
	
	if len(serverList) == 0:
		cu.printMsg('ERROR: no servers found for the report.' ,False)
		return
	serverList = cu.sortByCellAndScope(serverList,cu.getNameAndScopeSort,'name') #Ref0015
	cu.printMsg('Server list:',False)
	for server in serverList:
		cu.printMsg('\t\t'+cu.MasterDict[server]['name']+" Cell: "+server.split("/")[1]+" Node: "+server.split("/")[3],False)

	subReports = [['JVM',jvmReportSrv],\
				 ['Process Definition',processDefinitionReportSrv],\
				 ['Process Execution',processExecutionReportSrv],\
				  ['Process Monitoring Policy',processMonitoringPolicyReportSrv],\
				  ['Web Container',webContainerReportSrv],\
				  ['HTTP Plugin',httpPluginReportSrv],\
				  ['Application Server',applicationServerReportSrv],\
				  ['Session Management',sessionManagerReportSrv],\
				  ['SIP Container',sipContainerReportSrv],\
				  ['SIP Stack',sipStackReportSrv],\
				  ['SIP Timer',sipTimersReportSrv],\
				  ['Portlet Container',portletContainerReportSrv],\
				  ['Dynamic Cache',dynamicCacheReportSrv],\
				  ['EJB Container', ejbContainerSrv],\
				  ['Transaction Service',transactionServiceReportSrv],\
				  ['ORB',orbServiceReportSrv],\
				  ['PMI',pmiServiceReportSrv],\
				  ['Trace Service',traceServiceReportSrv],\
				  ['HTTP Access Log Service',httpAccessLogServiceReportSrv],\
				  ['Thread Pool Manager',threadPoolManagerSrv],\
				  ['WebSphere Variable Substitutions',variablesReport],\
#ref0012		  ['File Transfer Service',fileTransferServiceReportSrv],\
#ref0012		  ['File Synchronization Service',fileSynchServiceReportSrv],\
				  ['Tranport Channels',reportTransportChannelServiceSrv]]
	cu.reportInitialize(propertiesDict[report+':Title'],propertiesDict[report+':FileName'])

	runReportList = ['All']                                                 #Ref0041
	try:                                                                  #Ref0041
		runReportList = propertiesDict[report+':ReportList'].split(',')   #Ref0041
	except:                                                               #Ref0041
		None                                                              #Ref0041
	for subReport in subReports:
		run = False
		for runReport in runReportList:
			if str(subReport[1]).find(runReport) > -1 or runReport == 'All':
				run = True
				break
		if run:
			cu.printMsg('Running '+subReport[0],False)
			subReport[1](serverList)
		else:
			cu.printMsg('Skipping '+subReport[0],False)
	cu.reportFinalize()

#Begin Ref0012
#########################################################################################################
# Executes all node agent reports
#########################################################################################################
def NodeAgentReport():
	cu.printMsg('Running node agent report',False)
	serverList = cu.getNodeAgentConfigIDs()
	
	if len(serverList) == 0:
		cu.printMsg('ERROR: no node agents found for the report.' ,False)
		return
	serverList = cu.sortByCellAndScope(serverList,cu.getNameAndScopeSort,'name') #Ref0015
	cu.printMsg('Server list:',False)
	for server in serverList:
		cu.printMsg('\t\t'+cu.MasterDict[server]['name']+" Cell: "+server.split("/")[1]+" Node: "+server.split("/")[3],False)

	subReports = [['JVM',jvmReportSrv],\
				 ['Process Definition',processDefinitionReportSrv],\
				 ['Process Execution',processExecutionReportSrv],\
				  ['File Transfer Service',fileTransferServiceReportSrv],\
				  ['File Synchronization Service',fileSynchServiceReportSrv],\
				  ['ORB',orbServiceReportSrv],\
				  ['PMI',pmiServiceReportSrv],\
				  ['Trace Service',traceServiceReportSrv],\
				  ['Thread Pool Manager',threadPoolManagerSrv],\
				  ['WebSphere Variable Substitutions',variablesReport],\
				  ['Tranport Channels',reportTransportChannelServiceSrv]]
	cu.reportInitialize('Node Agents','NodeAgent')

	for subReport in subReports:
		cu.printMsg('Running '+subReport[0],False)
		subReport[1](serverList)
	cu.reportFinalize()
#End Ref0012

#########################################################################################################
# Generates the Cell summary report
#########################################################################################################
def CellSummaryReport():
	cu.printMsg('Generating cell summary report',False)
	reports = [['Application Servers','/.*\#Server_.*','name',True,['serverType','APPLICATION_SERVER']],#Ref0008\ 
			   ['Web Servers','/.*\#Server_.*','name',True,['serverType','WEB_SERVER']],#Ref0008\ 
	           ['Clusters','/.*\#ServerCluster_.*','name',False],\
			   ['Virtual Hosts','.*VirtualHost_.*','name',False],\
			   ['Core Groups','.*CoreGroup_.*','name',False],\
			   ['Data Sources','.*DataSource_.*','name',True],\
			   ['JMS Providers','.*JMSProvider_.*','name',True],\
			   ['J2C Resource Adapters','.*J2CResourceAdapter_.*','name',True],\
			   ['SSL Configs','.*SSLConfig_.*','alias',True],\
			   ['Mail Providers','.*MailProvider_.*','name',True],\
			   ['URL Providers','.*URLProvider_.*','name',True],\
			   ['JDBC Providers','.*JDBCProvider_.*','name',True],\
			   ['Service Integration Buses','.*SIBus_.*','name',False],\
			   ['Application Deployments','.*ApplicationDeployment_.*','binariesURL',False],\
			   ['Servlet Cache Instances','.*ServletCacheInstance_.*','name',True],\
			   ['Object Cache Instances','.*ObjectCacheInstance_.*','name',True],\
			   ]
	cu.reportInitialize('Cell Summary Report','Summary')
	columnHeaders=cu.getCellNames(cu.MasterDict)
	rowHeaders=[]
	tableData=[]
	for report in reports:
		cu.printMsg('\t'+ report[0],False)
		list=[]
		rowHeaders.append(report[0])
		for cell in columnHeaders:
			elements=[]
			configIDs = cu.findConfigIDs('.*/'+cell+report[1],True,cu.MasterDict)
			for configID in configIDs:
				#Begin Ref0008
				if len(report) == 5:
					if not cu.MasterDict[configID][report[4][0]] == report[4][1]:
						continue
				#End Ref0008
				value = cu.MasterDict[configID][report[2]]
				reportScope = report[3]
				if reportScope:
					scope = cu.getScope(configID)
					value = value + '<br>&nbsp;&nbsp;&nbsp;<font size="1">'+scope+'<font size="3">'
				elements.append(value)
			if len(elements) > 0:
				elements.sort()
			list.append(cu.listToString(elements,'\n'))
		tableData.append(list)
	#Setup report dictionaries
	tables={'Title':'Cell Summary','RowHeaders':rowHeaders,'TableData':tableData,'FirstColumnHeader':'',\
		   'MatchColumn':'ignore','EncodeHTML':False}
	rptParms={'ColumnHeaders':columnHeaders,'Tables':[tables],'MatchColumn':'ignore'}
	cu.reportWrite(rptParms)
	cu.reportFinalize()

#########################################################################################################
# 
#########################################################################################################
#BUGBUG This list should be places in ConfigReportAttributes.properties and not hard coded
def getResourceReportDefinitions():
	return {\
	'DataSource': [{'Title':'Data Source','ReportName':'dataSourceRsc','ConfigPath':[]},\
					{'Title':'Data Source Connection Pool','ReportName':'connectionPoolRsc','ConfigPath':['connectionPool']},\
					{'Title':'Data Source Provider','ReportName':'providerReportRsc','ConfigPath':['provider']},\
					{'Title':'Data Source Relational Resource Adpter','ReportName':'resourceAdapterRsc','ConfigPath':['relationalResourceAdapter']},\
					{'Title':'Data Source Relational Resource Adpter Connector','ReportName':'connectorRsc',\
						'ConfigPath':['relationalResourceAdapter','deploymentDescriptor']}\
					],\
	'J2CResourceAdapter':[{'Title':'J2C Resource Adapter','ReportName':'resourceAdapterRsc','ConfigPath':[]},\
						 {'Title':'J2C Resource Adpter Connector','ReportName':'connectorRsc',\
							'ConfigPath':['deploymentDescriptor']}\
							],\
	'JDBCProvider':[{'Title':'JDBC Provider','ReportName':'jdbcProviderRsc','ConfigPath':[]}],\
	'SIBus':[{'Title':'Service Integration Bus','ReportName':'sibRsc','ConfigPath':[]}],\
	'ObjectCacheInstance':[{'Title':'Object Cache','ReportName':'objectCacheRsc','ConfigPath':[]},\
						  {'Title':'Cache Provider','ReportName':'cacheProviderRsc','ConfigPath':['provider']}\
						  ],\
	'ServletCacheInstance':[{'Title':'Servlet Cache','ReportName':'objectCacheRsc','ConfigPath':[]},\
							{'Title':'Cache Provider','ReportName':'cacheProviderRsc','ConfigPath':['provider']},\
							{'Title':'Disk Cache custom Performance Settings','ReportName':'diskCacheCustomPerformanceSettingsRsc',\
								'ConfigPath':['diskCacheCustomPerformanceSettings']},\
							{'Title':'Disk Cache Eviction Policy','ReportName':'diskCacheEvictionPolicyRsc','ConfigPath':['diskCacheEvictionPolicy']}\
							],\
	'Security':[{'Title':'Global Security','ReportName':'securityRsc','ConfigPath':[]},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound','ReportName':'csiv2Rsc','ConfigPath':['CSI','claims']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound ID assertion','ReportName':'csiv2idAssertRsc','ConfigPath':['CSI','claims','layers->IdentityAssertionLayer_']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound ID assertion QOP','ReportName':'csiv2idAssertQOPRsc','ConfigPath':['CSI','claims','layers->IdentityAssertionLayer_','supportedQOP']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound Message','ReportName':'csiv2MessageRsc','ConfigPath':['CSI','claims','layers->MessageLayer_']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound Message supported QOP','ReportName':'csiv2MessageQOPRsc','ConfigPath':['CSI','claims','layers->MessageLayer_','supportedQOP']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound Message required QOP','ReportName':'csiv2MessageQOPRsc','ConfigPath':['CSI','claims','layers->MessageLayer_','requiredQOP']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound Transport','ReportName':'csiv2TransportRsc','ConfigPath':['CSI','claims','layers->TransportLayer_']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound Transport Server Authentication','ReportName':'csiv2TransportSrvSAuthRsc','ConfigPath':['CSI','claims','layers->TransportLayer_','serverAuthentication']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound Transport supported QOP','ReportName':'csiv2TransportQOPRsc','ConfigPath':['CSI','claims','layers->TransportLayer_','supportedQOP']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Inbound Transport required QOP','ReportName':'csiv2TransportQOPRsc','ConfigPath':['CSI','claims','layers->TransportLayer_','requiredQOP']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound','ReportName':'csiv2Rsc','ConfigPath':['CSI','performs']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound ID assertion','ReportName':'csiv2idAssertRsc','ConfigPath':['CSI','performs','layers->IdentityAssertionLayer_']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound ID assertion QOP','ReportName':'csiv2idAssertQOPRsc','ConfigPath':['CSI','performs','layers->IdentityAssertionLayer_','supportedQOP']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound Message','ReportName':'csiv2MessageRsc','ConfigPath':['CSI','performs','layers->MessageLayer_']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound Message supported QOP','ReportName':'csiv2MessageQOPRsc','ConfigPath':['CSI','performs','layers->MessageLayer_','supportedQOP']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound Message required QOP','ReportName':'csiv2MessageQOPRsc','ConfigPath':['CSI','performs','layers->MessageLayer_','requiredQOP']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound Transport','ReportName':'csiv2TransportRsc','ConfigPath':['CSI','performs','layers->TransportLayer_']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound Transport Server Authentication','ReportName':'csiv2TransportSrvSAuthRsc','ConfigPath':['CSI','performs','layers->TransportLayer_','serverAuthentication']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound Transport supported QOP','ReportName':'csiv2TransportQOPRsc','ConfigPath':['CSI','performs','layers->TransportLayer_','supportedQOP']},\
			   {'Title':'Cell Default Common Secure Interoperability (CSI) Outbound Transport required QOP','ReportName':'csiv2TransportQOPRsc','ConfigPath':['CSI','performs','layers->TransportLayer_','requiredQOP']},\
			   {'Title':'Certificate Expiration Monitor','ReportName':'certExpMonitorRsc','ConfigPath':['wsCertificateExpirationMonitor']},\
			   {'Title':'Certificate Expiration Monitor Notification','ReportName':'notificationRsc','ConfigPath':['wsCertificateExpirationMonitor','wsNotification']},\
			   {'Title':'Certificate Expiration Monitor Scedule','ReportName':'scheduleRsc','ConfigPath':['wsCertificateExpirationMonitor','wsSchedule']},\
			   ],\
#Begin Ref0015
#	'SSLConfig' : [{'Title':'SSL settings','ReportName':'sslConfigRsc','ConfigPath':[]},\
	'SSLConfig' : [{'Title':'SSL settings','ReportName':'sslConfig1Rsc','ConfigPath':['setting']},\
			      {'Title':'Ciphers','ReportName':'ciphers','ConfigPath':['setting','trustStore'],'ReportFunc':ciphersReport},\
			      {'Title':'Trust Store','ReportName':'keyStoreRsc','ConfigPath':['setting','trustStore']},\
			      {'Title':'Key Store','ReportName':'keyStoreRsc','ConfigPath':['setting','keyStore']},\
			      {'Title':'Trust Manager','ReportName':'trustManagerRsc','ConfigPath':['setting','trustManager']},\
			      {'Title':'Key Manager','ReportName':'keyManagerRsc','ConfigPath':['setting','keyManager']},\
			   ],\
#End Ref0015
#Begin Ref0018
	'ResourceEnvironmentProvider':[{'Title':'Resource Environment Provider','ReportName':'rscEnvProviderRsc','ConfigPath':[]}], \
	'ResourceEnvEntry':[{'Title':'Resource Environment Entry','ReportName':'rscEnvEntryRsc','ConfigPath':[]},\
	                    {'Title':'Referencable','ReportName':'referencableRsc','ConfigPath':['referenceable']},\
	                    {'Title':'Resource Environment Provider','ReportName':'rscEnvProviderRsc','ConfigPath':['provider']},\
	], \
#End Ref0018
#Begin Ref0021
	'Application':[{'Title':'Application Deployment','ReportName':'applicationDeployment','ConfigPath':[]},\
	               {'Title':'Application Deployment Classloader','ReportName':'applicationClassloader','ConfigPath':['classloader']},\
	], \
	'ApplicationModules':[{'Title':'Application Module','ReportName':'applicationDeployment','ConfigPath':['modules']},\
	], \
#End Ref0021
#Begin Ref0045
	'JMSProvider':[{'Title':'JMS Provider','ReportName':'jmsProviderRsc','ConfigPath':[]},\
	], \
#End Ref0045
#Begin Ref0046
	'GenericJMSConnectionFactory':[{'Title':'JMS Connectioin Factory','ReportName':'genericJMSConnectionFactoryRsc','ConfigPath':[]},\
								   {'Title':'Session Pool','ReportName':'connectionPoolRsc','ConfigPath':['sessionPool']},\
								   {'Title':'JMS Provider','ReportName':'jmsProviderRsc','ConfigPath':['provider']},\
								   {'Title':'Connection Pool','ReportName':'connectionPoolRsc','ConfigPath':['connectionPool']},\
								   {'Title':'JAAS Mapping','ReportName':'mappingModuleRsc','ConfigPath':['mapping']}\
								  ],\
#End Ref0046
#Begin Ref0047
	'GenericJMSDestination':[{'Title':'JMS Destination','ReportName':'genericJMSDestinationRsc','ConfigPath':[]},\
							 {'Title':'JMS Provider','ReportName':'jmsProviderRsc','ConfigPath':['provider']},\
							],\
#End Ref0047
#Begin Ref0048
	'J2CActivationSpec':[{'Title':'J2C Activation Specification','ReportName':'j2cActivationSpecRsc','ConfigPath':[]},\
						 {'Title':'Activation Specification','ReportName':'activationSpecRsc','ConfigPath':['activationSpec']},\
						],\
#End Ref0048
#Begin Ref0048
	'JAASAuthData':[{'Title':'JAAS Alias','ReportName':'jaasAuthDataRsc','ConfigPath':[]},\
	], \
#End Ref0048
	}  

def hasNoName(resourceType):
	list = ['Security']
	return list.count(resourceType) > 0
	
def getNameAttribute(reportType):
	rtnVal = 'name'
	if reportType == 'SSLConfig' or reportType == 'JAASAuthData': #Ref0049
		rtnVal = 'alias'
	return rtnVal

#########################################################################################################
# Generates the resource reports (Data Sources, Resource Adapters, etc.
#########################################################################################################
def ResourceReport(report):
	reportType = cu.PropertiesDict[report+':ReportType']
	reportTitle = cu.PropertiesDict[report+':Title']
	cu.printMsg('Generating report ' + reportTitle,False)
	resourceReports = {}

	resourcePropList=cu.getAllPropKeys(report+':Resources:',None)  #Ref0025

	resourceReports = getResourceReportDefinitions()
	resources = []
	columnHeaderFunc = cu.getNameAndScope
	if reportType == 'Security':
		columnHeaderFunc = cu.getScope
		resources = cu.findConfigIDs('.*'+reportType+'_.*', True, cu.MasterDict)
	else:
		nameAttr = getNameAttribute(reportType) #Ref0015
		scopePropList=cu.getAllPropKeys(report+':Scope:',None)  #Ref0025
		if not len(resourcePropList) == len(scopePropList):
			cu.printMsg('Resources do not match scopes for report '+report,False)
			return
		for idx in range(0, len(scopePropList)):
			scope=cu.PropertiesDict[scopePropList[idx]]
			propID=scopePropList[idx].split(':')[len(scopePropList[idx].split(':'))-1]
			resourceElements=cu.PropertiesDict[report+':Resources:'+propID].split('::')
			if scope == 'Cluster':
				if not len(resourceElements) == 3:
					cu.printMsg('Invalid resources specification for scope Cluster in report '+report,False)
					return
			elif scope == 'Cell':
				if not len(resourceElements) == 2:
					cu.printMsg('Invalid resources specification for scope Cell in report '+report,False)
					return
			elif scope == 'Node':
				if not len(resourceElements) == 3:
					cu.printMsg('Invalid resources specification for scope Node in report '+report,False)
					return
			elif scope == 'Server':
				if not len(resourceElements) == 4:
					cu.printMsg('Invalid resources specification for scope Server in report '+report,False)
					return
			elif scope == 'Application':
				if not len(resourceElements) == 3:
					cu.printMsg('Invalid resources specification for scope Application in report '+report,False)
					return
			else:
				cu.printMsg('Invalid scope "'+scope+'" in report '+report,False)
				return

		for idx in range(0, len(scopePropList)):
			scope=cu.PropertiesDict[scopePropList[idx]]
			propID=scopePropList[idx].split(':')[len(scopePropList[idx].split(':'))-1]
			resourceElements=cu.PropertiesDict[report+':Resources:'+propID].split('::')
			#Begin Ref0015
			if reportType == 'SSLConfig':
				if ['Cell','Node','Server'].count(scope) == 0 :
					cu.printMsg('Invalid scope "'+scope+'" in report '+report,False)
					return
				else:
					sslConfigs = cu.findConfigIDs(".*SSLConfig_.*",True,cu.MasterDict)
					for sslConfig in sslConfigs:
						mgmtScopeType = cu.getConfigFromPath([sslConfig,'managementScope'])['scopeType']
						if scope.lower() == mgmtScopeType and \
						   re.match(resourceElements[len(resourceElements)-1],cu.MasterDict[sslConfig]['alias']):
							mgmtScopeElements = cu.getConfigFromPath([sslConfig,'managementScope'])['scopeName'].split(':')
							match = True
							for idx1 in range(0,len(resourceElements)-1):
								if not re.match(resourceElements[idx1],mgmtScopeElements[idx1*2+1]):
									match = False
									break
							if match:
								resources.append(sslConfig)
			else:
			#End Ref0015
				if scope == 'Cluster':
					resources = resources + cu.getConfigIDsByAttrValueFromDict('.*cells/'+resourceElements[0]+'/clusters/'+resourceElements[1]+reportType+'_.*',\
																	  resourceElements[2],nameAttr,False,cu.MasterDict) #Ref0015
				elif scope == 'Cell':
					resources = resources + cu.getConfigIDsByAttrValueFromDict('.*cells/'+resourceElements[0]+reportType+'_.*',\
																	  resourceElements[1],nameAttr,False,cu.MasterDict) #Ref0015
				elif scope == 'Node':
					resources = resources + cu.getConfigIDsByAttrValueFromDict('.*cells/'+resourceElements[0]+'/nodes/'+resourceElements[1]+reportType+'_.*',\
																	  resourceElements[2],nameAttr,False,cu.MasterDict) #Ref0015
				elif scope == 'Server':
					resources = resources + cu.getConfigIDsByAttrValueFromDict('.*cells/'+resourceElements[0]+'/nodes/'+resourceElements[1]+'/servers/'+resourceElements[2]+reportType+'_.*',\
																	  resourceElements[3],nameAttr,False,cu.MasterDict) #Ref0015
				elif scope == 'Application':
					resources = resources + cu.getConfigIDsByAttrValueFromDict('.*cells/'+resourceElements[0]+'/applications/'+resourceElements[1]+'/deployments/.*'+reportType+'_.*',\
																	  resourceElements[2],nameAttr,False,cu.MasterDict) #Ref0015
				else:
					cu.printMsg('Invalid scope "'+scope+'" in report '+report,False)
					return

	if len(resources) == 0:
		cu.printMsg('ERROR: no resources found for the report.' ,False)
		return
	cu.printMsg(reportType + ' list:',False)
	for resource in resources:
		cu.printMsg('\t\t'+cu.MasterDict[resource][nameAttr],False) #Ref0015

	cu.reportInitialize(reportTitle,cu.PropertiesDict[report+':FileName'])

	rptParms={'ServerList':resources,'ColumnHeaderFunc':columnHeaderFunc}
	for resourceReport in resourceReports[reportType]:
		rptParms['ConfigPath'] = resourceReport['ConfigPath']
		rptParms['Title'] = resourceReport['Title']
		rptParms['ReportName'] = resourceReport['ReportName']
		try:                                         #Ref0015
			resourceReport['ReportFunc'](rptParms)   #Ref0015
		except KeyError:                             #Ref0015
			reportConfigElementAttrList(rptParms)
			reportProperties(rptParms)
		except:                                                              #Ref0015
			cu.printException('Exception in ResourceReport',sys.exc_info())  #Ref0015
			
	cu.reportWrite(rptParms)
	cu.reportFinalize()

#########################################################################################################
# This report finds all resources by the same name and generates reports on them
#########################################################################################################
def reportAllResourcesByName():
	resourceTypes=['Security','SSLConfig','DataSource','J2CResourceAdapter','JDBCProvider','ObjectCacheInstance','ServletCacheInstance','SIBus',\
				   'ResourceEnvironmentProvider','ResourceEnvEntry','JMSProvider','GenericJMSConnectionFactory','GenericJMSDestination', #Ref0015 #Ref0018 #Ref0045 #Ref0046 #Ref0047 \
				   'J2CActivationSpec','JAASAuthData'] #Ref0048 #Ref0049
	resourceReports = getResourceReportDefinitions()
	global ReportOnlyMismatched
	originalReportOnlyMismatched = cu.ReportOnlyMismatched
	loopParmsList = [['true',' with attribute values that don\'t match',' with attribute values that do not match only','NotMatched'],\
					 ['false','','','']]
	for loopParms in loopParmsList:
		ReportOnlyMismatched = loopParms[0]
		messageSuffix = loopParms[1]
		titleSuffix = loopParms[2]
		fileNameSuffix = loopParms[3]
		cu.reportInitialize('Singleton resources and resources compared by name%s' % titleSuffix,'Resources%s' % fileNameSuffix)
		cu.printMsg('Generating report of all of the following resource types by resource name%s: %s' % \
					(messageSuffix,str(resourceTypes)),False)
		for resourceType in resourceTypes:
			cu.printMsg('\tGenerating reports for ' + resourceType,False)
			names = []
			if hasNoName(resourceType):
				names = [resourceType]
			else:
				names = cu.getUniqueConfigAttrValues(resourceType,getNameAttribute(resourceType))
			for name in names:
				cu.printMsg('\t\tGenerating report for ' + name,False)
				rptParms = {}
				if hasNoName(resourceType):
					resources = cu.findConfigIDs('.*'+re.escape('#'+resourceType+'_')+'.*', True, cu.MasterDict)
					resources = cu.sortByCellAndScope(resources,cu.getScopeSort,None) #Ref0015
					rptParms={'ServerList':resources,'ColumnHeaderFunc':cu.getScope}
				else:
					nameAttr = getNameAttribute(resourceType) #Ref0015
					list = []
					resources = cu.getConfigIDsByAttrValueFromDict('.*'+re.escape('#'+resourceType+'_')+'.*',re.escape(name),nameAttr,False,cu.MasterDict) #Ref0015
					for resource in resources:
						if cu.MasterDict[resource][nameAttr] == name:  #Ref0015
							list.append(resource)
							list = cu.sortByCellAndScope(list,cu.getNameAndScopeSort,nameAttr) #Ref0015
					rptParms={'ServerList':list,'ColumnHeaderFunc':cu.getNameAndScope}
				for resourceReport in resourceReports[resourceType]:
					rptParms['ConfigPath'] = resourceReport['ConfigPath']
					if hasNoName(resourceType):
						rptParms['Title'] = resourceReport['Title']
					else:
						rptParms['Title'] = '%s (%s)' % (resourceReport['Title'],name)
					rptParms['ReportName'] = resourceReport['ReportName']
					try:                                         #Ref0015
						resourceReport['ReportFunc'](rptParms)   #Ref0015
					except KeyError:                             #Ref0015
#						cu.Debug=True
#						cu.printException('Exception in ResourceReport',sys.exc_info())  #Ref0015
#						cu.Debug=False
						reportConfigElementAttrList(rptParms)
						reportProperties(rptParms)
					except:                                                              #Ref0015
						cu.printException('Exception in ResourceReport',sys.exc_info())  #Ref0015
				cu.reportWrite(rptParms)
		cu.reportFinalize()
	cu.ReportOnlyMismatched = originalReportOnlyMismatched

#Ref0021 Begin
#########################################################################################################
# Returns the columnn header for Application reports.
#########################################################################################################
def ApplicationDeploymentReportColumnHeader(configID):
	cellName = configID.split('/')[1]
	binaryName = cu.MasterDict[configID]['binariesURL']
	return '%s Cell: %s' % (binaryName,cellName)

#########################################################################################################
# Reports configurations for application modules.
#########################################################################################################
def ApplicationModulesReport(rptParms):
	appConfigIDs = rptParms['ServerList']
	binaries = []
	for appConfigID in appConfigIDs:
		modConfigIDs = cu.stringListAsList1(cu.MasterDict[appConfigID]['modules'])
		for modConfigID in modConfigIDs:
			binary = cu.MasterDict[modConfigID]['uri']
			if binaries.count(binary) == 0:
				binaries.append(binary)
		binaries.sort()

	for binary in binaries:
		rptParms['ConfigPath'] = ['modules::uri::%s' % binary]
		rptParms['Title'] = 'Module %s' % binary
		rptParms['ReportName'] = 'applicationModules'
		reportConfigElementAttrList(rptParms)
		reportProperties(rptParms)

#########################################################################################################
# Generatres a user defined application report.
#########################################################################################################
def ApplicationDeploymentReport(report):
	appReports = getResourceReportDefinitions()['Application']
	reportTitle = cu.PropertiesDict[report+':Title']
	global ReportOnlyMismatched
	applicationSearchList = cu.getAllPropKeys(report+':Archive:',None)  #Ref0025
	appConfigIDList = []
	cu.printMsg('Generating report ' + reportTitle,False)

	for searchItem in applicationSearchList:
		apps = cu.getConfigIDsByAttrValueFromDict('.*#ApplicationDeployment_.*',"/"+cu.PropertiesDict[searchItem],'binariesURL',False,cu.MasterDict)
		appConfigIDList = appConfigIDList + apps
	
	if len(appConfigIDList) == 0 :
		cu.printMsg("ERROR: No applicatioins found for report " + report,False)
	else:
		cu.printMsg('Application List:',False)
		for configID in appConfigIDList:
			cu.printMsg('\t%s' % ApplicationDeploymentReportColumnHeader(configID),False)
		rptParms={'ServerList':appConfigIDList,'ColumnHeaderFunc':ApplicationDeploymentReportColumnHeader}
		for appReport in appReports:
			rptParms['ConfigPath'] = appReport['ConfigPath']
			rptParms['Title'] = appReport['Title']
			rptParms['ReportName'] = appReport['ReportName']
			try:
				reportConfigElementAttrList(rptParms)
				reportProperties(rptParms)
			except:
				cu.printException('Exception in ApplicationDeploymentReport',sys.exc_info())


		ApplicationModulesReport(rptParms)
		
		cu.reportInitialize(reportTitle,cu.PropertiesDict[report+':FileName'])
		cu.reportWrite(rptParms)
		cu.reportFinalize()
		
#########################################################################################################
# Compares all application configurations using the same binary name with each other.
#########################################################################################################
def ApplicationsReport(report):
	appReports = getResourceReportDefinitions()['Application']
	appConfigIDs = cu.findConfigIDs('.*#ApplicationDeployment_.*',True,None)
	appBinaryList = []
	for configID in appConfigIDs:
		binaryName = cu.MasterDict[configID]['binariesURL'].split('/')
		binaryName = binaryName[len(binaryName)-1]
		if appBinaryList.count(binaryName) == 0:
			appBinaryList.append(binaryName)
	appBinaryList.sort()
	
	cu.reportInitialize('Aplications compared by name.','Applications')
	for appBinary in appBinaryList:
		cu.printMsg('Generating report for:' + appBinary,False)
		appConfigIDs = cu.getConfigIDsByAttrValueFromDict('.*#ApplicationDeployment_.*',"/"+re.escape(appBinary),'binariesURL',False,cu.MasterDict)
		for configID in appConfigIDs:
			cu.printMsg('\t%s' % ApplicationDeploymentReportColumnHeader(configID),False)
		rptParms={'ServerList':appConfigIDs,'ColumnHeaderFunc':ApplicationDeploymentReportColumnHeader}
		for appReport in appReports:
			rptParms['ConfigPath'] = appReport['ConfigPath']
			rptParms['Title'] = '%s (%s) ' % (appReport['Title'],appBinary)
			rptParms['ReportName'] = appReport['ReportName']
			try:
				reportConfigElementAttrList(rptParms)
				reportProperties(rptParms)
			except:
				cu.printException('Exception in ApplicationDeploymentReport',sys.exc_info())
		ApplicationModulesReport(rptParms)
		cu.reportWrite(rptParms)

	cu.reportFinalize()

#Ref0021 End

#Ref0025 Begin
#########################################################################################################
# Compares all application configurations using the same binary name with each other.
#########################################################################################################
def ClustersReport():
	cu.printMsg('Clusters found for server cluster report:',False)
	configIDs = cu.findConfigIDs('.*\#ServerCluster_.*',True,cu.MasterDict)
	clusters = []
	for configID in configIDs:
		name = cu.MasterDict[configID]['name']
		cell = cu.getConfigIDCell(configID)
		if clusters.count(name) == 0:
			clusters.append(name)
			cu.printMsg('\tName: %s' % (name),False)
	for cluster in clusters:
		props = {'%s:ReportType' % cluster:'Server',\
				 '%s:Title' % cluster:'Cluster: %s' % cluster,\
				 '%s:Clusters:1' % cluster:'.*::%s' % cluster,\
				 '%s:ReportList' % cluster:'All' ,\
				 '%s:FileName' % cluster:'Cluster-%s' % cluster}
		ServerReport(cluster,props)

#Ref0025 End

#Ref0028 Begin
#########################################################################################################
# Compares all TAIs by the same class and domain with each other.  
#########################################################################################################
def TrustAssociationReport():
	configIDs = cu.findConfigIDs('.*\#TrustAssociation_.*',True,cu.MasterDict)
	configIDs.sort()
	cells = cu.getCellNames(cu.MasterDict)
	cells.sort()
	domains = []
	for configID in configIDs:
		domain = getSecDomain(configID)
		if not domain in domains:
			domains.append(domain)
	domains.remove('Global')
	domains.insert(0,'Global')
	
	cu.reportInitialize('Trust Association Report.','TrustAssociation')

	rptParms = {'ColumnHeaders':cells,'Tables':[]}
	rowHaeaders = ['enabled','interceptors']
	interceptorClasses = []
	for domain in domains:
		enabledRow = []
		interceptorRow = []
		for cell in cells:
			configID = getTAConfigID(domain,cell)
			if len(configID) == 0:
				enabledRow.append('Security Domain not present')
				interceptorRow.append('Security Domain not present')
			else:
				enabledRow.append(cu.MasterDict[configID]['enabled'])
				interceptors = cu.stringListAsList(cu.MasterDict[configID]['interceptors'])
				interceptorStr = ''
				for interceptor in interceptors:
					interceptorClass = cu.MasterDict[interceptor]['interceptorClassName']
					interceptorStr = '%s%s<br>------------<br>' % (interceptorStr,interceptorClass)
					if not interceptorClass in interceptorClasses:
						interceptorClasses.append(interceptorClass)
				if len(interceptorStr) > 4:
					interceptorStr = interceptorStr[:-20]
				interceptorRow.append(interceptorStr)
		table = {'Title' : 'Trust Association configuration for %s domain' % domain,\
				 'Type':'Attributes',#Ref0033\ 
				 'ConfigIDs':configIDs,#Ref0033\ 
				 'RowHeaders' : rowHaeaders,\
				 'FirstColumnHeader' : 'Attribute',\
				 'TableData' : [enabledRow,interceptorRow],\
				 'EncodeHTML' : False,\
				 'Match' : [cu.listElementsMatch(enabledRow),cu.listElementsMatch(interceptorRow)]}
		rptParms['Tables'].append(table)
	cu.reportWrite(rptParms)

	interceptorClasses.sort()
	for domain in domains:
		rptParms = {'ColumnHeaders':cells,'Tables':[],'ConfigPath':[]}
		for interceptorClass in interceptorClasses:
			rptParms['ServerList'] = []
			rptParms['Title'] = 'interceptor %s and domain %s' % (interceptorClass,domain)
			for cell in cells:
				configID = getTAIConfigID(domain,cell,interceptorClass)
				if len(configID) == 0:
					configID = '<<IGNORE>>'
				rptParms['ServerList'].append(configID)
			reportProperties(rptParms)
		cu.reportWrite(rptParms)	
		
	cu.reportFinalize()
	
	
def getSecDomain(configID):
	domain = 'Global'
	if configID.find('(waspolicies') == 0:
		idx = configID.find('|')
		fields = configID[:idx].split('/')
		domain = fields[len(fields)-1]
	return domain

def getTAConfigID(domain,cell):
	if domain == 'Global':
		return cu.findConfigIDs('\(cells\/%s\|.*\#TrustAssociation\_' % re.escape(cell),False,None)
	else:
		idx = cell.rfind('-') + 1
		return cu.findConfigIDs('\(waspolicies\/default\-%s\/securitydomains\/%s\|.*\#TrustAssociation\_' % \
		                       (re.escape(cell[idx:]),re.escape(domain)),False,None)

def getTAIConfigID(domain,cell,classname):
	if domain == 'Global':
		return cu.getConfigIDsByAttrValueFromDict('\(cells\/%s\|.*\#TAInterceptor\_' % re.escape(cell),\
												  classname,\
												  'interceptorClassName',\
												  True,\
												  cu.MasterDict)
	else:
		idx = cell.rfind('-') + 1
		return cu.getConfigIDsByAttrValueFromDict('\(waspolicies\/default\-%s\/securitydomains\/%s\|.*\#TAInterceptor\_' % \
												  (re.escape(cell[idx:]),re.escape(domain)),\
												  classname,\
												  'interceptorClassName',\
												  True,\
												  cu.MasterDict)
#Ref0028 End


# [Tables] = List of output table dictionaries (see below)
# [ColumnHeaders] = Column headers for output tables

# [Title] = The title of this table report
# [RowHeaders] = The row headers for the table
# [TableData] = A list of lists.  Each list contains an entry for each server for the specific header.
# [Match] = Indicates is all values in the corresponding row are equal.  "ignore" indicates to omit the match column
# [FirstColumnHeader] = Title for the attributes or properties for the table

#########################################################################################################
#########################################################################################################
# Execution logic begins here 
#########################################################################################################
#########################################################################################################
if len(sys.argv) == 2 and (sys.argv[1].find('?') > -1 or sys.argv[1].upper().find('HELP') > -1): #Ref0051
	print 'Syntax:'
	print '  python '+ sys.argv[0] + ' arg1 arg2 arg3 ...'
	print '    Where arg is either'
	print '      a properties file name'
	print '    or'
	print '      a property in the form of PropertyName=PropertyValue'
	sys.exit(0)

cu.printMsg('Begin run.',False)

propIdx = 0
if sys.argv[0].find('.py') > 0:
	propIdx = 1

cu.readProperties(sys.argv[propIdx:],ScriptPath) #Ref0011

#Get configurations 
cu.readConfigs()


#Run other defined reports
reportList='All'
try:                                                        #Ref0041
	reportList = cu.PropertiesDict['ReportList'].strip()    #Ref0041
except:                                                     #Ref0041
	None                                                    #Ref0041
builtInReports = ['Summary','Resources','NodeAgent','Applications','Clusters','TrustAssociation'] #Ref0025 Ref0028
userReportProps = cu.getAllPropKeys('.*:ReportType',None)  #Ref0025 #Ref0040
userReports = []                                                                                                               #Ref0040
for report in userReportProps:                                                                                                 #Ref0040
	userReports.append(report.split(':')[0])                                                                                   #Ref0040
userReports.sort()                                                                                                             #Ref0040
for report in userReports:                                                                                                     #Ref0040
	if report in builtInReports:                                                                                               #Ref0040
		cu.printMsg('ERROR: Report name %s is identical to a built in report name.  Please change the name.' % report,False)   #Ref0040 
		sys.exit(1)                                                                                                            #Ref0040

if len(reportList) > 0:
	reports = []
	if reportList == 'All':
		reports = builtInReports + userReports #Ref0025 #Ref0040
	else:
		reports = reportList.split(',')
		reports.sort()
	cu.printMsg('Running the following reports:',False)
	for report in reports:
		cu.printMsg('\t%s' % report,False)
	for report in reports:
		report = report.strip()
		reportType = ''
		cu.setReportOnlyMismatched(report) #Ref0010
		cu.setOutputScripts(report) #Ref0022
		if builtInReports.count(report) > 0: #Ref0025
			reportType = report
		else:
			try:
				reportType = cu.PropertiesDict[report+':ReportType']
			except:
				cu.printException('Report attribute ReportType for report %s missing.'  % report,sys.exc_info())
				continue
		cu.printMsg('===== Begin Report. Name: %s =====' % report,False)
		if reportType == 'Summary':
			CellSummaryReport()
		elif reportType == 'Resources':
			reportAllResourcesByName()
		elif reportType == 'Server':
			ServerReport(report,None)
		elif reportType == 'NodeAgent':  #Ref0012
			NodeAgentReport()            #Ref0012
		elif reportType == 'Clusters':   #Ref0025
			ClustersReport()             #Ref0025
		elif reportType == 'TrustAssociation': #Ref0028
			TrustAssociationReport()           #Ref0028
		elif reportType == 'DataSource':
			ResourceReport(report)
		elif reportType == 'J2CResourceAdapter':
			ResourceReport(report)
		elif reportType == 'JDBCProvider':
			ResourceReport(report)
		elif reportType == 'ObjectCacheInstance':
			ResourceReport(report)
		elif reportType == 'ServletCacheInstance':
			ResourceReport(report)
		elif reportType == 'SIBus':
			ResourceReport(report)
		elif reportType == 'Security':
			ResourceReport(report) 
		elif reportType == 'SSLConfig':  #Ref0015
			ResourceReport(report)       #Ref0015
		elif reportType == 'ResourceEnvironmentProvider':  #Ref0018
			ResourceReport(report)                         #Ref0018
		elif reportType == 'ResourceEnvEntry':             #Ref0018
			ResourceReport(report)                         #Ref0018
		elif reportType == 'Applications':                 #Ref0021
			ApplicationsReport(report)            		   #Ref0021
		elif reportType == 'ApplicationDeployment':        #Ref0021
			ApplicationDeploymentReport(report)            #Ref0021
		elif reportType == 'JMSProvider':                  #Ref0045
			ResourceReport(report)                         #Ref0045
		elif reportType == 'GenericJMSConnectionFactory':  #Ref0046
			ResourceReport(report)                         #Ref0046
		elif reportType == 'GenericJMSDestination':        #Ref0047
			ResourceReport(report)                         #Ref0047
		elif reportType == 'J2CActivationSpec':            #Ref0048
			ResourceReport(report)                         #Ref0048
		elif reportType == 'JAASAuthData':                 #Ref0049
			ResourceReport(report)                         #Ref0049
		else:
			cu.printMsg('ERROR: Invalid report type: ' + reportType,False)
		cu.printMsg('===== End Report. Name: %s =====' % report,False)

cu.printMsg('End run.',False)
