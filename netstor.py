from netprocess import NetProcess
import socket
import sys
import fcntl
import os
from tools.argparcer import ArgParcer


arguments = sys.argv
if len(arguments) <= 1:
    # print out help or something
    print("ERROR. NO ARGUMENTS PASSED. PARAMETERS REQUIRED TO OPERATE")
    sys.exit(1)

#fetch the arguments we need
address = ArgParcer.getValue(arguments, "-h")
port = ArgParcer.getValue(arguments, "-p")

if address == "" or port == "":
    print("ERROR. ADDRESS AND PORT PARAMETERS ARE REQUIRED")
    sys.exit(1)

config_data = {"address": (address, port)}
send_pipe = os.pipe()
recv_pipe = os.pipe()

pid = os.fork()
if pid == 0:
    print("IN CHILD PROCESS")
    # this is the child process
    net_manager = NetProcess(config_data, recv_pipe, send_pipe)
    net_manager.start()

elif pid > 0:

    #this is the parent process
    print("IN THE PARENT PROCESS")
    os.wait()

elif pid < 0:
    # there was an error creating the process
    print("ERROR. COULD NOT CREATE CHILD PROCESS")
else:
    print("UNKNOWN ERROR HAS OCCURRED")
    sys.exit(1)


