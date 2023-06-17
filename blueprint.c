#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>

// =================================================
// fila.c
// =================================================

// Vai precisar de uma fila que tenha mutex pra proteger de multi threads
// O emfilera() deve ser bloqueante até que tenha alguma vaga na fila
// O desemfilera() deve ser bloquante até que tenha algum item na fila

emfilera{
    sem_down(sem_vagas)
        pthread_mutex_lock(mutex)
    // coloca dado
    pthread_mutex_unlock(mutex)
        sem_up(sem_itens)}

desemfilera{
    sem_down(sem_itens)
        pthread_mutex_lock(mutex)
    // pega dado
    pthread_mutex_unlock(mutex)
        sem_up(sem_vagas)}

// =================================================
// token_ring.c
// =================================================

token_ring_t *
token_ring_init(char *device, char *hostnameFrom, char *hostnameTo, int porta);
int socket(char *device, char *hostname, int porta);
int recebe(token_ring_t *tr, messagem_t *data);
int envia_e_passa_token(token_ring_t *tr, messagem_t *data);

typedef struct token_ring_t {
    int socket;
    struct sockaddr_in FromAddr;  // Endereço de onde recebemos mensagens
    struct sockaddr_in ToAddr;    // Endereço para onde enviamos mensagens
    // preemcha conforme o necessario
} token_ring_t;

void getAddrFromHostname(struct sockaddr *addr, char *hostname) {
    struct addrinfo host, res;
    memset(&host, 0, sizeof(struct addrinfo));
    host.ai_family = AF_INET;
    host.ai_socktype = SOCK_DGRAM;
    if (getaddrinfo(hostname, NULL, &host, &res) != 0) {
        fprintf(stderr, "Erro ao obter informações do endereço\n");
        exit(1);
    }

    memcpy(addr, res.ai_addr, sizeof(struct sockaddr));
}

token_ring_t *token_ring_init(char *device, char *hostnameFrom, char *hostnameTo, int porta) {
    token_ring_t *tokenRing = malloc(sizeof(token_ring_t));

    char *hostname_desse_pc = função_que_pega_nome_do_pc();
    // device tambpem é o desse pc
    tokenRing->socket = socket(device, hostname_desse_pc, porta);

    // configura para quem vamos enviar

    tokenRing->ToAddr.sin_family = AF_INET;
    tokenRing->ToAddr.sin_port = htons(porta);
    tokenRing->ToAddr.sin_addr.s_addr = getAddrFromHostname(hostnameTo);

    tokenRing->FromAddr.sin_family = AF_INET;
    tokenRing->FromAddr.sin_port = htons(porta);
    tokenRing->FromAddr.sin_addr.s_addr = getAddrFromHostname(hostnameFrom);
}

void repassador_de_mensagens(void *arg) {
    token_ring_t *tr = (token_ring_t *)arg;
    messagem_t *data;
    for (;;) {
        if (recvfrom(tr->socket, data, sizeof(messagem_t), 0, &addr, &size) != 0) {
            // crasha ou
            return -1;
        }

        if (data->destino != meu_addr) {  // Essa comparação desse jeito não funciona. Precisa ser implementada
            if (sendto(tr->socket, data, sizeof(messagem_t), 0, (struct sockaddr *)tr->ToAddr, sizeof(tr->ToAddr)) != 0) {
                // Crasha o programa ou faz timeout ou \/
                return -1;
            }
        } else {
            emfilera(data);  // Sim, vai precisar de uma pilha.
        }
    }
}

int recebe(token_ring_t *tr, messagem_t *data) {
    desemfilera(data);
}
int envia_e_passa_token(token_ring_t *tr, messagem_t *data) {
    if (sendto(tr->socket, data, sizeof(messagem_t), 0, (struct sockaddr *)tr->ToAddr, sizeof(tr->ToAddr)) != 0) {
        // Crasha o programa ou faz timeout ou \/
        return -1;
    }
}

// =================================================
// jogo.c
// =================================================

init_game();
interpreta(&game, data);
print_tela_do_jogo();
jogo_vitoria();
jogo_derrota();

enum estados {
    ESPERANDO,  // Esperando todo mundo se conectar
    TURNO_DE_OUTRO,
    MEU_TURNO,
    VITORIA,
    DERROTA,
    FIM_DE_JOGO
};

enum eventos {
    TOKEN,
    DESLIGAMENTO,
    JOGADA,
    VITORIA,
};

typedef struct messagem_t {
    sockaddr_in destino;
    char evento;      // diz o que aconteceu
    char carta;       // sobre qual carta
    char quantidade;  // qual a quantidade de cartas
    // preemcha conforme o necessario
} messagem_t;

typedef struct game_t {
    // variáveis do jogo
    char estado;  //
    char turno;
    struct mao *mao;
} game_t;

int o_jogo(void) {
    // conecta
    token_ring_t *token_ring = token_ring_init(device, hostnameFrom, hostnameTo, porta);
    messagem_t *data;
    game_t *game = init_game();
    pthread_t recebedor;

    pthread_init(recebedor, repassador_de_mensagens, (void *)token_ring);

    while (game->estado != FIM_DE_JOGO) {
        print_tela_do_jogo();
        switch (game->estado) {
            case ESPERANDO:
                recebe(&token_ring, data);  // primeira mensagem
                // ^ Bloqueante até receber uma mensagem
                game->estado = interpreta(game, data);  // atualiza as variais do jogo
                break;

            case TURNO_DE_OUTRO:
                recebe(&token_ring, data);
                // ^ Bloqueante até receber uma mensagem
                game->estado = interpreta(game, data);  // atualiza as variais do jogo
                break;

            case MEU_TURNO:

                escolhe_acao(game, data);  // atualiza as variais do jogo e prepara uma mensagem de dados.
                // ^ Bloqueia até o usuário escolhear a ação

                envia_e_passa_token(&token_ring, data);
                // ^ Bloqueante até terminar de enviar uma mensagem
                break;

            case VITORIA:
                jogo_vitoria();  // printa "vitoria" na tela, seila
                break;           // fecha o jogo

            case DERROTA:
                jogo_derrota();  // printa "derrota"
                return 0;        // fecha o jogo
        }
    }

    // Da free() em tudo

    pthread_cancel(recebedor);
}