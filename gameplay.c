#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>

#include "readconfig.h"
#include "ringconn.h"

#ifndef PORT
#define PORT 18086

int main () {
    
    int socket_options = 1;
    struct sockaddr_in address;
    
    read_config_file("dalmuti.ini");
    
    // int fd = socket(int domain, int type, int protocol);
    // * AF_LOCAL domain for local communication (same host)
    // * AF_INET  domain for IPv4 connection between different hosts
    // * AF_INET6 domain for IPv6 connection between different hosts
    // Protocol is the protocol field on the IP header 
    // * 0 for IP (Internet Protocol)
    
    //int socket_fd = socket(AF_LOCAL, SOCK_DGRAM, 0); 
    int socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_fd < 0) {
        perror("nao foi possivel criar um socket\n");
        return 1;
    }
    
    if (setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, 
            &socket_options, sizeof(socket_options)) != 0) {
        perror("nao foi possivel configurar as opcoes do socket\n");
        return 1;
    }
    
    // typedef struct in_addr {uint32_t s_addr;} in_addr_t;
    address.sin_family = AF_INET;
    address.sin_port = htons(PORT);
    address.sin_addr.s_addr = INADDR_LOOPBACK; //INADDR_ANY; 
    //address.sin_addr.s_addr = htonl(0x7f000001);
    //address.sin_addr = inet_addr("127.0.0.1"); 
    
    if (bind(socket_fd, (struct sockaddr*) &address, sizeof(address)) < 0) {
        perror("nao foi possivel crirar uma conexao com o socket\n");
        return 1;
    }
    
    send();
    
    return 0;
}
