import random
import copy

LINHAS, COLUNAS = 7, 7

def gerar_posicoes_validas():
    return [(i, j) for i in range(1, LINHAS - 1) for j in range(1, COLUNAS - 1)]

def distancia(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

# Posições permitidas para as "portas"
def get_posicoes_porta():
    posicoes = []
    for j in range(1, COLUNAS - 1):  # topo e base
        posicoes.append((0, j))  # topo
        posicoes.append((LINHAS - 1, j))  # base
    for i in range(1, LINHAS - 1):  # laterais
        posicoes.append((i, 0))  # esquerda
        posicoes.append((i, COLUNAS - 1))  # direita
    return posicoes

def gerar_mapa():
    while True:
        # Inicializa mapa com paredes
        mapa = [['P' for _ in range(COLUNAS)] for _ in range(LINHAS)]

        # Adiciona áreas internas como células vazias
        for i in range(1, LINHAS - 1):
            for j in range(1, COLUNAS - 1):
                mapa[i][j] = 'V'

        # Escolher duas posições de porta diferentes para J e S
        posicoes_porta = get_posicoes_porta()
        pos_jogador = random.choice(posicoes_porta)
        posicoes_porta.remove(pos_jogador)
        pos_saida = random.choice(posicoes_porta)

        mapa[pos_jogador[0]][pos_jogador[1]] = 'J'
        mapa[pos_saida[0]][pos_saida[1]] = 'S'

        # Lista de posições livres (internas)
        posicoes_livres = gerar_posicoes_validas()
        random.shuffle(posicoes_livres)

        # Inimigos (3–5), com distância mínima entre si
        inimigos = []
        for _ in range(random.randint(3, 5)):
            for pos in posicoes_livres:
                if all(distancia(pos, outro) >= 2 for outro in inimigos):
                    inimigos.append(pos)
                    mapa[pos[0]][pos[1]] = 'I'
                    posicoes_livres.remove(pos)
                    break

        # Baús (1–3)
        for _ in range(random.randint(1, 3)):
            if not posicoes_livres:
                break
            pos_bau = posicoes_livres.pop()
            mapa[pos_bau[0]][pos_bau[1]] = 'B'

        # Armadilhas (2), longe do jogador
        for _ in range(2):
            for pos in posicoes_livres:
                if distancia(pos, pos_jogador) >= 2:
                    mapa[pos[0]][pos[1]] = 'T'
                    posicoes_livres.remove(pos)
                    break

        return mapa

mapa_gerado = gerar_mapa()
for linha in mapa_gerado:
    print(' '.join(linha))
