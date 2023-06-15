#!/usr/bin/python3

import socket # importa o módulo de sockets

# Será lido do arquivo dalmuti.ini
hostnameFrom = 'h1'  # Hostname de quem você recebe. Será convertido para o endereço IP
hostnameTo = 'h1'  # Hostname de quem você envia. Será convertido para o endereço IP

def setup_connection (porta):
    #
    #
    #
    ip = socket.gethostbyname(socket.gethostname())
    UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPsocket.bind((ip, porta))
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

# Exemplo: SERVIDOR RECEBENDO
# UDPsocket = setup_connection(7304)
# while(True):
    # (data_str, ip_addr) = recv_from(UDPsocket, 2048)
    # print(data_str.decode('utf-8'))


# Exemplo: CLIENT ENVIANDO
# UDPsocket = setup_connection(7304)
# send_to(UDPsocket, "Ola", socket.gethostbyname(hostnameTo), 7304);   
    
