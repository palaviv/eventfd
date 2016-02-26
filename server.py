"""This is an example of python HTTP server without polling using the EventFD to shutdown the server"""

import threading
import select
from socketserver import TCPServer, BaseRequestHandler
import socket
import time

from eventfd import EventFD


class NonPollingHTTPServer(TCPServer):

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.__is_shut_down = threading.Event()
        # using an EventFD to signal the server_forever to stop
        self.__shutdown_event = EventFD()
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        if bind_and_activate:
            try:
                self.server_bind()
                self.server_activate()
            except:
                self.server_close()
                raise

    # overriding the server_forever class to not poll.
    def serve_forever(self):
        self.__is_shut_down.clear()
        self.__shutdown_event.clear()
        try:
            while True:
                r, w, e = select.select([self.__shutdown_event, self], [], [])

                if self.__shutdown_event in r:
                    break

                if self in r:
                    self._handle_request_noblock()

                self.service_actions()
        finally:
            self.__is_shut_down.set()

    def shutdown(self):
        self.__shutdown_event.set()
        self.__is_shut_down.wait()


###############################################
# MyTCPHandler class and client function are
# from the python socketserver documentation.
###############################################

class MyTCPHandler(BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print("Received: {}".format(response))
    finally:
        sock.close()


def test():
    server = NonPollingHTTPServer(("localhost", 0), MyTCPHandler)
    ip, port = server.server_address

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    client(ip, port, b"Hello World 1")
    client(ip, port, b"Hello World 2")
    client(ip, port, b"Hello World 3")

    print("requesting server shutdown at {}".format(time.time()))
    server.shutdown()
    print("server was shutdown at {}".format(time.time()))
    server.server_close()


if __name__ == "__main__":
    test()



