#!/usr/bin/env python

import sys, time, os, traceback
import json
import re
from datetime import *; 
from dateutil.relativedelta import *
import dateutil.parser

#input_file = open('heartbeat_with_av_zscore','r')

WALKER_FILE_PATTERN = "to_process"

class FileLineWrapper(object):
    def __init__(self, f):
        self.f = f
        self.lineNum = 0
    def close(self):
        return self.f.close()
    def readline(self):
        self.lineNum += 1
        return self.f.readline()

# Get all log files in current dir recursively
def getCurrFiles():
    #return [f for f in os.listdir('.') if os.path.isfile(f)]
    logFiles = []
    for dirpath, _, files in os.walk('./'):
        for logFile in files:
            if logFile.startswith(WALKER_FILE_PATTERN):
                logFiles.append(os.path.abspath(os.path.join(dirpath, logFile)))

    return logFiles

def process_json(lineNum, lineString):
    parsed_json = json.loads(lineString)
    #event = parsed_json['d']
    #raw = event['heartbeat']
    #av = event['av']
    #zscore = event['zscore']
    #return [raw, av, zscore]
    return 

def process_txt(lineNum, lineString):
    lineComps = lineString.split()
    result = lineComps[-1]
    return result
    
def analysis(logFile):    
    f = FileLineWrapper(open(logFile, "r"))
    while True:
        rawLine = f.readline()
        if len(rawLine) == 0:
            break
        result = process_txt(f.lineNum, rawLine)
        print result 
        
    f.close()

def main():
    logsToAnalysis = getCurrFiles()
    for logFile in logsToAnalysis:
        print "---------- processing {} ----------------".format(logFile)
        analysis(logFile)


if __name__ == "__main__":
    rc = main()
