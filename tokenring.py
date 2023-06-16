import socket
import json
import sys
from enum import Enum
from queue import *
from threading import *

class Type(Enum):
    TOKEN = 0
    DATA = 1

def message(Type, To: str, From: str, Data: dict):
    message = {
        "Type" : Type,
        "To" : To,
        "From" : From,
        "Data" : Data.copy()
    }
    return message

class TokenRing:
    def __init__(self, From:str , To: str, port=7304):
        self.hostnameFrom = From
        self.hostnameTo = To
        try:
            self.from_addr = socket.gethostbyname(self.hostnameFrom)
            self.to_addr = socket.gethostbyname(self.hostnameTo)
        except Exception as e:
            pass
        self.port = port
        self.sendSemaphore = BoundedSemaphore(value=0)
        self.messageQueue = Queue()
        self.have_token = False
        self.my_addr = socket.gethostbyname(socket.gethostname())
        self.UDPsocket = self.__setup_connection()
        self.__startReceiver()
            

    def enviar(self, data: dict, To = "Broadcast") -> bool:
        if self.have_token == False:
            return False
        self.__send(message(Type.DATA, To, socket.gethostbyname(socket.gethostname()), data))
        if( not self.sendSemaphore.acquire(timeout=5) ):
            try:
                self.sendSemaphore.release()
            except RuntimeError:
                pass
            return False
        return True
    
    def receber(self) -> dict:
        return self.messageQueue.get(block=True)
    
    # Essa função só deve ser usada pelo primeiro computador na lista do .ini
    def criarToken(self):
        self.have_token = True
        return
    
    def passarToken(self):
        data = {
            "Event" : "Token"
        }
        self.__send(data)
        self.have_token = False
        return

    def __setup_connection(self) -> socket:
        UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPsocket.bind((self.my_addr, self.port))
        return UDPsocket
    
    def __startReceiver(self):
        self.recvManagerThread = Thread(target=self.__recvManager, args=[])
        self.recvManagerThread.start()
        return

    def __recvManager(self):
        while(True):
            (data, recv_addr) = self.__recv()
            if recv_addr != self.from_addr:
                # Ignora
                continue

            if data["Type"] == Type.TOKEN:
                self.have_token = True
                continue

            if data["To"] == self.my_addr or data["To"] == "Broadcast":
                # Se a thread principal nao funcionar,
                # essa thread trava aqui e a rede em anel trava
                self.messageQueue.put(data["Data"], block=True)

            if data["From"] == self.my_addr:
                # Remove do anel
                try:
                    self.sendSemaphore.release()
                except RuntimeError:
                    pass
            else:
                self.__send(data)

    def __send(self, data: dict):
        data_str = json.dumps(data)
        data_str = "<<<" + data_str + ">>>"
        self.UDPsocket.sendto(data_str.encode("utf-8"), (self.to_addr, self.port))

    def __recv(self):
        (data_str, recv_addr) = self.UDPsocket.recvfrom(2048)
        data_str = data_str.decode("utf-8")
        data_str = data_str[3:-3]
        data = json.loads(data_str)
        return (data, recv_addr)
