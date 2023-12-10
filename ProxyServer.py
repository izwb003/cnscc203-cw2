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

import argparse
import socket
import threading

version = '0.1.0'


class ProxyServer:
    """
    Define a proxy server.
    """
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handleRequest(self, tcpSocket):
        """
        Handle a request sent across tcpSocket.
        :param tcpSocket: the request's socket.
        :return:
        """
        try:
            tcpSocket.settimeout(5)
            requestData = tcpSocket.recv(4096)

            # Analyze client request
            requestLines = requestData.split(b'\r\n')
            requestFirstLine = requestLines[0].decode('utf-8')
            method, url, protocol = requestFirstLine.split()

            # Extract host and port information
            if url.find("://") != -1:
                hostStart = url.find("://") + 3
            else:
                hostStart = 0
            if url.find("/", hostStart) != -1:
                hostEnd = url.find("/", hostStart)
            else:
                hostEnd = len(url)
            portPosition = url.find(":", hostStart)
            if portPosition != -1:
                # If a port was set extracts it
                targetPort = int(url[portPosition + 1:hostEnd])
                hostEnd = portPosition
            else:
                # If not then use default
                targetPort = 80
            targetHost = url[hostStart:hostEnd]

            # Connect target server
            print(f"Proxy connecting to {targetHost}:{targetPort}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as targetSocket:
                targetSocket.settimeout(5)
                targetSocket.connect((targetHost, targetPort))
                targetSocket.send(requestData)

                # Receive target server's response and send it to the client
                responseData = targetSocket.recv(4096)
                # Use a while loop to make sure that every packet are received.
                while len(responseData) > 0:
                    tcpSocket.send(responseData)
                    responseData = targetSocket.recv(4096)
        except socket.timeout:
            print("Connection to target host timed out.")
        except Exception as e:
            print(f"An error occured: {e}")

    def startServer(self, serverAddress, serverPort):
        """
        Starts the server and keeps listening for request.
        :param serverAddress: Listening address.
        :param serverPort: Listening port.
        :return:
        """
        # Create server socket
        print("Starting the server...")
        self.serverSocket.bind((serverAddress, serverPort))
        # Set backlog to 1 so it only handles 1 connection per time.
        self.serverSocket.listen(1)
        print(f"Server started. Listening on {serverAddress}:{serverPort}...")

        # Waiting for request
        while True:
            clientSocket, clientAddress = self.serverSocket.accept()
            print(f"Received connection from {clientAddress[0]}:{clientAddress[1]}")
            # As a browser may send so many weird request, multithread is necessary.
            clientHandler = threading.Thread(target=self.handleRequest, args=(clientSocket,))
            clientHandler.start()


if __name__ == "__main__":
    commandParser = argparse.ArgumentParser(
        description=f"ProxyServer.py {version} Copyright (c) 2023 Steven Song. Coursework for CNSCC203 Computer Networks "
                    f"2023.")
    commandParser.add_argument('-l', metavar='listening-address', default='127.0.0.1', type=str,
                               help="server listening address.")
    commandParser.add_argument('-p', metavar='port', default=8088, type=int, help="server listening port.")
    commandOptions = commandParser.parse_args()
    print(f"ProxyServer.py {version} Copyright (c) 2023 Steven Song. Coursework for CNSCC203 Computer Networks 2023.")
    server = ProxyServer()
    server.startServer(commandOptions.l, commandOptions.p)
