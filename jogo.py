import pygame
import random
import copy
from collections import deque

# ========== CONFIGURAÇÃO ==========
LINHAS = random.randint(12, 18)
COLUNAS = random.randint(12, 18)
AREA_MAPA = LINHAS * COLUNAS
TAMANHO_CELULA = 40
LARGURA_TELA = COLUNAS * TAMANHO_CELULA
ALTURA_TELA = LINHAS * TAMANHO_CELULA

# Cores para os elementos
CORES = {
    'P': (100, 100, 100),      # Parede
    'V': (255, 255, 255),      # Espaço vazio
    'J': (0, 0, 255),          # Jogador
    'S': (0, 200, 0),          # Saída
    'I': (200, 0, 0),          # Inimigo
    'B': (255, 215, 0),        # Baú
    'T': (0, 0, 0),            # Armadilha
}

# ========== FUNÇÕES UTILITÁRIAS ==========
def get_posicoes_porta():
    posicoes = []
    for j in range(1, COLUNAS - 1):
        posicoes.append((0, j))
        posicoes.append((LINHAS - 1, j))
    for i in range(1, LINHAS - 1):
        posicoes.append((i, 0))
        posicoes.append((i, COLUNAS - 1))
    return posicoes

def distancia_manhattan(p1, p2):
    """Calcula a distância de Manhattan entre dois pontos."""
    if not p1 or not p2:
        return 0
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def existe_caminho(mapa, inicio, fim):
    if not inicio or not fim: return False
    
    fila = deque([inicio])
    visitados = {inicio}
    celulas_passaveis = {'V', 'B', 'S'}

    while fila:
        x, y = fila.popleft()
        if (x, y) == fim:
            return True

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < LINHAS and 0 <= ny < COLUNAS and (nx, ny) not in visitados:
                if (nx, ny) == fim or mapa[nx][ny] in celulas_passaveis:
                    visitados.add((nx, ny))
                    fila.append((nx, ny))
    return False

# ========== FUNÇÕES DE GERAÇÃO (BACKTRACKING) ==========

def obter_posicoes_disponiveis(mapa):
    posicoes = [(r, c) for r in range(1, LINHAS - 1) for c in range(1, COLUNAS - 1) if mapa[r][c] == 'V']
    random.shuffle(posicoes)
    return posicoes

def verificar_caminhos_criticos(mapa, contexto):
    """Verifica as restrições de caminho caras APÓS uma solução completa ser encontrada."""
    pos_jogador = contexto.get('JOGADOR')
    pos_chave = contexto.get('CHAVE')
    pos_saida = contexto.get('SAIDA')

    # Garante que o jogador pode chegar à chave
    if not existe_caminho(mapa, pos_jogador, pos_chave):
        print("Falha na validação final: Sem caminho do Jogador para a Chave.")
        return False
        
    # Garante que, da chave, é possível chegar à saída
    if not existe_caminho(mapa, pos_chave, pos_saida):
        print("Falha na validação final: Sem caminho da Chave para a Saída.")
        return False
        
    # Se todos os caminhos críticos existem, a solução é válida.
    return True

def eh_caminho_valido_parcial(mapa, contexto):
    pos_jogador = contexto.get('JOGADOR')
    pos_chave = contexto.get('CHAVE')
    pos_saida = contexto.get('SAIDA')

    if pos_jogador and pos_chave and not existe_caminho(mapa, pos_jogador, pos_chave):
        return False
    if pos_chave and pos_saida and not existe_caminho(mapa, pos_chave, pos_saida):
        return False
    return True

def eh_distribuicao_valida(contexto, tipo_item_atual, pos_atual):
    """NOVA FUNÇÃO: Verifica se a distância entre os itens é boa."""
    pos_jogador = contexto.get('JOGADOR')
    
    # Itens não podem estar muito perto do jogador
    MIN_DIST_JOGADOR = 3
    if pos_jogador and tipo_item_atual not in ['JOGADOR', 'SAIDA']:
        if distancia_manhattan(pos_atual, pos_jogador) < MIN_DIST_JOGADOR:
            return False

    # Regras específicas para a Chave e a Espada
    if tipo_item_atual == 'CHAVE':
        pos_espada = contexto.get('ESPADA')
        if pos_espada and distancia_manhattan(pos_atual, pos_espada) < 5:
            return False # Chave e Espada não podem estar lado a lado
            
    if tipo_item_atual == 'ESPADA':
        pos_chave = contexto.get('CHAVE')
        if pos_chave and distancia_manhattan(pos_atual, pos_chave) < 5:
            return False
        
    if tipo_item_atual.startswith('BAU') or tipo_item_atual in ['CHAVE', 'ESPADA']:
        for tipo, pos in contexto.items():
            if (tipo.startswith('BAU') or tipo in ['CHAVE', 'ESPADA']) and tipo != tipo_item_atual:
                if distancia_manhattan(pos_atual, pos) < 3:
                    return False

    return True

# Em ========== FUNÇÕES DE GERAÇÃO (BACKTRACKING) ==========

def resolver_backtracking(mapa, itens_a_colocar, contexto, estado_busca):
    """Função recursiva que tenta posicionar os itens no mapa. (VERSÃO COM FUSÍVEL DE SEGURANÇA)"""
    
    # ===== NOSSO FUSÍVEL DE SEGURANÇA =====
    estado_busca['passos'] += 1
    if estado_busca['passos'] > estado_busca['limite_passos']:
        return False, None, None # ABORTAR! A busca está demorando demais.

    if not itens_a_colocar:
        return True, mapa, contexto

    item_atual, tipo_item = itens_a_colocar[0]
    
    # ... (o resto da lógica da função, como get_posicoes_porta, continua igual) ...
    if tipo_item in ['JOGADOR', 'SAIDA']:
        posicoes_candidatas = get_posicoes_porta()
        random.shuffle(posicoes_candidatas)
    else:
        posicoes_candidatas = obter_posicoes_disponiveis(mapa)

    for pos in posicoes_candidatas:
        r, c = pos
        char_original = mapa[r][c]
        pode_colocar = (tipo_item in ['JOGADOR', 'SAIDA'] and char_original == 'P') or \
                       (tipo_item not in ['JOGADOR', 'SAIDA'] and char_original == 'V')
        
        if pode_colocar:
            mapa[r][c] = item_atual
            contexto[tipo_item] = pos
            
            if eh_distribuicao_valida(contexto, tipo_item, pos):
                # Importante: Passe o 'estado_busca' na chamada recursiva!
                sucesso, mapa_final, contexto_final = resolver_backtracking(mapa, itens_a_colocar[1:], contexto, estado_busca)
                if sucesso:
                    return True, mapa_final, contexto_final

            # Backtrack
            mapa[r][c] = char_original
            del contexto[tipo_item]

    return False, None, None

def gerar_mapa_com_backtracking():
    """Função principal para iniciar a geração do mapa. (VERSÃO FINAL OTIMIZADA COM FUSÍVEL)"""
    print("Iniciando geração com Backtracking e regras de distribuição...")
    
    max_tentativas = 10 
    tentativas = 0

    while tentativas < max_tentativas:
        tentativas += 1
        
        # ... (lógica de criação do mapa_base e itens_para_colocar continua igual) ...
        mapa_base = [['P' for _ in range(COLUNAS)] for _ in range(LINHAS)]
        for i in range(1, LINHAS - 1):
            for j in range(1, COLUNAS - 1):
                mapa_base[i][j] = 'V'
        
        # AQUI ESTÁ A DENSIDADE ALTA QUE CAUSA O PROBLEMA
        num_inimigos = int(round((AREA_MAPA / 10) * 1.1))
        num_baus_extras = int(round((AREA_MAPA / 15) * 1.1)) 

        itens_para_colocar = [
            ('J', 'JOGADOR'), ('S', 'SAIDA'), ('B', 'CHAVE'), ('B', 'ESPADA')
        ]
        itens_para_colocar.extend([('B', f'BAU_{i}') for i in range(num_baus_extras)])
        itens_para_colocar.extend([('I', f'INIMIGO_{i}') for i in range(num_inimigos)])
        itens_para_colocar.extend([('T', f'ARMADILHA_{i}') for i in range(2)])
        
        itens_essenciais = itens_para_colocar[:4]
        itens_randomizaveis = itens_para_colocar[4:]
        random.shuffle(itens_randomizaveis)
        itens_para_colocar = itens_essenciais + itens_randomizaveis

        # ===== CRIAÇÃO DO ESTADO DE BUSCA PARA CADA TENTATIVA =====
        estado_busca = {
            'passos': 0,
            'limite_passos': 500  # Limite de segurança. Ajuste se necessário.
        }
        print(f"Tentativa de geração nº {tentativas} (limite de {estado_busca['limite_passos']} passos)...")
        
        # Passe o 'estado_busca' para a função
        sucesso_posicionamento, mapa_potencial, contexto_potencial = resolver_backtracking(
            copy.deepcopy(mapa_base), itens_para_colocar, {}, estado_busca
        )

        # Adiciona uma verificação para saber se o limite foi atingido
        if estado_busca['passos'] > estado_busca['limite_passos']:
            print(f"Tentativa {tentativas} abortada: Limite de passos de busca atingido.")
            continue # Pula para a próxima tentativa

        if sucesso_posicionamento and verificar_caminhos_criticos(mapa_potencial, contexto_potencial):
            print("Mapa válido gerado e validado com sucesso!")
            # ... (resto da lógica para retornar o mapa e jogador) ...
            pos_jogador = contexto_potencial['JOGADOR']
            jogador = {
                "x": pos_jogador[0], "y": pos_jogador[1], "tem_chave": False,
                "tem_espada": False, "vida_espada": 3, "vida": 3
            }
            bau_com_chave = contexto_potencial['CHAVE']
            bau_com_espada = contexto_potencial['ESPADA']
            return mapa_potencial, jogador, bau_com_chave, bau_com_espada
        else:
            if sucesso_posicionamento:
                print(f"Posicionamento da tentativa {tentativas} bem-sucedido, mas falhou na validação de caminhos.")
    
    # Esta mensagem agora será exibida corretamente quando for impossível gerar o mapa
    print(f"\nNÃO FOI POSSÍVEL GERAR UM MAPA VÁLIDO APÓS {max_tentativas} TENTATIVAS.")
    print("A combinação de tamanho do mapa, número de itens e restrições de distância provavelmente torna a geração impossível.")
    print("Sugestão: Aumente o mapa, reduza o número de itens ou diminua a distância mínima entre eles.")
    pygame.quit()
    exit()

# ========== LÓGICA DO JOGO E MOVIMENTO ==========
def mover(dx, dy, jogador, mapa, bau_com_chave, bau_com_espada):
    x_atual, y_atual = jogador["x"], jogador["y"]
    nx, ny = jogador["x"] + dx, jogador["y"] + dy

    if 0 <= nx < LINHAS and 0 <= ny < COLUNAS:
        destino = mapa[nx][ny]

        if destino == 'P':
            return
        elif destino == 'S':
            if jogador["tem_chave"]:
                print("\033[33mVocê venceu!\033[0m")  # Amarelo
                pygame.quit()
                exit()
            else:
                print("Você precisa da chave para sair!")
                return
        elif destino == 'B':
            print("Você encontrou um baú!")
            if (nx, ny) == bau_com_chave:
                jogador["tem_chave"] = True
                print("\033[33mVocê encontrou a CHAVE!\033[0m")  # Amarelo
            elif(nx, ny) == bau_com_espada:
                jogador["tem_espada"] = True
                print("\033[34mVocê encontrou a ESPADA!, de durabilidade 3\033[0m")  # Azul
            else:
                print("Este baú está vazio.")
            mapa[nx][ny] = 'V'

        elif destino == 'I':
            print("você encontrou um inimigo!")
            if jogador["tem_espada"]:
                mapa[nx][ny] = 'V'
                jogador["vida_espada"] -= 1
                print("você eliminou um inimigo, durabilidade: ", jogador["vida_espada"])
                if jogador["vida_espada"] <= 0:
                    jogador["tem_espada"] = False
                    print("Sua espada quebrou")
            else:
                jogador["vida"] -= 1
                print("você foi atacado!\nVidas restantes:", jogador["vida"])
                if jogador["vida"] <= 0:
                    print("\033[31mVocê perdeu todas as vidas!\nGAME OVER!\033[0m")  # Vermelho
                    pygame.quit()
                    exit()
        elif destino == 'T':
            jogador["vida"] -= 2
            print("você caiu em uma armadilha!\nVidas restantes:", jogador["vida"])
            if jogador["vida"] <= 0:
                print("\033[31mVocê perdeu todas as vidas!\nGAME OVER!\033[0m")  # Vermelho
                pygame.quit()
                exit()
        elif destino == 'V':
            mapa[nx][ny] = 'J'
            mapa[x_atual][y_atual] = 'V'
            jogador["x"], jogador["y"] = nx, ny
            return

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
            if tipo != 'V':
                texto = fonte.render(tipo, True, (255, 255, 255) if tipo in ['I', 'J', 'T'] else (0, 0, 0))
                rect_texto = texto.get_rect(center=(x + TAMANHO_CELULA // 2, y + TAMANHO_CELULA // 2))
                tela.blit(texto, rect_texto)

# ========== LOOP PRINCIPAL ==========
def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Mapa Gerado com Backtracking v2")
    fonte = pygame.font.SysFont(None, 36)

    mapa, jogador, bau_com_chave, bau_com_espada = gerar_mapa_com_backtracking()
    
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
                    mapa, jogador, bau_com_chave, bau_com_espada = gerar_mapa_com_backtracking()
                elif evento.key == pygame.K_UP:
                    mover(-1, 0, jogador, mapa, bau_com_chave, bau_com_espada)
                elif evento.key == pygame.K_DOWN:
                    mover(1, 0, jogador, mapa, bau_com_chave, bau_com_espada)
                elif evento.key == pygame.K_LEFT:
                    mover(0, -1, jogador, mapa, bau_com_chave, bau_com_espada)
                elif evento.key == pygame.K_RIGHT:
                    mover(0, 1, jogador, mapa, bau_com_chave, bau_com_espada)

        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()