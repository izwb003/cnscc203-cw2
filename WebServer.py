#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Copyright (c) 2023 Steven Song

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import argparse
import socket

version = '0.1.0'


class WebServer:
    """
    Define a web server.
    """
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handleRequest(self, tcpSocket):
        """
        Handle a GET request.
        :param tcpSocket: the request's socket.
        :return:
        """
        requestData = tcpSocket.recv(1024).decode('utf-8')

        try:
            requestPath = requestData.split(' ')[1]
        except IndexError:
            requestPath = '/index.html'
        if requestPath == '/':
            requestPath = '/index.html'

        filePath = "." + requestPath

        if os.path.exists(filePath):
            with open(filePath, 'r') as file:
                fileContent = file.read()
            responseStatus = "HTTP/1.1 200 OK\r\n"
        else:
            fileContent = "404 Not Found."
            responseStatus = "HTTP/1.1 404 Not Found\r\n"

        responseHeader = f"{responseStatus}Content-Type: text/html\r\nCharset: utf-8\r\n\r\n"
        response = responseHeader.encode('utf-8') + fileContent.encode('utf-8')

        tcpSocket.sendall(response)

        tcpSocket.close()

    def startServer(self, serverAddress, serverPort):
        """
        Starts the server and keep listening for request.
        :param serverAddress: This server's address.
        :param serverPort: This server's port.
        :return:
        """
        # Create server socket
        print("Starting the server...")
        self.serverSocket.bind((serverAddress, serverPort))
        # Set backlog to 1 so it only handles 1 connection per time.
        self.serverSocket.listen(1)
        print(f"Server started. Listening on {serverAddress}:{serverPort}...")

        # Wait for request
        while True:
            clientSocket, clientAddress = self.serverSocket.accept()
            print(f"Received connection from {clientAddress[0]}:{clientAddress[1]}")
            self.handleRequest(clientSocket)


if __name__ == "__main__":
    commandParser = argparse.ArgumentParser(
        description=f"WebServer.py {version} Copyright (c) 2023 Steven Song. Coursework for CNSCC203 Computer Networks "
                    f"2023.")
    commandParser.add_argument('-p', metavar='port', default=80, type=int, help="server listening port.")
    commandOptions = commandParser.parse_args()
    print(f"WebServer.py {version} Copyright (c) 2023 Steven Song. Coursework for CNSCC203 Computer Networks 2023.")
    server = WebServer()
    server.startServer("", commandOptions.p)
