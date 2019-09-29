#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 20:47:48 2019

@author: mrich
"""

import socket
import re

import threading
import queue
"""
regex = r"]->!(.+)"

test_str = ("[dawg]->bo!rk\n"
	"[dawg]->b!ork\n"
	"[dawg]->!bork\n"
	"[dawg]->!peer\n\n")

matches = re.finditer(regex, test_str, re.MULTILINE)

for matchNum, match in enumerate(matches, start=1):
    
    print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    
    for groupNum in range(0, len(match.groups())):
        groupNum = groupNum + 1
        
        print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

data = "[dawg]->!bork"
data = "[dawg]->b!ork\n"
data = "[dawg]->!gopeer(192.168.1.78, 5000)"
match = re.search(regex,data)
if match:
    print("match found: {}".format(match.group(1)))
else:
    print("no match")
    

def checkForCommand(data):
    # returns false on no command, or the command string on command
    cmd_regex = r"]->!(.+)"
    match = re.search(cmd_regex,data)
    if match:
        return match.group(1)
    return False
"""
"""
def getInput(q):
    while True:
        data = input()
        q.put((data))
    
def inputMonitor():
    mumbo = queue.Queue()
    threading.Thread(target=getInput,args=(mumbo,)).start()
    print("started")
    while True:
        while not mumbo.empty():
            data = mumbo.get()
            print("this happened: {}".format(data))

inputMonitor()
"""
if True:
    pass
    print("thing")
    