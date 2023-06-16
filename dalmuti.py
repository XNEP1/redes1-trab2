#!/usr/bin/python3

from threading import *
from enum import Enum
import sys

import readconfig
from tokenring import *

def mensagem(Evento, Info = {}):
    message = {
        "Evento" : Evento,
        "Info" : Info.copy()
    }
    return message

def imprimir_tela():
    pass
        
class Evento(Enum):
    TOKEN = 0
    DESLIGAMENTO = 1
    JOGADA = 2
    VITORIA = 3
    PING = 4 # Não faz nada, é só pra ver se a mensagem volta para você
    OK = 4

class Estado(Enum):
    ARRUMANDO_BARALHO = -2  # Você é o lider da mesa e está esperando todo mundo se conectar
    INICIANDO_MASTER = -1   # Você é o lider da mesa e está distribuindo cartas
    ESPERANDO = 0           # Esperando todo mundo se conectar
    INICIANDO_PLAYER = 1    # Recebendo as cartas, etc
    TURNO_DE_OUTRO = 2
    MEU_TURNO = 3
    VITORIA = 4
    DERROTA = 5
    FIM_DE_JOGO = 6

class Carta:
    def __init__(self, valor):
        self.valor = valor

class Jogo:

    def __init__(self):
        self.estado = Estado.ESPERANDO
        self.turno = ""
        self.minhaMao = []
        self.registro = []

def inicializa_jogo ():
    return Jogo()

def jogo_principal ():
    tokenRing = TokenRing(From="h1", To="h2")
    jogo = inicializa_jogo()
    data = {}


    
    while (jogo.estado != Estado.FIM_DE_JOGO):
        imprimir_tela()

        if jogo.estado == Estado.ARRUMANDO_BARALHO:
            while( not tokenRing.enviar(mensagem(Evento.PING), To=socket.gethostbyname(socket.gethostname()))):
                pass
            _ = tokenRing.receber()
            tokenRing.enviar(mensagem(Evento.OK), To= "Broadcast") 
            jogo.estado = Estado.INICIANDO_MASTER
            continue

        elif jogo.estado == Estado.ESPERANDO:
            while( tokenRing.receber()["Evento"] != Evento.OK):
                pass
            jogo.estado = Estado.INICIANDO_PLAYER
            continue


        elif jogo.estado == Estado.INICIANDO_MASTER:
            pass # ...
        elif jogo.estado == Estado.INICIANDO_PLAYER:
            pass # ...


        elif jogo.estado == Estado.TURNO_DE_OUTRO:
            pass # ...
        elif jogo.estado == Estado.MEU_TURNO:
            pass # ...
        elif jogo.estado == Estado.VITORIA:
            pass # ...
        elif jogo.estado == Estado.DERROTA:
            pass # ...
        elif jogo.estado == Estado.FIM_DE_JOGO:
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
