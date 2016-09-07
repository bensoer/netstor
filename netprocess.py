__author__ = 'bensoer'
import socket
import sys
import fcntl
import os


class NetProcess:

    __netstor_socket = None

    __listener_socket = None
    __sender_socket = None
    __configuration = None
    __recv_pipe = None
    __send_pipe = None

    def __init__(self, config_data, recv_pipe, send_pipe):

        if "destaddr" not in config_data:
            print("ERROR. ADDRESS KEY MUST EXIST")
            sys.exit(1)

        #setup the listener socket to recieve connections
        __listener_socket = socket.socket()
        __listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        __listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        __listener_socket.bind(("localhost", 8430))
        __listener_socket.setblocking(0) #don't make it block so that we can skip it

        #set the configuration so it can be referred to by future commands
        __configuration = config_data
        __recv_pipe = recv_pipe
        __send_pipe = send_pipe

        #make pipe non-blocking
        #fcntl.fcntl(__pipe, fcntl.F_SETFL, os.O_NONBLOCK)

    def __has_entry(self, buffer):
        skip_next_letter = False
        for letter in buffer:
            if skip_next_letter:
                skip_next_letter = False
                continue
            if letter == "\\" or letter == "/":
                skip_next_letter = True
                continue
            if letter == "}":
                return True

        return False

    def __get_entry_index(self,buffer):
        skip_next_letter = False
        for index, letter in enumerate(buffer):
            if skip_next_letter:
                skip_next_letter = False
                continue
            if letter == "\\" or letter == "/":
                skip_next_letter = True
                continue
            if letter == "}":
                return index + 1

        return False

    def start(self):

        start_listening = False

        # the first time we run, pipe is blocking, we want to get a successful connect command before we change that
        print("Starting NetProcess. Awaiting Commands")
        while True:
            command = self.__recv_pipe.readline()
            data = None

            if start_listening:
                data = self.__listener_socket.recv(1024)

            if command == "connect":
                if self.__sender_socket is not None:
                    self.__sender_socket.shutdown()
                    self.__sender_socket.close()

                __sender_socket = socket.socket()
                __sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                __sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                try:
                    __sender_socket.connect(self.__configuration["address"])
                except Exception as e:
                    address, port = self.__configuration["address"]
                    print("something's wrong with %s:%d. Exception is %s" % (address, port, e))
                    __sender_socket.close()
                    continue

                #make the recv_pipe now non-blocking and start looping between the recv_pipe and the listener_socket
                #for either data to pass around or a new command of things to do

                fcntl.fcntl(self.__recv_pipe, fcntl.F_SETFL, os.O_NONBLOCK)

            # for adding files to the storage
            if "add" in command:
                file_dir = command.split()[1]
                print("Adding File: " + file_dir)

                #need to find a break point in the network flow. keep listening until you find one and edit/append
                #the 'data' string until you find a spot


            # for removing files from the storage
            if "remove" in command:
                file_name = command.split()[1]
                print("Removing File Named: " + file_name)

                #will need to find this file in the network flow, keep reading and writing until it is found at whihc
                #point them remove it


            #after all of the above has happened we still sendout the data to the sender_socket and loop again for
            #the next command
            if data is not None:
                bytes_of_data = len(data)
                bytes_sent = self.__sender_socket.send(data)
                #if for some reason not all gets sent before a return. keep trying
                while bytes_sent < bytes_of_data:
                    bytes_sent += self.__sender_socket.send(data)