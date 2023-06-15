#!/usr/bin/python3

import socket # importa o módulo de sockets
import thread
from enum import Enum

import readconfig
import tokenring

# Será lido do arquivo dalmuti.ini
hostnameFrom = 'h1'  # Hostname de quem você recebe. Será convertido para o endereço IP
hostnameTo = 'h1'  # Hostname de quem você envia. Será convertido para o endereço IP
PORT = 7304
have_token = False
sendLock = Lock()
messageQueue = queue.Queue()
my_addr = socket.gethostbyname(socket.gethostname())

def receiveManager(UDPsocket):
        while(True):
            (data_str, ip_addr) = recv_from(UDPsocket, PORT)
            if data["Event"] == "Token":
                # Pega permissao de enviar mensagens
                break

            if data["Event"] == "Desligamento":
                # Mensagem especial de desligamento da rede
                # Passa pro proximo e da exit
                # função_exit(0)
                pass

            if data["To"] == my_addr:
                # Se a thread principal nao funcionar,
                # essa thread trava aqui e a rede em anel trava
                messageQueue.put(data_str, block=True)

            if data["From"] == my_addr:
                # Remove do anel
                sendLock.release()
            else:
                send_to(UDPsocket, data_str, hostnameTo, PORT)

def enviar(data):
    if have_token == False:
        return False
    send_to(UDPsocket, json.dumps(data), next_adrr, PORT)
    sendLock.acquire()
    return True

def receber():
    return messageQueue.get(block=True)

def setup_connection (porta):
    #
    #
    #
    UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPsocket.bind((my_addr, porta))
    return UDPsocket


def send_to (socket, msg, ip_addr, port):
    # envia a mensagem pelo socket como uma string na codificação UTF-8
    # para a porta e endereço IPv4 passados como parâmetro
    socket.sendto(bytes(msg, "utf-8"), (ip_addr, port))

def recv_from (socket, buffer_size):
    # caso o tamanho do buffer não seja um valor (numérico) inteiro
    #
    (data_str, ip_addr) = socket.recvfrom(buffer_size)
    return (data_str, ip_addr) # retorna tupla com mensagem, e IP de origrm

class Estados(Enum):
    ESPERANDO = 0  # Esperando todo mundo se conectar
    TURNO_DE_OUTRO = 1
    MEU_TURNO = 2
    VITORIA = 3
    DERROTA = 4
    FIM_DE_JOGO = 5

class Jogo:


    def __init__(self) -> None:
        self.estado = Estados.ESPERANDO
        self.turno = ""
        self.minhaMao = []

def inicializa_jogo ():
    pass

def jogo_principal ():
    while (jogo.estado != jogo.FIM_JOGO);
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
