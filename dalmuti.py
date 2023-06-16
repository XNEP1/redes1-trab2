#!/usr/bin/python3

from enum import Enum
import socket
from random import shuffle
import sys
import time

from readconfig import read_config
from tokenring import TokenRing

def mensagem(Evento, Info = {}):
    message = {
        "Evento" : Evento,
        "Info" : Info.copy()
    }
    return message

def verifica_repeticao(lista, N):
    contagem = {}
    for num in lista:
        contagem[num] = contagem.get(num, 0) + 1
        if contagem[num] == N:
            return True
    return False

def imprimir_tela(jogo):
    print("\033[H\033[J") 
    print("Está no turno de outro jogador")
    print("============================")
    print(jogo.minhamao)
    print("============================")
    print("Registro:")
    for valor, qnt in jogo.registro:
        if qnt == 0:
            print("Passou a vez")
        else:
            print(f"Valor: {valor}, Quantidade: {qnt}")

def gerar_baralho():
    baralho = []
    for i in range(1,13):
        for n in range(1, i+1):
            baralho.insert(0, i)
    baralho.insert(0, 0)
    baralho.insert(0, 0)
    shuffle(baralho)
    return baralho

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

        
class Evento(Enum):
    TOKEN = 0
    DESLIGAMENTO = 1
    JOGADA = 2
    VITORIA = 3
    PING = 4 # Não faz nada, é só pra ver se a mensagem volta para você
    OK = 5
    DISTRIBUICAO = 6 # Você recebeu sua mão de cartas

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

    def escolherJogada(self, primeiraJogada=False):
        ultima_jogada = []

        if(primeiraJogada):
            while(True):
                print("Você é o primeiro a jogar.")
                print("\n")
                print("\n")
                print("Sua mão: " + str(self.minhaMao))
                print("\033[{subirLinhas}A\033[0K\r".format(3))
                qnt = input("Escolha quantas cartas você irá jogar: ")
                if not qnt.isdigit():
                    print("\033[1;31mJogada Invalida")
                    time.sleep(2)
                    continue
                if not verifica_repeticao(self.minhaMao, qnt):
                    print("\033[1;31mJogada Invalida")
                    time.sleep(2)
                    continue

                ultima_jogada = (13, qnt)

        else:
            ultima_jogada = self.registro[-1]

        while(True):
            print("\033[H\033[J") 
            print("Qual será sua jogada?")
            print("\n")
            print("\n")
            print("\n===========Opções===========")
            filtered = list(filter(lambda valor: valor < ultima_jogada[0], self.minhaMao))
            options = set(filter(lambda x: filtered.count(x) == ultima_jogada[1], filtered))
            n = 0
            print(" " + str(n) + ": Passar a vez" )
            for i in options:
                print(" " + str(n) + ": " + str(ultima_jogada[1]) + " cartas de valor " + str(i))
                n += 1
            print("============================")
            print("\n")
            print("\033[{subirLinhas}A\033[0K\r".format(5 + n))
            selecionado = input("Opção: ")
            if not selecionado.isdigit():
                print("\033[1;31mJogada Invalida")
                time.sleep(2)
                continue
            
            selecionado = int(selecionado)
            if not (selecionado >= 0 and selecionado <= n):
                print("\033[1;31mJogada Invalida")
                time.sleep(2)
                continue

            if selecionado == 0:
                return (-1, 0)
            
            carta = list(options)[selecionado - 1]
            qnt = ultima_jogada[1]
            return (carta, qnt)


def jogo_principal ():
    minha_config = {}
    proximo_no_anel_config = {}
    baralho = []

    jogadores = read_config("dalmuti.ini")
    jogadoresIndex = list(jogadores)
    quantidadeJogadores = len(jogadoresIndex)
    for i in jogadoresIndex[:-1]:
        if (jogadores[i]["addr"] == socket.gethostbyname(socket.gethostname()) or jogadores[i]["addr"] == socket.gethostname()):
            minha_config = jogadores[i]
            proximo_no_anel_config = jogadores[i+1]

    if (jogadores[jogadoresIndex[-1]]["addr"] == socket.gethostbyname(socket.gethostname()) or jogadores[jogadoresIndex[-1]]["addr"] == socket.gethostname()):
        minha_config = jogadores[jogadoresIndex[-1]]
        proximo_no_anel_config = jogadores[jogadoresIndex[0]]
    tokenRing = TokenRing(From= minha_config["addr"], To= proximo_no_anel_config["addr"], port= int(minha_config["port"]))
    jogo = Jogo()

    if (minha_config is jogadores[1]):
        jogo.estado = Estado.ARRUMANDO_BARALHO
    else:
        jogo.estado = Estado.ESPERANDO

    
    while (jogo.estado != Estado.FIM_DE_JOGO):
        # imprimir_tela(jogo)

        if jogo.estado == Estado.ARRUMANDO_BARALHO:
            baralho = list(split(gerar_baralho(), quantidadeJogadores))
            while( not tokenRing.enviar(mensagem(Evento.PING), To= socket.gethostbyname(socket.gethostname()))):
                pass
            _ = tokenRing.receber()
            tokenRing.enviar(mensagem(Evento.OK), To= "Broadcast") 
            _ = tokenRing.receber()
            jogo.estado = Estado.INICIANDO_MASTER
            continue

        elif jogo.estado == Estado.ESPERANDO:
            while( tokenRing.receber()["Evento"] != Evento.OK):
                pass
            jogo.estado = Estado.INICIANDO_PLAYER
            continue




        elif jogo.estado == Estado.INICIANDO_MASTER:
            for i in jogadoresIndex:
                tokenRing.enviar(mensagem(Evento.DISTRIBUICAO, baralho[i-1]), To= jogadores[i]["addr"])
            mensagemR = tokenRing.receber()
            if( mensagemR["Evento"] != Evento.DISTRIBUICAO ):
                raise Exception("Broken Game Logic")
            jogo.minhaMao = sorted( mensagemR["Info"].copy() )
            jogo.estado = Estado.MEU_TURNO
            continue

        elif jogo.estado == Estado.INICIANDO_PLAYER:
            mensagemR = tokenRing.receber()
            if( mensagemR["Evento"] != Evento.DISTRIBUICAO ):
                raise Exception("Broken Game Logic")
            jogo.minhaMao = sorted( mensagemR["Info"].copy() )
            jogo.estado = Estado.TURNO_DE_OUTRO
            continue
            



        elif jogo.estado == Estado.TURNO_DE_OUTRO:
            mensagemR = tokenRing.receber()
            if( mensagemR["Evento"] == Evento.TOKEN ):
                jogo.estado = Estado.MEU_TURNO
                continue
            if( mensagemR["Evento"] != Evento.JOGADA ):
                raise Exception("Broken Game Logic")
            jogo.registro.append( mensagemR["Info"].copy() )
            continue
            
        elif jogo.estado == Estado.MEU_TURNO:
            (carta, qnt) = jogo.escolherJogada()
            tokenRing.enviar(mensagem(Evento.JOGADA, {(carta, qnt)}), To= "Broadcast")
            mensagemR = tokenRing.receber()
            if( mensagemR["Evento"] != Evento.JOGADA ):
                raise Exception("Broken Game Logic")
            jogo.registro.append( mensagemR["Info"].copy().pop() )

            if len(jogo.minhaMao) == 0:
                jogo.estado = Estado.VITORIA
            else:
                tokenRing.enviar(mensagem(Evento.TOKEN), To= proximo_no_anel_config["addr"])
                tokenRing.passarToken()
                jogo.estado = Estado.TURNO_DE_OUTRO
            continue

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
