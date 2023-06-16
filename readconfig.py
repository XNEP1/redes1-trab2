import configparser
import socket
import re

def read_config (filename):
    config = configparser.ConfigParser()
    config.read(filename)
    
    hosts = []
    current_machine = None
    repeated_local_host = False
    
    # seção para rastrear no config (seção padrão é 'DEFAULT')
    connections = 'Connections'
    
    try:
        if connections in config:
            for key in config[connections]:
                try:
                    key_type = 0
                    # verifica se a chave contém 'addr' ou 'port' 
                    if re.search('addr', key, re.IGNORECASE) != None:
                        key_type = 1
                    elif re.search('port', key, re.IGNORECASE) != None:
                        key_type = 2
                    else: # caso não tenha, siga adiante:
                        continue
                    # regex para selecionar substring de dígitos da chave 
                    grp = re.search(r'\d+', key)
                    if grp is None:
                        continue
                    i = int(grp.group())
                    
                    if (not i in hosts):
                        hosts[i] = {}
                    elif (not isinstance(hosts[i], (dict))): # (dict,set)
                        hosts[i] = {}
                    
                    if key_type == 1:
                        hosts[i]['addr'] = (config[connections][key])
                    elif key_type == 2:
                        hosts[i]['port'] = (config[connections][key])
                except Exception: # Exception as e:
                    pass
        
        local_host = socket.gethostname()
        for host in hosts:
            if hosts[host] == local_host:
                if current_machine != None:
                    repeated_local_host = True
                current_machine = host
            
            # caso houver hostnames repetidos:
                #
            
    except Exception: # Exception as e:
        pass
    
    return hosts
