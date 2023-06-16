import socket
import json
import sys
from queue import *
from threading import *

class TokenRing:
    def __init__(self, From:str , To: str, port=7304):
        self.hostnameFrom = From
        self.hostnameTo = To
        self.from_addr = socket.gethostbyname(self.hostnameFrom)
        self.to_addr = socket.gethostbyname(self.hostnameTo)
        self.port = port
        self.sendLock = Lock()
        self.messageQueue = Queue()
        self.have_token = False
        self.my_addr = socket.gethostbyname(socket.gethostname())
        self.UDPsocket = self.__setup_connection()
        self.__startReceiver()

    def enviar(self, data: dict) -> bool:
        if self.have_token == False:
            return False
        socket.sendto(json.dumps(data).encode("utf-8"), (self.to_addr, self.port))
        self.sendLock.acquire()
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
        socket.sendto(json.dumps(data).encode("utf-8"), (self.to_addr, self.port))
        self.have_token = False
        return
    
    def desligarRede(self):
        data = {
            "Event" : "Desligamento"
        }
        socket.sendto(json.dumps(data).encode("utf-8"), (self.to_addr, self.port))
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
            (data_str, recv_addr) = socket.recvfrom(2048)
            if recv_addr != self.from_addr:
                # Ignora
                continue

            data = json.loads(data_str.decode("utf-8"))
            if data["Event"] == "Token":
                self.have_token = True
                continue

            if data["Event"] == "Desligamento":
                socket.sendto(data_str, (self.to_addr, self.port))
                sys.exit()

            if data["To"] == self.my_addr:
                # Se a thread principal nao funcionar,
                # essa thread trava aqui e a rede em anel trava
                self.messageQueue.put(data_str, block=True)

            if data["From"] == self.my_addr:
                # Remove do anel
                self.sendLock.release()
            else:
                socket.sendto(data_str, (self.to_addr, self.port))