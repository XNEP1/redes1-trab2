#!/usr/bin/python3

import socket # importa o módulo de sockets
from threading import *
from enum import Enum
from queue import *
import json
import sys

import readconfig
import tokenring

class TokenRing:
    def __init__(self, hostnameFrom, hostnameTo, port=7304):
        self.hostnameFrom = hostnameFrom
        self.hostnameTo = hostnameTo
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
        

class Eventos(Enum):
    TOKEN = 0
    DESLIGAMENTO = 1
    JOGADA = 2
    VITORIA = 3

class Estados(Enum):
    ESPERANDO = 0  # Esperando todo mundo se conectar
    TURNO_DE_OUTRO = 1
    MEU_TURNO = 2
    VITORIA = 3
    DERROTA = 4
    FIM_DE_JOGO = 5

class Carta:
    def __init__(self, valor):
        self.valor = valor

class Jogo:

    def __init__(self):
        self.estado = Estados.ESPERANDO
        self.turno = ""
        self.minhaMao = []
        self.registro = []

def inicializa_jogo ():
    pass

def jogo_principal ():
    token_ring = token_ring_init(device, hostnameFrom, hostnameTo, porta)
    jogo = inicializa_jogo()
    data = {}
    
    recebedor = {} #thread.init(repassador_de_mensagens, token_ring)
    
    while (jogo.estado != jogo.FIM_JOGO):
        imprimir_tela()
        estado = jogo.estado
        if estado == jogo.ESPERANDO:
            pass # ...
        elif estado == jogo.TURNO_OUTRO:
            pass # ...
        else:
            pass # ...

# Exemplo: SERVIDOR RECEBENDO
# UDPsocket = setup_connection(7304)
# while(True):
    # (data_str, ip_addr) = recv_from(UDPsocket, 2048)
    # print(data_str.decode('utf-8'))


# Exemplo: CLIENT ENVIANDO
# UDPsocket = setup_connection(7304)
# send_to(UDPsocket, "Ola", socket.gethostbyname(hostnameTo), 7304);   

jogo_principal()
