import pygame
import random
import copy
from collections import deque

# ========== CONFIGURAÇÃO ==========
LINHAS = random.randint(10, 20)
COLUNAS = random.randint(10, 20)
AREA_MAPA = LINHAS * COLUNAS
TAMANHO_CELULA = 40
LARGURA_TELA = COLUNAS * TAMANHO_CELULA
ALTURA_TELA = LINHAS * TAMANHO_CELULA

# Cores para os elementos
CORES = {
    'P': (100, 100, 100),    # Parede
    'V': (255, 255, 255),    # Espaço vazio
    'J': (0, 0, 255),        # Jogador
    'S': (0, 200, 0),        # Saída
    'I': (200, 0, 0),        # Inimigo
    'B': (255, 215, 0),      # Baú
    'T': (0, 0, 0),          # Armadilha
}

# ========== FUNÇÕES DE GERAÇÃO ==========
def gerar_posicoes_validas():
    return [(i, j) for i in range(1, LINHAS - 1) for j in range(1, COLUNAS - 1)]

def distancia(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def get_posicoes_porta():
    posicoes = []
    for j in range(1, COLUNAS - 1):  # topo e base
        posicoes.append((0, j))
        posicoes.append((LINHAS - 1, j))
    for i in range(1, LINHAS - 1):  # esquerda e direita
        posicoes.append((i, 0))
        posicoes.append((i, COLUNAS - 1))
    return posicoes


def mover(dx, dy, jogador, mapa, bau_com_chave):
    x_atual, y_atual = jogador["x"], jogador["y"]
    nx, ny = jogador["x"] + dx, jogador["y"] + dy

    if 0 <= nx < LINHAS and 0 <= ny < COLUNAS:
        destino = mapa[nx][ny]

        if destino == 'P':
            return  # parede: sem movimento

        elif destino == 'S':
            if jogador["tem_chave"]:
                print("Você venceu!")
                pygame.quit()
                exit()
            else:
                print("Você precisa da chave para sair!")
                return

        elif destino == 'B':
            print("Você encontrou um baú!")
            if (nx, ny) == bau_com_chave:
                jogador["tem_chave"] = True
                print("Você encontrou a CHAVE!")
            # Remove o baú após abertura
            # mapa[nx][ny] = 'V'
            # jogador["x"], jogador["y"] = nx, ny

        elif destino == 'V':
            mapa[nx][ny] = 'J'
            mapa[x_atual][y_atual] = 'V'
            jogador["x"], jogador["y"] = nx, ny
            return


def gerar_mapa():
    while True:
        mapa = [['P' for _ in range(COLUNAS)] for _ in range(LINHAS)]
        for i in range(1, LINHAS - 1):
            for j in range(1, COLUNAS - 1):
                mapa[i][j] = 'V'

        posicoes_porta = get_posicoes_porta()
        pos_jogador = random.choice(posicoes_porta)
        posicoes_porta.remove(pos_jogador)
        pos_saida = random.choice(posicoes_porta)

        mapa[pos_jogador[0]][pos_jogador[1]] = 'J'
        mapa[pos_saida[0]][pos_saida[1]] = 'S'

        jogador = {
            "x": pos_jogador[0],
            "y": pos_jogador[1],
            "tem_chave": False,
            "tem_espada": False,
            "vida": 3
        }

        posicoes_livres = gerar_posicoes_validas()
        random.shuffle(posicoes_livres)

        inimigos = []
        min_inimigos = int(round(AREA_MAPA / 10))
        max_inimigos = round(min_inimigos * 1.5)
        for _ in range(random.randint(min_inimigos, max_inimigos)):
        # for _ in range(AREA_MAPA):
            for pos in posicoes_livres:
                if all(distancia(pos, outro) >= 3 for outro in inimigos):
                    inimigos.append(pos)
                    mapa[pos[0]][pos[1]] = 'I'
                    posicoes_livres.remove(pos)
                    break

        baus = []
        min_baus = int(round(AREA_MAPA / 20))
        max_baus = round(min_baus * 1.5)
        for _ in range(random.randint(min_baus, max_baus)):
            if not posicoes_livres:
                break
            pos_bau = posicoes_livres.pop()
            mapa[pos_bau[0]][pos_bau[1]] = 'B'
            baus.append(pos_bau)

        bau_com_chave = random.choice(baus)

        for _ in range(2):
            for pos in posicoes_livres:
                if distancia(pos, pos_jogador) >= 2:
                    mapa[pos[0]][pos[1]] = 'T'
                    posicoes_livres.remove(pos)
                    break

        if existe_caminho(mapa, pos_jogador, pos_saida):
            return mapa, jogador, bau_com_chave


# ========== FUNÇÃO DE DESENHO ==========
def desenhar_mapa(tela, mapa, fonte):
    for i in range(LINHAS):
        for j in range(COLUNAS):
            tipo = mapa[i][j]
            cor = CORES.get(tipo, (0, 0, 0))
            x = j * TAMANHO_CELULA
            y = i * TAMANHO_CELULA

            pygame.draw.rect(tela, cor, (x, y, TAMANHO_CELULA, TAMANHO_CELULA))
            pygame.draw.rect(tela, (0, 0, 0), (x, y, TAMANHO_CELULA, TAMANHO_CELULA), 1)

            texto = fonte.render(tipo, True, (255, 255, 255) if tipo in ['I', 'J', 'T'] else (0, 0, 0))
            rect_texto = texto.get_rect(center=(x + TAMANHO_CELULA // 2, y + TAMANHO_CELULA // 2))
            tela.blit(texto, rect_texto)


def existe_caminho(mapa, pos_jogador, pos_saida):
    visitados = set()
    fila = deque()
    fila.append(pos_jogador)

    while fila:
        x, y = fila.popleft()
        if (x, y) == pos_saida:
            return True

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < LINHAS and 0 <= ny < COLUNAS:
                if mapa[nx][ny] in ['V', 'S']:  # Caminhos válidos (pode incluir B se quiser)
                    if (nx, ny) not in visitados:
                        visitados.add((nx, ny))
                        fila.append((nx, ny))
    return False


# ========== LOOP PRINCIPAL ==========
def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Mapa Gerado com CSP")
    fonte = pygame.font.SysFont(None, 36)

    mapa, jogador, bau_com_chave = gerar_mapa()
    clock = pygame.time.Clock()
    rodando = True

    while rodando:

        tela.fill((0, 0, 0))
        desenhar_mapa(tela, mapa, fonte)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    mapa, jogador, bau_com_chave = gerar_mapa()
                elif evento.key == pygame.K_UP:
                    mover(-1, 0, jogador, mapa, bau_com_chave)
                elif evento.key == pygame.K_DOWN:
                    mover(1, 0, jogador, mapa, bau_com_chave)
                elif evento.key == pygame.K_LEFT:
                    mover(0, -1, jogador, mapa, bau_com_chave)
                elif evento.key == pygame.K_RIGHT:
                    mover(0, 1, jogador, mapa, bau_com_chave)

        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
