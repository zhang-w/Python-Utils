#!/usr/bin/env python

import sys, time, os, traceback
import re
from datetime import *; 
from dateutil.relativedelta import *
import dateutil.parser

ApiDict = {}
noResponseOut = open('noResponseApiCall.txt','w')
outstandingOut = open('outstandingApiCall.txt','w')
allOut = open('allApiCall.txt','w')

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
            if logFile.startswith("iota"):
                logFiles.append(os.path.abspath(os.path.join(dirpath, logFile)))

    return logFiles


def splitLine(lineNum, lineString):
    #timeStamp; thread; level; class; msg
    lineComps = lineString.split(';');
    timeStamp = lineComps[0].strip();
    thread = lineComps[1].strip();
    msg = lineComps[4].strip();
    msg = msg.strip('-').strip()
    methodTypeAndMethodName = msg.split('(')[0].split()
    methodType = methodTypeAndMethodName[0]
    methodName = methodTypeAndMethodName[1]

    return [lineNum, timeStamp, thread, methodType, methodName]
    
def findExitTimestamp(logFile, lineNum, thread, methodName):
    timestamp = ""
    f = FileLineWrapper(open(logFile, "r"))
    while True:
        rawLine = f.readline()
        if len(rawLine) == 0:
            break

        
        if f.lineNum <= lineNum :
            continue

        if ("Exit " in rawLine) or ("Enter " in rawLine) :
            comps = splitLine(f.lineNum, rawLine)
            if (comps[2].strip() == thread):
                if (comps[4] == methodName):
                    if (comps[3].strip() == "Exit"):
                        timestamp = comps[1]
                        break;
                    elif (comps[3].strip() == "Enter"):
                         #print "logFile={}, lineNum={}, thread={}, methodName={}, Error/No response!!!".format(logFile, lineNum, thread, methodName)
                         tmpMsg = "logFile={}, lineNum={}, thread={}, methodName={}, Error/No response!!!".format(logFile, lineNum, thread, methodName)
                         noResponseOut.write(tmpMsg + "\n")
                         break
                    else:
                        continue
                 #else:
                 #    print "methodName do not match"
             #else:
             #    print "thread do not match"
        else:
             continue

    #if len(timestamp) <= 0:
        #print "Exit wasn't found for lineNum={}; thread={}; api={}".format(lineNum, thread, methodName)

    f.close()
    return timestamp

def calculateTime(logFile, enter, exit, lineNum, thread, methodName):
    # convert enter and exit
    enter = enter.replace(',', '.');
    exit = exit.replace(',', '.');

    enterTime = dateutil.parser.parse(enter)
    exitTime = dateutil.parser.parse(exit)
    #delta = relativedelta(exitTime, enterTime)
    
    totalSeconds = (exitTime - enterTime).total_seconds()
    #print "{} {} === {} ".format(lineNum, methodName, (exitTime - enterTime).total_seconds())
    fileName = logFile.split("/")[-1]
    #outMsg =  "filename = {}, lineNum={}, api={}, totalSeconds={} ".format(logFile, lineNum, methodName, totalSeconds)
    outMsg =  "filename = {}, lineNum={}, api={}, totalSeconds={} ".format(fileName, lineNum, methodName, totalSeconds)

    allOut.write(outMsg + "\n")

    if (totalSeconds  > 5):
        outstandingOut.write(outMsg + "\n")

    if methodName not in ApiDict:
        ApiDict.setdefault(methodName, [])

    seconds = ApiDict[methodName]
    seconds.append(totalSeconds)
    


def analysis(logFile):    
    f = FileLineWrapper(open(logFile, "r"))
    while True:
        rawLine = f.readline()
        if len(rawLine) == 0:
            break

        # for each Enter
        if "Enter " in rawLine :
            lineComps = splitLine(f.lineNum, rawLine)
            enterTime = lineComps[1].strip();
            thread = lineComps[2].strip();
            #methodType = lineComps[3].strip();
            methodName = lineComps[4].strip();
            exitTime = findExitTimestamp(logFile, f.lineNum, thread, methodName);
            if len(exitTime) > 0:
                calculateTime(logFile, enterTime, exitTime, f.lineNum, thread, methodName)
    f.close()

def main():

    logsToAnalysis = getCurrFiles()
    for logFile in logsToAnalysis:
        print "---------- processing {} ----------------".format(logFile)
        analysis(logFile)

    #print ApiDict  
    for key, value in ApiDict.iteritems():
        average = reduce(lambda x, y: x + y, value) / len(value)
        print "API={}, Max:{}; Average:{}".format(key, max(value), average)

    noResponseOut.close()
    outstandingOut.close()
    allOut.close()


if __name__ == "__main__":
    rc = main()
