#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 19:34:11 2019

@author: mrich
"""

import argparse
import socket
import threading
import queue
import sys
import random
import os
import re
import random
import string
import time

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def checkForCommand(data):
    # returns false on no command, or the command string on command
    cmd_regex = r"]->!(.+)"
    match = re.search(cmd_regex,data)
    if match:
        return match.group(1)
    return False
"""
My peering strat
    !trypeer - sent by a client to ask for peering
    !gopeer|ip,port,nonce - Sent by server back to clients with ip and port they should start sending to
    !peer|nonce - Sent by client to client until the corresponding peer is received, indicating link is up
"""

#Client Code
def ReceiveData(sock):
    data = False
    try:
        data,addr = sock.recvfrom(1024)
        data=data.decode('utf-8')
        return data,addr        
    except:
        return False,0

"""
client states:
    0 = client - server
    1 = waiting for peer
    2 = in peer
"""

def monitorUserInput(q):
    while True:
        data = input()
        q.put((data))
        if data == 'qqq':
            break
        
    return

def RunClient():
    clientState = 0
    host = get_ip()
    port = random.randint(6000,10000)
    print('Client IP->'+str(host)+' Port->'+str(port))
    server = (str(args.ip),args.port)
    
    # peer place holder
    peerIP = '127.0.0.1'
    peerPort = 31337
    nonce ='notset'    
    peer = (peerIP,peerPort) 
    
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.setblocking(False)
    s.bind((host,port))

    name = args.handle
    while name is None:
        name = input('Please write your name here: ')
    s.sendto(name.encode('utf-8'),server)
    userInput = queue.Queue()
    threading.Thread(target=monitorUserInput,args=(userInput,)).start()
    print("'qqq' to exit")
    while keepRunning:
        #print('loop')
        if not userInput.empty():
            data = userInput.get()
            #print("User input received {}".format(data))
            if data == 'qqq':
                break
            elif data=='':
                continue
            data = '['+name+']' + '->'+ data
            if clientState in [0,1]:
                s.sendto(data.encode('utf-8'),server)
            elif clientState == 2:
                s.sendto(data.encode('utf-8'),peer)
    
        data,addr = ReceiveData(s)
        if data:
            cmd = checkForCommand(data)
            if cmd:
                if clientState == 0:
                    # check for gopeer command
                    if (cmd.startswith("gopeer")):
                        # get the important part
                        peerIP, peerPort, nonce = cmd.split("|")[1].split(",")
                        # set te peer
                        peer = (peerIP, int(peerPort))
                        #set the state
                        clientState = 1
                        print("Go peer recvd: {}, {}, {}".format(peerIP, peerPort, nonce))
                if clientState == 1:
                    
                    if (cmd.startswith("peer")):
                        # get the sent nonce
                        print("peer recvd: {}".format(cmd))
                        sentnonce = cmd.split("|")[1]
                        if (nonce == sentnonce):
                            # We are peered!
                            print("[!] Peer to peer established!")
                            clientState = 2
                        else:
                            print("nonce mismatch? {} != {}".format(nonce, sentnonce))
                
                if clientState == 2:
                    # placeholder
                    pass
                #print("Command received: {}".format(cmd))
            # end command check
            else:
                # just print the received message
                print("[{}]: {}".format(addr,data))
        else:
            # No data was received, placeholder
            pass
    
        # Need to send the peer command if in correct state
        if clientState == 1:
            peercmd = '['+name+']->!peer|' + nonce
            s.sendto(peercmd.encode('utf-8'),peer)
        
        # little sleep to prevent crazy message spam
        time.sleep(0.1)
        
    s.close()
    os._exit(1)
#Client Code Ends Here


#Server Code
def RecvData(sock,recvPackets):
    while keepRunning:
        data,addr = sock.recvfrom(1024)
        recvPackets.put((data,addr))

def RunServer():
    host = get_ip()
    port = args.port
    print('Server hosting on IP-> '+str(host))
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((host,port))
    clients = set()
    recvPackets = queue.Queue()

    print('Server Running...')

    threading.Thread(target=RecvData,args=(s,recvPackets)).start()

    while keepRunning:
        while not recvPackets.empty():
            data,addr = recvPackets.get()
            if addr not in clients:
                clients.add(addr)
                #continue
            #clients.add(addr)
            data = data.decode('utf-8')
            cmd = checkForCommand(data)
            if cmd:
                print("Command received: {}".format(cmd))
                if cmd.startswith('trypeer'):
                    # go through the list of clients and send a gopeer message
                    # this is really only meant for single peer to peer testing
                    nonce = randomString(5)
                    for c1 in clients:
                        for c2 in clients:
                            if c1 != c2:
                                # format data in c2 and send as gopeer
                                msg = "[server]->!gopeer|{},{},{}".format(c2[0], c2[1], nonce)
                                print("sending {} to {}".format(msg,str(c1)))
                                s.sendto(msg.encode('utf-8'),c1)
                            # end if c1 != c2
                        # end for c2
                    # end for c1
                # end command check
            elif data.endswith('qqq'):
                clients.remove(addr)
                continue
            else:
                print(str(addr)+data)
                for c in clients:
                    if c!=addr:
                        s.sendto(data.encode('utf-8'),c)
    s.close()
    
#Server Code Ends Here
description = 'UDP Chat v0.1 Beta\n'
description += "Want to learn about UDP hole punching?  Write it yourself.\n"

parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("mode", type=str, help="Either server or client", choices=['server', 'client'])
parser.add_argument("--ip", type=str, help="Server IP, required in client mode")
parser.add_argument("--port", type=int, help="Server port.  If specified in server mode, will establish server at given port", default=5000)
parser.add_argument("--handle", type=str, help="Your chosen chat handle.  If not specified, will be requested")
# And GO!

args = parser.parse_args()
keepRunning = True

if (args.mode == 'client') and (args.ip is None):
    parser.error("client mode requires the server ip, set with '--ip=x.x.x.x'")


if __name__ == '__main__':
    try:
        if args.mode=='server':
            print("would run server at port {}".format(args.port))
            RunServer()
        elif args.mode=='client':
            print("Would run client to server at {}:{} with handle: {}".format(args.ip, args.port, args.handle))
            RunClient()
    except Exception as badnews: 
        # basically exiting all threads on an exception
        print("Exiting because of {}".format(badnews))
        keepRunning = False
        print("Stopped.")
        os._exit(1)
        