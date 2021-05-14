import sys
import json
import socket
from IA import next
import random

def SendServer(port, msg):                        #sends message converted to json and encoded to the server
    s = socket.socket()
    s.bind(('localhost', port))
    s.connect(('localhost', 3000))
    msg = json.dumps(msg).encode('utf8')
    s.send(msg)

def identity():             #fetches port and name from the arguments (command line)
    ClientPort = 3001           #Default
    ClientName = "IAbalone"     #Default
    args = sys.argv[1:]
    for arg in args:
        if arg.startswith('name='):
            ClientName = arg[len('name='):]
        else:
            ClientPort = int(arg)
    return ClientPort, ClientName

def subscribe(ClientPort, ClientName):          #connects to the server
    msg = {
        "request": "subscribe",
        "port": ClientPort,
        "name": ClientName,
        "matricules": ["195193", "195003"]
    }
    SendServer(ClientPort, msg)

def ProcessRequest(request, client, port):          #détermine ce qu'il faut répondre en fonction du type de requête
    if request["request"] == "ping":
        response = {"response": "pong"}
        msg = json.dumps(response).encode('utf8')
        client.send(msg)
        return False
    if request["request"] == "play":
        move = next(request["state"])
        print(move)
        response = {
            "response": "move",
            "move": move,
            "message": "Fun message"
            }
        msg = json.dumps(response).encode('utf8')
        client.send(msg)
        return False
    return True

def listenForRequests(port):        #boucle qui écoute le serveur
    while True:
        finished = False
        request=""
        with socket.socket() as s:
            s.bind(('localhost', port))
            s.listen()
            while not finished:
                client, address = s.accept()
                print(address)
                request = json.loads(client.recv(4096).decode('utf8'))
                print(request)
                finished = ProcessRequest(request, client, port)


def start(ClientPort, ClientName):              #starts the program
    subscribe(ClientPort, ClientName)
    listenForRequests(ClientPort)