#!/usr/bin/python3

from threading import *
from enum import Enum
import sys

import readconfig
from tokenring import *
        
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
    tokenRing = TokenRing(From="h1", To="h2")
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
