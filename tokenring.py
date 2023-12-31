import socket
import json
import sys
from enum import IntEnum
from queue import Queue
from threading import Thread, Lock

class Type(IntEnum):
    TOKEN = 0
    DATA = 1

def message(Type, To: str, From: str, Data: dict):
    message = {
        "Type" : Type,
        "To" : To,
        "From" : From,
        "Data" : Data.copy(),
        "Confirmação" : False
    }
    return message

class TokenRing:
    def __init__(self, From:str , To: str, ToPort: int ,myPort=7304):
        self.hostnameFrom = From
        self.hostnameTo = To
        try:
            self.from_addr = socket.gethostbyname(self.hostnameFrom)
            self.to_addr = socket.gethostbyname(self.hostnameTo)
        except Exception as e:
            raise Exception("Impossivel achar o host. Confira o dalmuti.ini")
        self.to_port = ToPort
        self.port = int(myPort)
        self.sendLock = Lock()
        self.tokenLock = Lock()
        self.messageQueue = Queue()
        self.have_token = False
        self.my_addr = socket.gethostbyname(socket.gethostname())
        self.my_hostname = socket.gethostname()
        self.UDPsocket = self.__setup_connection()
        self.__startReceiver()
            

    def enviar(self, data: dict, To = "Broadcast") -> bool:
        if self.have_token == False:
            self.tokenLock.acquire(blocking=False)
            self.tokenLock.acquire(blocking=True)
        
        self.sendLock.acquire(blocking=False)
        self.__send(message(Type.DATA, To, socket.gethostbyname(socket.gethostname()), data))
        if( not self.sendLock.acquire(timeout=5) ):
            try:
                self.sendLock.release()
            except ValueError:
                pass
            return False
        return True
    
    def receber(self) -> dict:
        return self.messageQueue.get(block=True)
    
    # Essa função só deve ser usada pelo primeiro computador na lista do .ini
    def criarToken(self):
        self.have_token = True
        return
    
    def passarToken(self, To: str) -> bool:
        if self.have_token == False:
            return False
        self.__send(message(Type.TOKEN, To, socket.gethostbyname(socket.gethostname()), {}))
        self.have_token = False
        return True

    def __setup_connection(self):
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
            if recv_addr[0] != self.from_addr:
                # Ignora
                continue

            if data["To"] == self.my_addr or data["To"] == "Broadcast" or data["To"] == self.my_hostname:
                # Se a thread principal nao funcionar,
                # essa thread trava aqui e a rede em anel trava
                data["Confirmação"] = True
                if data["Type"] == Type.TOKEN:
                    self.have_token = True
                    try:
                        self.tokenLock.release()
                    except RuntimeError:
                        pass
                    continue
                self.messageQueue.put(data["Data"], block=True)

            if data["From"] == self.my_addr:
                # Remove do anel
                if(not data["Confirmação"]):
                    raise Exception("Connection Error")
                try:
                    self.sendLock.release()
                except ValueError:
                    pass
            else:
                self.__send(data)

    def __send(self, data: dict):
        data_str = json.dumps(data)
        data_str = "<<<" + data_str + ">>>"
        self.UDPsocket.sendto(data_str.encode("utf-8"), (self.to_addr, self.to_port))

    def __recv(self):
        (data_str, recv_addr) = self.UDPsocket.recvfrom(2048)
        data_str = data_str.decode("utf-8")
        data_str = data_str[3:-3]
        data = json.loads(data_str)
        return (data, recv_addr)
