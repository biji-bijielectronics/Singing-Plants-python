import socket

class PdConnection:

    def __init__(self, address, port):
        self.__address = address
        self.__port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connect()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __connect(self):
        server_address = (self.__address, self.__port)
        self.__socket.connect(server_address)

    def close(self):
        self.__socket.close()

    def sendValue(self, name, value):
        message = name + " " + str(value) + ";"
        try:
            self.__socket.send(message)
        except socket.timeout:
            self.__connect()
            self.__socket.send(message)