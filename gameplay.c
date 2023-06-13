#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>

#include "readconfig.h"
#include "ringconn.h"

#ifndef PORT
#define PORT 18086

int main () {
    
    read_config_file("dalmuti.ini");
    
    
    
    return 0;
}
