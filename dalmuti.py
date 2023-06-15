#!/usr/bin/python3

import socket # importa o módulo de sockets


def setup_connection ():
    #
    #
    #
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_to (socket, msg, ip_addr, port):
    # envia a mensagem pelo socket como uma string na codificação UTF-8
    # para a porta e endereço IPv4 passados como parâmetro
    socket.sendto(bytes(msg, "utf-8"), (ip_addr, port))

def recv_from (socket, buffer_size):
    # caso o tamanho do buffer não seja um valor (numérico) inteiro
    if (not buffer_size.is_integer())
        # atribua um valor padrão (2048 nesse caso)
        buffer_size = 2048
    #
    (data_str, ip_addr) = socket.recvfrom(bytes())
    return (data_str, ip_addr) # retorna tupla com mensagem, e IP de origrm

def jogo_principal ():
    while (jogo.estado != jogo.FIM_JOGO) {
        imprimir_tela()
        estado = jogo.estado
        if estado == jogo.ESPERANDO:
            pass # ...
        elif estado == jogo.TURNO_OUTRO:
            pass # ...
        else
            pass # ...
    }

jogo_principal()
