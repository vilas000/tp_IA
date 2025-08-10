import pygame
import random
import copy
from collections import deque

# ========== CONFIGURAÇÃO ==========
# Define as dimensões do mapa (grid) com um tamanho aleatório para cada nova execução.
LINHAS = random.randint(12, 18)
COLUNAS = random.randint(12, 18)
# Calcula a área total do mapa, útil para determinar a densidade de itens.
AREA_MAPA = LINHAS * COLUNAS
# Define o tamanho em pixels de cada célula do grid.
TAMANHO_CELULA = 40
# Calcula a largura e altura da janela do jogo com base nas dimensões do mapa e no tamanho da célula.
LARGURA_TELA = COLUNAS * TAMANHO_CELULA
ALTURA_TELA = LINHAS * TAMANHO_CELULA

# Dicionário que mapeia o caractere de cada elemento do mapa a uma cor (em formato RGB).
CORES = {
    'P': (100, 100, 100),      # Parede (cinza)
    'V': (255, 255, 255),      # Espaço vazio (branco)
    'J': (0, 0, 255),          # Jogador (azul)
    'S': (0, 200, 0),          # Saída (verde)
    'I': (200, 0, 0),          # Inimigo (vermelho)
    'B': (255, 215, 0),        # Baú (dourado)
    'T': (0, 0, 0),            # Armadilha (preto)
}

# ========== FUNÇÕES UTILITÁRIAS ==========
def get_posicoes_porta():
    """Retorna uma lista de todas as posições válidas para portas (jogador/saída).
    
    Essas posições estão nas bordas do mapa, excluindo os cantos, para garantir
    que o jogador e a saída sempre comecem em uma parede externa.
    """
    posicoes = []
    # Itera sobre as colunas da primeira e última linha.
    for j in range(1, COLUNAS - 1):
        posicoes.append((0, j))
        posicoes.append((LINHAS - 1, j))
    # Itera sobre as linhas da primeira e última coluna.
    for i in range(1, LINHAS - 1):
        posicoes.append((i, 0))
        posicoes.append((i, COLUNAS - 1))
    return posicoes

def distancia_manhattan(p1, p2):
    """Calcula a distância de Manhattan entre dois pontos (p1 e p2)."""
    # Se um dos pontos não existir (None), retorna 0 para evitar erros.
    if not p1 or not p2:
        return 0
    # A fórmula é a soma das diferenças absolutas das coordenadas x e y.
    # Útil para medir a distância em um grid.
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def existe_caminho(mapa, inicio, fim):
    """Verifica se existe um caminho passável entre um ponto de início e um de fim.
    
    Usa o algoritmo de busca em largura (BFS) para encontrar o caminho.
    """
    if not inicio or not fim: return False
    
    # 'deque' é uma fila otimizada, ideal para BFS. Começa com o ponto de início.
    fila = deque([inicio])
    # 'visitados' armazena as células já exploradas para não entrar em loop.
    visitados = {inicio}
    # Define quais tipos de células são considerados passáveis.
    celulas_passaveis = {'V', 'B', 'S'}

    while fila:
        # Pega a próxima célula da fila para explorar.
        x, y = fila.popleft()
        
        # Se a célula atual é o destino, um caminho foi encontrado.
        if (x, y) == fim:
            return True

        # Explora os vizinhos (cima, baixo, esquerda, direita).
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            # Verifica se o vizinho está dentro dos limites do mapa e não foi visitado.
            if 0 <= nx < LINHAS and 0 <= ny < COLUNAS and (nx, ny) not in visitados:
                # Se o vizinho é o próprio fim ou uma célula passável...
                if (nx, ny) == fim or mapa[nx][ny] in celulas_passaveis:
                    # ...adiciona-o aos visitados e à fila para ser explorado.
                    visitados.add((nx, ny))
                    fila.append((nx, ny))
    # Se a fila esvaziar e o fim não for alcançado, não há caminho.
    return False

# ========== FUNÇÕES DE GERAÇÃO (BACKTRACKING) ==========

def obter_posicoes_disponiveis(mapa):
    """Retorna uma lista embaralhada de todas as posições vazias ('V') no interior do mapa."""
    posicoes = [(r, c) for r in range(1, LINHAS - 1) for c in range(1, COLUNAS - 1) if mapa[r][c] == 'V']
    random.shuffle(posicoes) # Embaralha para garantir aleatoriedade na colocação dos itens.
    return posicoes

def verificar_caminhos_criticos(mapa, contexto):
    """Verifica as restrições de caminho mais importantes APÓS uma solução completa ser encontrada.
    
    Esta é a validação final que garante que o mapa gerado é jogável e pode ser vencido.
    """
    pos_jogador = contexto.get('JOGADOR')
    pos_chave = contexto.get('CHAVE')
    pos_saida = contexto.get('SAIDA')

    # Garante que o jogador pode chegar até o baú com a chave.
    if not existe_caminho(mapa, pos_jogador, pos_chave):
        print("Falha na validação final: Sem caminho do Jogador para a Chave.")
        return False
        
    # Garante que, da posição da chave, é possível chegar até a saída.
    # Isso impede que a chave fique presa em uma área sem saída para o resto do mapa.
    if not existe_caminho(mapa, pos_chave, pos_saida):
        print("Falha na validação final: Sem caminho da Chave para a Saída.")
        return False
        
    # Se todos os caminhos críticos existem, a solução é válida.
    return True

def eh_caminho_valido_parcial(mapa, contexto):
    """
    (Função não utilizada no fluxo atual)
    Verifica se os caminhos parciais são válidos durante a geração.
    Foi provavelmente substituída pela verificação final `verificar_caminhos_criticos`
    por ser computacionalmente cara para ser chamada a cada passo.
    """
    pos_jogador = contexto.get('JOGADOR')
    pos_chave = contexto.get('CHAVE')
    pos_saida = contexto.get('SAIDA')

    if pos_jogador and pos_chave and not existe_caminho(mapa, pos_jogador, pos_chave):
        return False
    if pos_chave and pos_saida and not existe_caminho(mapa, pos_chave, pos_saida):
        return False
    return True

def eh_distribuicao_valida(contexto, tipo_item_atual, pos_atual):
    """Verifica se a distância entre os itens colocados segue as regras de bom design de mapa."""
    pos_jogador = contexto.get('JOGADOR')

    # Regra 1: Itens importantes não podem estar muito perto do ponto inicial do jogador.
    MIN_DIST_JOGADOR = 3
    if pos_jogador and tipo_item_atual not in ['JOGADOR', 'SAIDA']:
        if distancia_manhattan(pos_atual, pos_jogador) < MIN_DIST_JOGADOR:
            return False

    # Regra 2: A chave e a espada não podem estar muito próximas uma da outra.
    if tipo_item_atual == 'CHAVE':
        pos_espada = contexto.get('ESPADA')
        if pos_espada and distancia_manhattan(pos_atual, pos_espada) < 5:
            return False 
            
    if tipo_item_atual == 'ESPADA':
        pos_chave = contexto.get('CHAVE')
        if pos_chave and distancia_manhattan(pos_atual, pos_chave) < 5:
            return False
            
    # Regra 3: Baús e itens especiais (chave/espada) não devem ficar agrupados.
    if tipo_item_atual.startswith('BAU') or tipo_item_atual in ['CHAVE', 'ESPADA']:
        for tipo, pos in contexto.items():
            # Verifica contra outros baús ou itens, ignorando a comparação com ele mesmo.
            if (tipo.startswith('BAU') or tipo in ['CHAVE', 'ESPADA']) and tipo != tipo_item_atual:
                if distancia_manhattan(pos_atual, pos) < 3:
                    return False

    # Se todas as regras de distância forem satisfeitas, a posição é válida.
    return True

def resolver_backtracking(mapa, itens_a_colocar, contexto, estado_busca):
    """Função recursiva que tenta posicionar os itens no mapa usando a técnica de backtracking.
    
    Parâmetros:
    - mapa: O estado atual do grid.
    - itens_a_colocar: Lista de tuplas (char, tipo) dos itens que ainda faltam.
    - contexto: Dicionário que armazena as posições dos itens já colocados.
    - estado_busca: Dicionário para controlar o número de passos e evitar buscas infinitas.
    """
    
    # ===== FUSÍVEL DE SEGURANÇA =====
    # Incrementa o contador de passos. Se exceder o limite, a busca é abortada.
    # Isso previne que o programa congele se uma solução for muito difícil ou impossível de encontrar.
    estado_busca['passos'] += 1
    if estado_busca['passos'] > estado_busca['limite_passos']:
        return False, None, None # Aborta a busca.

    # Caso base da recursão: se não há mais itens para colocar, a solução foi encontrada.
    if not itens_a_colocar:
        return True, mapa, contexto

    # Pega o próximo item da lista para tentar posicioná-lo.
    item_atual, tipo_item = itens_a_colocar[0]
    
    # Define as possíveis posições para o item atual.
    if tipo_item in ['JOGADOR', 'SAIDA']:
        posicoes_candidatas = get_posicoes_porta() # Jogador e saída ficam nas bordas.
        random.shuffle(posicoes_candidatas)
    else:
        posicoes_candidatas = obter_posicoes_disponiveis(mapa) # Outros itens ficam no chão.

    # Tenta colocar o item em cada posição candidata.
    for pos in posicoes_candidatas:
        r, c = pos
        char_original = mapa[r][c]
        
        # Verifica se o item pode ser colocado na posição (porta na parede, item no chão).
        pode_colocar = (tipo_item in ['JOGADOR', 'SAIDA'] and char_original == 'P') or \
                       (tipo_item not in ['JOGADOR', 'SAIDA'] and char_original == 'V')
        
        if pode_colocar:
            # "Tenta" colocar o item: modifica o mapa e o contexto.
            mapa[r][c] = item_atual
            contexto[tipo_item] = pos
            
            # Verifica se essa nova distribuição de itens é válida de acordo com as regras de distância.
            if eh_distribuicao_valida(contexto, tipo_item, pos):
                # Se for válida, chama a função recursivamente para o resto dos itens.
                sucesso, mapa_final, contexto_final = resolver_backtracking(mapa, itens_a_colocar[1:], contexto, estado_busca)
                # Se a chamada recursiva foi bem-sucedida, propaga o sucesso para cima.
                if sucesso:
                    return True, mapa_final, contexto_final

            # Se a colocação não levou a uma solução (ou falhou na validação), desfaz a tentativa.
            # Este é o passo de "Backtrack".
            mapa[r][c] = char_original
            del contexto[tipo_item]

    # Se o loop terminar sem encontrar uma posição válida para o item atual, retorna falha.
    return False, None, None

def gerar_mapa_com_backtracking():
    """Função principal que orquestra a geração do mapa, com múltiplas tentativas e validação final."""
    print("Iniciando geração com Backtracking e regras de distribuição...")
    
    max_tentativas = 10 # Número máximo de vezes que o algoritmo tentará gerar um mapa válido.
    tentativas = 0

    while tentativas < max_tentativas:
        tentativas += 1
        
        # Cria um mapa base, com paredes nas bordas e chão vazio no interior.
        mapa_base = [['P' for _ in range(COLUNAS)] for _ in range(LINHAS)]
        for i in range(1, LINHAS - 1):
            for j in range(1, COLUNAS - 1):
                mapa_base[i][j] = 'V'
        
        # Define a quantidade de inimigos e baús com base na área do mapa.
        # A densidade aqui pode tornar a geração difícil se for muito alta.
        num_inimigos = int(round((AREA_MAPA / 10) * 1.1))
        num_baus_extras = int(round((AREA_MAPA / 10)))

        # Cria a lista de todos os itens que precisam ser posicionados.
        itens_para_colocar = [
            ('J', 'JOGADOR'), ('S', 'SAIDA'), ('B', 'CHAVE'), ('B', 'ESPADA')
        ]
        itens_para_colocar.extend([('B', f'BAU_{i}') for i in range(num_baus_extras)])
        itens_para_colocar.extend([('I', f'INIMIGO_{i}') for i in range(num_inimigos)])
        itens_para_colocar.extend([('T', f'ARMADILHA_{i}') for i in range(2)])
        
        # Separa os itens essenciais dos aleatórios para garantir que os mais importantes
        # sejam processados primeiro, e embaralha o resto.
        itens_essenciais = itens_para_colocar[:4]
        itens_randomizaveis = itens_para_colocar[4:]
        random.shuffle(itens_randomizaveis)
        itens_para_colocar = itens_essenciais + itens_randomizaveis

        # Cria um novo estado de busca para cada tentativa.
        estado_busca = {
            'passos': 0,
            'limite_passos': 500  # Limite de segurança.
        }
        print(f"Tentativa de geração nº {tentativas} (limite de {estado_busca['limite_passos']} passos)...")
        
        # Chama a função de backtracking para tentar encontrar uma solução.
        # Usa copy.deepcopy para não modificar o mapa_base original.
        sucesso_posicionamento, mapa_potencial, contexto_potencial = resolver_backtracking(
            copy.deepcopy(mapa_base), itens_para_colocar, {}, estado_busca
        )

        # Se a busca foi abortada por excesso de passos, informa e tenta novamente.
        if estado_busca['passos'] > estado_busca['limite_passos']:
            print(f"Tentativa {tentativas} abortada: Limite de passos de busca atingido.")
            continue # Pula para a próxima iteração do loop de tentativas.

        # Se o posicionamento foi um sucesso, faz a validação final dos caminhos críticos.
        if sucesso_posicionamento and verificar_caminhos_criticos(mapa_potencial, contexto_potencial):
            print("Mapa válido gerado e validado com sucesso!")
            # Extrai as informações necessárias do contexto para o estado inicial do jogo.
            pos_jogador = contexto_potencial['JOGADOR']
            jogador = {
                "x": pos_jogador[0], "y": pos_jogador[1], "tem_chave": False,
                "tem_espada": False, "vida_espada": 3, "vida": 3
            }
            bau_com_chave = contexto_potencial['CHAVE']
            bau_com_espada = contexto_potencial['ESPADA']
            return mapa_potencial, jogador, bau_com_chave, bau_com_espada
        else:
            # Informa se o posicionamento funcionou mas a validação de caminhos falhou.
            if sucesso_posicionamento:
                print(f"Posicionamento da tentativa {tentativas} bem-sucedido, mas falhou na validação de caminhos.")
    
    # Se o loop terminar sem gerar um mapa válido, encerra o programa com uma mensagem de erro.
    print(f"\nNÃO FOI POSSÍVEL GERAR UM MAPA VÁLIDO APÓS {max_tentativas} TENTATIVAS.")
    print("A combinação de tamanho do mapa, número de itens e restrições de distância provavelmente torna a geração impossível.")
    print("Sugestão: Aumente o mapa, reduza o número de itens ou diminua a distância mínima entre eles.")
    pygame.quit()
    exit()

# ========== LÓGICA DO JOGO E MOVIMENTO ==========
def mover(dx, dy, jogador, mapa, bau_com_chave, bau_com_espada):
    """Processa o movimento do jogador e as interações com os objetos do mapa."""
    x_atual, y_atual = jogador["x"], jogador["y"]
    nx, ny = jogador["x"] + dx, jogador["y"] + dy # Calcula a nova posição.

    # Garante que a nova posição está dentro dos limites do mapa.
    if 0 <= nx < LINHAS and 0 <= ny < COLUNAS:
        destino = mapa[nx][ny]

        if destino == 'P': # Bateu na parede
            return # Não faz nada.
        
        elif destino == 'S': # Chegou na saída
            if jogador["tem_chave"]:
                print("\033[33mVocê venceu!\033[0m") # Mensagem de vitória.
                pygame.quit()
                exit()
            else:
                print("Você precisa da chave para sair!")
                return
        
        elif destino == 'B': # Encontrou um baú
            print("Você encontrou um baú!")
            if (nx, ny) == bau_com_chave:
                jogador["tem_chave"] = True
                print("\033[33mVocê encontrou a CHAVE!\033[0m")
            elif (nx, ny) == bau_com_espada:
                jogador["tem_espada"] = True
                print("\033[34mVocê encontrou a ESPADA!, de durabilidade 3\033[0m")
            else:
                print("Este baú está vazio.")
            mapa[nx][ny] = 'V' # Baú aberto vira chão vazio.

        elif destino == 'I': # Encontrou um inimigo
            print("você encontrou um inimigo!")
            if jogador["tem_espada"]:
                mapa[nx][ny] = 'V' # Inimigo derrotado vira chão vazio.
                jogador["vida_espada"] -= 1
                print("você eliminou um inimigo, durabilidade: ", jogador["vida_espada"])
                if jogador["vida_espada"] <= 0:
                    jogador["tem_espada"] = False
                    print("Sua espada quebrou")
            else: # Sem espada, o jogador toma dano.
                jogador["vida"] -= 1
                print("você foi atacado!\nVidas restantes:", jogador["vida"])
                if jogador["vida"] <= 0: # Fim de jogo se a vida acabar.
                    print("\033[31mVocê perdeu todas as vidas!\nGAME OVER!\033[0m")
                    pygame.quit()
                    exit()
        
        elif destino == 'T': # Caiu em uma armadilha
            jogador["vida"] -= 2
            print("você caiu em uma armadilha!\nVidas restantes:", jogador["vida"])
            mapa[nx][ny] = 'V' # Armadilha desarmada vira chão vazio
            if jogador["vida"] <= 0: # Fim de jogo se a vida acabar.
                print("\033[31mVocê perdeu todas as vidas!\nGAME OVER!\033[0m")
                pygame.quit()
                exit()
        
        elif destino == 'V': # Moveu para um espaço vazio
            # Atualiza o mapa: o novo local recebe o jogador, o antigo vira vazio.
            mapa[nx][ny] = 'J'
            mapa[x_atual][y_atual] = 'V'
            # Atualiza a posição do jogador no dicionário.
            jogador["x"], jogador["y"] = nx, ny
            return

# ========== FUNÇÃO DE DESENHO ==========
def desenhar_mapa(tela, mapa, fonte):
    """Desenha o estado atual do mapa na tela do jogo."""
    # Itera sobre cada célula do grid.
    for i in range(LINHAS):
        for j in range(COLUNAS):
            tipo = mapa[i][j]
            # Pega a cor correspondente ao tipo de célula.
            cor = CORES.get(tipo, (0, 0, 0)) # Padrão preto se o tipo não for encontrado.
            # Calcula as coordenadas em pixels para desenhar.
            x = j * TAMANHO_CELULA
            y = i * TAMANHO_CELULA
            # Desenha o retângulo colorido da célula.
            pygame.draw.rect(tela, cor, (x, y, TAMANHO_CELULA, TAMANHO_CELULA))
            # Desenha uma borda preta fina ao redor de cada célula.
            pygame.draw.rect(tela, (0, 0, 0), (x, y, TAMANHO_CELULA, TAMANHO_CELULA), 1)
            # Se a célula não for vazia, desenha o caractere correspondente no centro.
            if tipo != 'V':
                # Renderiza o texto (caractere).
                texto = fonte.render(tipo, True, (255, 255, 255) if tipo in ['I', 'J', 'T'] else (0, 0, 0))
                # Centraliza o texto na célula.
                rect_texto = texto.get_rect(center=(x + TAMANHO_CELULA // 2, y + TAMANHO_CELULA // 2))
                # Desenha o texto na tela.
                tela.blit(texto, rect_texto)

# ========== LOOP PRINCIPAL ==========
def main():
    """Função principal que inicializa o Pygame e executa o loop do jogo."""
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Mapa Gerado com Backtracking v2")
    fonte = pygame.font.SysFont(None, 36) # Define a fonte para os caracteres no mapa.

    # Gera o mapa e o estado inicial do jogo.
    mapa, jogador, bau_com_chave, bau_com_espada = gerar_mapa_com_backtracking()
    
    clock = pygame.time.Clock() # Objeto para controlar o FPS.
    rodando = True

    # Loop principal do jogo.
    while rodando:
        # Limpa a tela.
        tela.fill((0, 0, 0))
        # Desenha o mapa atualizado.
        desenhar_mapa(tela, mapa, fonte)
        # Atualiza a tela para mostrar o que foi desenhado.
        pygame.display.flip()

        # Processa a fila de eventos do Pygame.
        for evento in pygame.event.get():
            # Se o evento for fechar a janela, termina o loop.
            if evento.type == pygame.QUIT:
                rodando = False
            # Se o evento for uma tecla pressionada.
            elif evento.type == pygame.KEYDOWN:
                # Tecla 'r': reinicia o jogo gerando um novo mapa.
                if evento.key == pygame.K_r:
                    mapa, jogador, bau_com_chave, bau_com_espada = gerar_mapa_com_backtracking()
                # Teclas de seta: chama a função de movimento.
                elif evento.key == pygame.K_UP:
                    mover(-1, 0, jogador, mapa, bau_com_chave, bau_com_espada)
                elif evento.key == pygame.K_DOWN:
                    mover(1, 0, jogador, mapa, bau_com_chave, bau_com_espada)
                elif evento.key == pygame.K_LEFT:
                    mover(0, -1, jogador, mapa, bau_com_chave, bau_com_espada)
                elif evento.key == pygame.K_RIGHT:
                    mover(0, 1, jogador, mapa, bau_com_chave, bau_com_espada)

        clock.tick(60) # Limita o jogo a 60 frames por segundo.
    pygame.quit() # Encerra o Pygame de forma limpa.


# Ponto de entrada padrão do Python: executa a função main() quando o script é chamado diretamente.
if __name__ == "__main__":
    main()