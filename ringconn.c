//#define _BSD_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include "ringconn.h"

int create_connection (char *local_ip_addr) {
    
    int socket_fd = -1;
    int socket_options = 1;
    struct sockaddr_in address;
    
    // * AF_LOCAL domain for local communication (same host, on filesystem)
    // * AF_INET  domain for IPv4 connection between different hosts
    // * AF_INET6 domain for IPv6 connection between different hosts
    // Protocol is the protocol field on the IP header 
    // * 0 for IP (Internet Protocol)
    
    //int socket_fd = socket(AF_LOCAL, SOCK_DGRAM, 0); 
    socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    
    if (socket_fd < 0) {
        //perror("nao foi possivel criar um socket\n");
        return -1;
    }
    
    if (setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, 
            &socket_options, sizeof(socket_options)) != 0) {
        //perror("nao foi possivel configurar as opcoes do socket\n");
        return -2;
    }
    
    //if (inet_aton(ip_addr, &address.sin_port) != 0)
    
    // typedef struct in_addr {uint32_t s_addr;} in_addr_t;
    address.sin_family = AF_INET;
    address.sin_port = htons(PORT);
    
    if (!local_ip_addr || !inet_aton(local_ip_addr, &address.sin_addr)) {
        address.sin_addr.s_addr = INADDR_ANY;
    }
    
    //address.sin_addr.s_addr = INADDR_LOOPBACK; //INADDR_ANY;
    //address.sin_addr.s_addr = htonl(0x7f000001);
    //address.sin_addr = inet_addr("127.0.0.1"); 
    
    if (bind(socket_fd, (struct sockaddr*) &address, sizeof(address)) < 0) {
        //perror("nao foi possivel crirar uma conexao com o socket\n");
        return -3;
    }
    
    
    
    return socket_fd;
}

int send_msg_to (int socket_fd, void *msg, size_t msg_length) {
    
    send(socket_fd, msg, msg_length, 0);
    
    return 0;
}
