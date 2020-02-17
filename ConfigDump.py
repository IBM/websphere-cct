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
# This script dumps out the majority of a server or cell configuration in a text format 
# for use with ConfigReport.py to compare configurations.
##########################################################################################
# Change history:
# Date        Ref  Who  Comments
# 2018/01/17  0001 DWR  Added logic to handle unsupported configuration types.
# 2018/01/19  0002 DWR  Added logic to handle systems where the environment is not present.
# 2018/06/16  0015 DWR  Collect all SSL config info.  
# 2019/01/30  0026 DWR  Using AdminConfig.types() to get configuration elements instead of hard coded list
# 2019/08/19  0037 DWR  Adding command line setting of CellSuffix
# 2019/08/19  0038 DWR  Limiting data gathered to specificed scope(s)
# 2020/01/09  0044 DWR  Added command line syntax to exclude collection specific objec types
#

import sys
import os

#Ref0002 Begin
def printException(msg,exceptionInfo):
	for line in exceptionInfo:
		msg=msg+'\n'+str(line)
	print 'ERROR: ' + msg

#Load libraries from where the path they are installed.
path = None
try:
	path = os.getenv('IBM_JAVA_COMMAND_LINE')
	path=path[path.find("-f") + 2:].strip()
	path=path.split(' ')[0]
	if path.find(os.sep) > -1:
		path=path.split(' ')[0]
		path=path[:path.rfind(os.sep)+1]
	else:
		path = ''
except:
	printException('Could not get command line from environment.',sys.exc_info())

sys.path.append(path)
try:
	import ConfigUtils as cu
except:
	printException('Failed to load support scripts.',sys.exc_info())
#Ref0002 End

#########################################################################################################
#########################################################################################################
# Gets configuration data from the repository
#########################################################################################################
#########################################################################################################
True=1
False=0

#Ref0002 Begin
try: 
	cu.printMsg('Begin run.',False)
except:
	print 'ERROR, cannot continue.  Failed to load support scripts.  Run wsadmin -f ConfigDump.py from the same directory it exists in.'
	sys.exit(1)

excludeTypeList = []  #Ref0044
regexList=[]  #Ref0038
if len(sys.argv) > 0:
	if " ".join(sys.argv).find("=") == -1: #Ref0038 
		cu.setRepositoryConfigFileName(sys.argv[0])
		#Ref0002 End
		if len(sys.argv) > 1:              #Ref0037
			cu.setCellSuffix(sys.argv[1])  #Ref0037
	#Ref0038 Begin
	else:
		for arg in sys.argv:
			if arg.find("="):
				parm = arg.split('=')[0]
				value = arg.split('=')[1]
				if parm == 'file':
					cu.setRepositoryConfigFileName(value)
				elif parm == 'suffix':
					cu.setCellSuffix(sys.argv[1])
				elif parm == 'excludeType':            #Ref0044
					excludeTypeList = value.split(',') #Ref0044
				else:
					regexList.append('.*%ss/%s[/|].*' % (parm,value))
			else:
				print('ERROR: Invalid parameter: %s' % arg)
	#Ref0038 End

# configElementList = [['Getting cluster configuration ','ServerCluster'],\
					 # ['Getting server configuration ','Server'],\
					 # ['Getting PMI configuration ','PMIModule'],\
					 # ['Getting Global Security configuration ','Security'],\
					 # ['Getting Security Domain configuration ','SecurityDomain'],\
					 # ['Getting SSL configuration ','SSLConfig'],  #Ref0015 \
					 # ['Getting Authorization Table ','AuthorizationTableExt'],\
					 # ['Getting Audit configuration ','Audit'],\
					 # ['Getting cell configuration ','Cell'],\
					 # ['Getting Core Group configuration ','CoreGroup'],\
					 # ['Getting Core Group Bridge configuration ','CoreGroupBridgeSettings'],\
					 # ['Getting cell variables ','VariableMap'],\
					 # ['Getting Virtual Host configuration ','VirtualHost'],\
					 # ['Getting cell Web Services Security configuration ','WSSecurity'],\
					 # ['Getting Object Pool Provider configuration ','ObjectPoolProvider'],\
					 # ['Getting Work Manager Provider configuration ','WorkManagerProvider'],\
					 # ['Getting Schedular Provider configuration ','SchedulerProvider'],\
					 # ['Getting JMS Provider configuration ','JMSProvider'],\
					 # ['Getting J2C Resource Adapter configuration ','J2CResourceAdapter'],\
					 # ['Getting Mail Provider configuration ','MailProvider'],\
					 # ['Getting URL Provider configuration ','URLProvider'],\
					 # ['Getting JDBC Provider configuration ','JDBCProvider'],\
					 # ['Getting Resource Environment Provider configuration ','ResourceEnvironmentProvider'],\
					 # ['Getting Data Source configuration ','DataSource'],\
					 # ['Getting Service Inigration Bus configuration ','SIBus'],\
					 # ['Getting JAX RPC handler configuration ','JAXRPCHandler'],\
					 # ['Getting Servlet Cache Instance configuration ','ServletCacheInstance'],\
					 # ['Getting Object Cache Instance configuration ','ObjectCacheInstance'],\
					 # ['Getting SIB configuration ','SIBus'],\
					 # ['Getting SIB WS Security Request Consumer Binding configuration ','SIBWSSecurityRequestConsumerBindingConfig'],\
					 # ['Getting SIB WS Security Request Generator Binding configuration ','SIBWSSecurityRequestGeneratorBindingConfig'],\
					 # ['Getting SIB WS Security Response Consumer Binding configuration ','SIBWSSecurityResponseConsumerBindingConfig'],\
					 # ['Getting SIB WS Security Response Generator Binding configuration ','SIBWSSecurityResponseGeneratorBindingConfig'],\
					 # ['Getting Application Deployment configuration ','ApplicationDeployment'],\
					 # ['Getting Resource Environment Providers','ResourceEnvironmentProvider'],\
					 # ['Getting Resource Environment Entries','ResourceEnvEntry'],\
					 # ]
configElementList = []
for type in AdminConfig.types('.*').splitlines():
	if excludeTypeList.count(type) == 0:    #Ref0044
		configElementList.append(type)
	else:                                                                #Ref0044
		cu.printMsg('Excluding configuration elements of type %s' % type,False) #Ref0044

for regex in regexList:                                              #Ref0038
	cu.printMsg('Filtering out configuration elements matching %s' % regex,False) #Ref0038	

#Ref0001 Moved logic into ConfigUtils.py
cu.getConfigElements(configElementList,AdminConfig,regexList) #Ref0038
#Ref0001 End
cu.writeRepositoryFile()


cu.printMsg('End run.',False)
cu.printMsg('Ignore the WASX7146I and WASX7309W messages.  No modifications to the repository were made so AdminConfig.save() was not invoked.',False)

print AdminConfig.queryChanges()
