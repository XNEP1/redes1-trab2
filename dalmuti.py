#!/usr/bin/python3

from enum import IntEnum
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

def imprimir_suaMao(jogo):
    print("\033[1;33m", end="")
    print("===========Sua Mão===========")
    print(str(jogo.minhaMao)[1:-1])
    print("============================")
    print("\033[0m", end="", flush=True)

def imprimir_registro(jogo) -> int: # linhas impressas
    print("\033[47m\033[30m", end="")
    print("Registro:")
    for r in jogo.registro[::-1][:15]:
        if r["Acontecimento"] == Jogada.PASSOU:
            print("{quem} passou a vez.".format(quem= r["Quem"]))
        else:
            (valor, qnt, coringasUsados) = r["Jogada"]
            if coringasUsados == 0:
                print("{quem} jogou {qnt} cartas de valor {valor}.".format(quem= r["Quem"], qnt= qnt, valor= valor))
            elif coringasUsados == 1:
                print("{quem} jogou {qnt} cartas de valor {valor} e mais 1 coringa.".format(quem= r["Quem"], qnt= qnt-1, valor= valor))
            elif coringasUsados == 2:
                print("{quem} jogou {qnt} cartas de valor {valor} e mais 2 coringa.".format(quem= r["Quem"], qnt= qnt-2, valor= valor))
    print("\033[0m", end="", flush=True)
    return (1 + len(jogo.registro[::-1][:15]))

def imprimir_tela(jogo):
    print("\033[H\033[J", end="", flush=True) 
    if(jogo.estado == Estado.ESPERANDO):
        print("Esperando conexão...")
    elif (jogo.estado == Estado.ARRUMANDO_BARALHO):
        print("Você é o lider da mesa")
        print("Esperando conexão...")
    elif (jogo.estado == Estado.TURNO_DE_OUTRO):
        imprimir_suaMao(jogo)
        print("Está no turno de outro jogador")
        print("Espere ele jogar")
        print("")
        imprimir_registro(jogo)
            # Falta o print de vitoria
    else:
        pass

def gerar_baralho():
    baralho = []
    for i in range(1,13):
        for n in range(1, i+1):
            baralho.insert(0, i)
    baralho.insert(0, 13)
    baralho.insert(0, 13)
    shuffle(baralho)
    return baralho

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

        
class Evento(IntEnum):
    TOKEN = 0
    DESLIGAMENTO = 1
    JOGADA = 2
    VITORIA = 3
    PING = 4 # Não faz nada, é só pra ver se a mensagem volta para você
    OK = 5
    DISTRIBUICAO = 6 # Você recebeu sua mão de cartas
    PASSOU = 7 # O jogador passou a vez

class Jogada(IntEnum):
    CARTA = 0
    PASSOU = 1

class Estado(IntEnum):
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
        self.minhaMao = []
        self.registro = []

    def escolherJogada(self, primeiraJogada=False):
        ultima_jogada = []

        if(primeiraJogada):
            while(True):
                print("\033[H\033[J", end="", flush=True) 
                imprimir_suaMao(self)
                print("Você é o primeiro a jogar.")
                print("")
                print("")
                linhas = imprimir_registro(self)
                print("\033[{subirLinhas}A\033[0K\r".format(subirLinhas=2+linhas), end="", flush=True)
                qnt = input("Escolha quantas cartas você irá jogar: ")
                try:
                    qnt = int(qnt)
                except ValueError:
                    print("\033[1;31mJogada Invalida\033[0m", end="", flush=True)
                    time.sleep(2)
                    continue
                if not verifica_repeticao(self.minhaMao, qnt):
                    print("\033[1;31mJogada Invalida\033[0m", end="", flush=True)
                    time.sleep(2)
                    continue

                ultima_jogada = (14, qnt)
                break

        else:
            ultima_jogada = self.registro[-1]["Jogada"]

        while(True):
            print("\033[H\033[J", end="", flush=True) 
            imprimir_suaMao(self)
            print("Qual será sua jogada?")
            print("")
            print("")
            print("===========Opções===========")
            filtered = list(filter(lambda valor: valor < ultima_jogada[0], self.minhaMao))
            options = set(filter(lambda x: filtered.count(x) >= ultima_jogada[1], filtered))
            
            options_coringa_1 = []
            options_coringa_2 = []
            if self.minhaMao.count(13) > 0: # Aqueles com 1 e 2 coringas
                options_coringa_1 = set(filter(lambda x: filtered.count(x) + 1 >= ultima_jogada[1] and filtered.count(x) != 0, filtered))
            if self.minhaMao.count(13) == 2: # só aqueles com 2 coringas
                options_coringa_2 = set(filter(lambda x: filtered.count(x) + 2 >= ultima_jogada[1] and filtered.count(x) != 0, filtered))
            n = 0
            o1 = 0 # Usados pra saber as fronteiras entre os tipos de opções
            o2 = 0
            print(" " + str(n) + ": Passar a vez" )
            n += 1
            for i in options:
                print(" " + str(n) + ": " + str(ultima_jogada[1]) + " cartas de valor " + str(i))
                n += 1
                o1 += 1
                o2 += 1
            for i in options_coringa_1:
                print(" " + str(n) + ": " + str(ultima_jogada[1] - 1) + " cartas de valor " + str(i) + " + 1 carta coringa")
                n += 1
                o2 += 1
            for i in options_coringa_2:
                print(" " + str(n) + ": " + str(ultima_jogada[1] - 2) + " cartas de valor " + str(i) + " + 2 carta coringa")
                n += 1
            print("============================")
            print("")
            linhas = imprimir_registro(self)
            print("\033[{subirLinhas}A\033[0K\r".format(subirLinhas= (5 + n + linhas)), end="", flush=True)
            selecionado = input("Opção: ")
            try:
                selecionado = int(selecionado)
            except ValueError:
                print("\033[1;31mJogada Invalida\033[0m", end="", flush=True)
                time.sleep(2)
                continue
            
            if not (selecionado >= 0 and selecionado < n):
                print("\033[1;31mJogada Invalida\033[0m", end="", flush=True)
                time.sleep(2)
                continue

            if selecionado == 0:
                return (-1, 0, 0)
            
            qnt = ultima_jogada[1]
            coringasUsados = 0

            if selecionado <= o1: # Não usou coringas junto a outras cartas
                carta = list(options)[selecionado - 1]
                for _ in range(qnt):
                    self.minhaMao.remove(carta)
            elif selecionado > o1 and selecionado <= o2: # selecionou opção com 1 coringa
                carta = list(options_coringa_1)[selecionado - o1 - 1]
                self.minhaMao.remove(13)
                coringasUsados = 1
                for _ in range(qnt - 1):
                    self.minhaMao.remove(carta)
            else: # usou 2 coringas
                carta = list(options_coringa_2)[selecionado - o2 - 1]
                self.minhaMao.remove(13)
                self.minhaMao.remove(13)
                coringasUsados = 2
                for _ in range(qnt - 2):
                    self.minhaMao.remove(carta)

            return (carta, qnt, coringasUsados)


def jogo_principal ():
    minha_config = {}
    anterior_no_anel_config = {}
    proximo_no_anel_config = {}
    baralho = []
    vencedorHostname = ""

    jogadores = read_config("dalmuti.ini")
    jogadoresIndex = list(jogadores)
    quantidadeJogadores = len(jogadoresIndex)
    for i in jogadoresIndex[:-1]:
        try:
            socket.gethostbyname(jogadores[i]["addr"])
        except Exception as e:
            raise Exception("Impossivel achar o host. Confira o dalmuti.ini")

        if (jogadores[i]["addr"] == socket.gethostbyname(socket.gethostname()) or jogadores[i]["addr"] == socket.gethostname()):
            anterior_no_anel_config = jogadores[jogadoresIndex[i-2]]
            minha_config = jogadores[i]
            proximo_no_anel_config = jogadores[i+1]

    if (jogadores[jogadoresIndex[-1]]["addr"] == socket.gethostbyname(socket.gethostname()) or jogadores[jogadoresIndex[-1]]["addr"] == socket.gethostname()):
        anterior_no_anel_config = jogadores[jogadoresIndex[-2]]
        minha_config = jogadores[jogadoresIndex[-1]]
        proximo_no_anel_config = jogadores[jogadoresIndex[0]]


    tokenRing = TokenRing(From= anterior_no_anel_config["addr"], To= proximo_no_anel_config["addr"], myPort= int(minha_config["port"]), ToPort= int(proximo_no_anel_config["port"]))
    jogo = Jogo()

    if (minha_config is jogadores[1]):
        jogo.estado = Estado.ARRUMANDO_BARALHO
        tokenRing.criarToken()
    else:
        jogo.estado = Estado.ESPERANDO

    
    while (jogo.estado != Estado.FIM_DE_JOGO):
        imprimir_tela(jogo)

        if jogo.estado == Estado.ARRUMANDO_BARALHO:
            baralho = list(split(gerar_baralho(), quantidadeJogadores))
            while( not tokenRing.enviar(mensagem(Evento.PING), To= socket.gethostbyname(socket.gethostname()))):
                pass
            _ = tokenRing.receber()
            if( not tokenRing.enviar(mensagem(Evento.OK), To= "Broadcast") ):
                raise Exception("Connection Loss")
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
                if( not tokenRing.enviar(mensagem(Evento.DISTRIBUICAO, baralho[i-1]), To= jogadores[i]["addr"])):
                    raise Exception("Connection Loss")
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
            if( mensagemR["Evento"] == Evento.VITORIA ):
                jogo.estado = Estado.DERROTA
                vencedorHostname = mensagemR["Info"]["Quem"]
                continue
            if(mensagemR["Evento"] != Evento.JOGADA):
                raise Exception("Broken Game Logic")
            
            jogo.registro.append( mensagemR["Info"].copy() )
            continue
            
        elif jogo.estado == Estado.MEU_TURNO:
            if len(jogo.registro) == 0:
                (carta, qnt, coringasUsados) = jogo.escolherJogada(primeiraJogada= True)
            elif jogo.registro[-1]["Contagem"] >= quantidadeJogadores:
                (carta, qnt, coringasUsados) = jogo.escolherJogada(primeiraJogada= True)
            else:
                (carta, qnt, coringasUsados) = jogo.escolherJogada()
            acontecimento = -1
            ultimoAJogar = {}
            contagem = 0
            if qnt == 0:
                acontecimento = Jogada.PASSOU
                ultimoAJogar = jogo.registro[-1]["Ultimo a jogar"]
                contagem = jogo.registro[-1]["Contagem"] + 1
            else:
                acontecimento = Jogada.CARTA
                ultimoAJogar = socket.gethostname()
            info = {
                "Quem" : socket.gethostname(),
                "Acontecimento" : acontecimento,
                "Jogada" : (carta, qnt, coringasUsados),
                "Ultimo a jogar" : ultimoAJogar,
                "Contagem" : contagem
            }
            if( not tokenRing.enviar(mensagem(Evento.JOGADA, info), To= "Broadcast")):
                raise Exception("Connection Loss")
            mensagemR = tokenRing.receber()
            if( mensagemR["Evento"] != Evento.JOGADA ):
                raise Exception("Broken Game Logic")
            jogo.registro.append( mensagemR["Info"].copy() )

            if len(jogo.minhaMao) == 0:
                jogo.estado = Estado.VITORIA
            elif contagem >= quantidadeJogadores:
                if( not tokenRing.enviar(mensagem(Evento.TOKEN), To= ultimoAJogar)):
                    raise Exception("Connection Loss")
                if( not tokenRing.passarToken(To= ultimoAJogar)):
                    raise Exception("Token Error")
                jogo.estado = Estado.TURNO_DE_OUTRO
            else:
                if( not tokenRing.enviar(mensagem(Evento.TOKEN), To= proximo_no_anel_config["addr"])):
                    raise Exception("Connection Loss")
                if( not tokenRing.passarToken(To= proximo_no_anel_config["addr"])):
                    raise Exception("Token Loss")
                jogo.estado = Estado.TURNO_DE_OUTRO
            continue

        elif jogo.estado == Estado.VITORIA:
            my_hostname = socket.gethostname()
            print("\033[H\033[J", end="") 
            print("\033[0;32m", end="")
            print(f"PARABÉNS {my_hostname}! VOCÊ FOI O VENCEDOR!")
            print("\033[0m", end="", flush=True)
            info = {
                "Quem" : my_hostname,
            }
            if( not tokenRing.enviar(mensagem(Evento.VITORIA, info), To = "Broadcast")):
                raise Exception("Connection Loss")
            _ = tokenRing.receber()
            jogo.estado = Estado.FIM_DE_JOGO

        elif jogo.estado == Estado.DERROTA:
            print("\033[H\033[J", end="") 
            imprimir_suaMao(jogo)
            print("")
            print("\033[1;31m", end="")
            print(f"O JOGADOR {vencedorHostname} FOI O VENCEDOR!")
            print("\033[0m", end="", flush=True)
            jogo.estado = Estado.FIM_DE_JOGO

        else:
            raise Exception("Erro desconhecido.")
    
    print("Aperte qualquer botão para fechar o jogo...")
    _ = input("")
    sys.exit(0)

jogo_principal()
