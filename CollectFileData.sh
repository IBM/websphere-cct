#!/bin/bash
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
# Copyright IBM 2019 all rights reserved.
#
# Change history:
# Date        Who  Comments
# 2019/08/06  DWR  Added support for AIX istat
# 2019/08/06  DWR  Adressed div by zero error with less than ten files found
# 2019/08/07  DWR  Addressed files with embedded spaces.  
# 

if [ -z "$1" ]; then
	echo "Syntax: $0 [DIRECTORY] [OUTPUT_FILE]"
	echo "   DIRECTORY the directory to recursively collect file date/time/CRC information from"
	echo "   OUTPUT_FILE the file to write file data to"
	exit
	fi

directory=$1
outputFile=$2
if [ -z "$2" ]; then
	dateStr=`date +"%Y%m%d.%H%M%S"`
	outputFile="file-list.$dateStr.txt"
	fi

niceCmd="nice -n10"
statCmd=`which stat 2>nul`
if [ -z "$statCmd" ]; then
		statCmd=`which istat 2> nul`
		if [ -z "$statCmd" ]; then
			echo "AIX utilities found, using istat."
			fi
	else
		echo "GNU utilities found, using stat."
	fi
if [ -z "$statCmd" ]; then
	echo "Neither stat nor istat found.  File date/time comparisons cannot be done."
	fi

###############################################################################
# Get file last modified time/date and CRC
###############################################################################
echo "Getting last modification date and cksum for files.  This may take several minutes."
files=`$niceCmd find $directory -type f|grep -v /workarea/` 
numFiles=`echo $files|wc -w`
numFilesDiv10=$(($numFiles / 10))
if [ $numFilesDiv10 -eq 0 ]; then
	numFilesDiv10=1
	fi
echo "$numFiles files found."
count=0
while read -r file; do
	crc=`$niceCmd cksum "$file"|cut -f 1,2 -d" " 2>nul`
	if [ -z "$statCmd" ]; then
		date=""
	else
		date=`$niceCmd $statCmd "$file" 2>nul|grep  "odif"`
	fi
	echo "$date|$crc|$file" >> $outputFile
	count=$(($count+1))
	if [ $(($count % $numFilesDiv10)) -eq 0 ]; then
		echo "$(($count * 100 / $numFiles))% done."
		fi
	done <<< "$files"

