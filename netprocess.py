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


    def start(self):

        # the first time we run, pipe is blocking, we want to get a successful connect command before we change that
        print("Starting NetProcess. Awaiting Commands")
        while True:
            command = self.__recv_pipe.readline()

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

            # assuming everything is successful, this part is simply adding and copying over content around
