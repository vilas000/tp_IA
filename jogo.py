import pygame
import random
import copy
from collections import deque
import imagens
import config
import tkinter as tk
from tkinter import messagebox
import time

# ========== CONFIGURAÇÃO ==========
# Comentários sobre configurações anteriores ou valores gerados aleatoriamente (atualmente comentados)

# Dicionário que associa símbolos do mapa às imagens correspondentes carregadas no módulo imagens
IMAGENS = {
    'P': imagens.img_parede,    # Parede
    'V': imagens.img_chao,      # Chão (vazio)
    'J': imagens.img_jogador,   # Jogador
    'S': imagens.img_saida,     # Saída
    'I': imagens.img_inimigo,   # Inimigo
    'B': imagens.img_bau,       # Baú
    'T': imagens.img_armadilha, # Armadilha
    'TA': imagens.img_armadilha, # Armadilha ativa (mesma imagem por enquanto)
}

# ========== FUNÇÕES UTILITÁRIAS ==========

def get_posicoes_porta(linhas, colunas):
    """Retorna uma lista de posições nas bordas internas do mapa (excluindo os cantos),
    que são candidatas para colocar portas, jogador ou saída."""
    posicoes = []
    # Linhas superior e inferior (exceto cantos)
    for j in range(1, colunas - 1):
        posicoes.append((0, j))             # topo
        posicoes.append((linhas - 1, j))   # base
    # Colunas esquerda e direita (exceto cantos)
    for i in range(1, linhas - 1):
        posicoes.append((i, 0))             # esquerda
        posicoes.append((i, colunas - 1))   # direita
    return posicoes

def distancia_manhattan(p1, p2):
    """Calcula a distância de Manhattan (soma das diferenças absolutas das coordenadas)
    entre dois pontos p1 e p2."""
    if not p1 or not p2:
        return 0
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def existe_caminho(mapa, inicio, fim, linhas, colunas):
    """Verifica se existe caminho do ponto 'inicio' até 'fim' no mapa,
    considerando apenas células passáveis ('V', 'B', 'S'). Usa busca em largura (BFS)."""
    if not inicio or not fim:
        return False
    
    fila = deque([inicio])      # fila para BFS
    visitados = {inicio}        # conjunto de visitados
    celulas_passaveis = {'V', 'B', 'S'}

    while fila:
        x, y = fila.popleft()
        if (x, y) == fim:
            return True  # caminho encontrado

        # Verifica vizinhos (cima, baixo, esquerda, direita)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < linhas and 0 <= ny < colunas and (nx, ny) not in visitados:
                # Se célula é destino ou passável, adiciona para explorar
                if (nx, ny) == fim or mapa[nx][ny] in celulas_passaveis:
                    visitados.add((nx, ny))
                    fila.append((nx, ny))
    return False  # caminho não encontrado

# ========== FUNÇÕES DE GERAÇÃO (BACKTRACKING) ==========

def obter_posicoes_disponiveis(mapa, linhas, colunas):
    """Retorna uma lista de posições internas do mapa que são chão ('V'),
    ou seja, disponíveis para colocar itens. A lista é embaralhada."""
    posicoes = [(r, c) for r in range(1, linhas - 1) for c in range(1, colunas - 1) if mapa[r][c] == 'V']
    random.shuffle(posicoes)
    return posicoes

def verificar_caminhos_criticos(mapa, contexto, linhas, colunas):
    """Verifica após a geração do mapa se existem caminhos válidos do jogador para a chave
    e da chave para a saída, para garantir jogabilidade mínima."""
    pos_jogador = contexto.get('JOGADOR')
    pos_chave = contexto.get('CHAVE')
    pos_saida = contexto.get('SAIDA')

    # Valida caminho do jogador para chave
    if not existe_caminho(mapa, pos_jogador, pos_chave, linhas, colunas):
        print("Falha na validação final: Sem caminho do Jogador para a Chave.")
        return False
        
    # Valida caminho da chave para a saída
    if not existe_caminho(mapa, pos_chave, pos_saida, linhas, colunas):
        print("Falha na validação final: Sem caminho da Chave para a Saída.")
        return False
        
    return True  # todos caminhos críticos válidos

def eh_caminho_valido_parcial(mapa, contexto):
    """Valida parcialmente os caminhos importantes durante a geração, para podar soluções ruins."""
    pos_jogador = contexto.get('JOGADOR')
    pos_chave = contexto.get('CHAVE')
    pos_saida = contexto.get('SAIDA')

    if pos_jogador and pos_chave and not existe_caminho(mapa, pos_jogador, pos_chave):
        return False
    if pos_chave and pos_saida and not existe_caminho(mapa, pos_chave, pos_saida):
        return False
    return True

def eh_distribuicao_valida(contexto, tipo_item_atual, pos_atual):
    """Verifica se a distância entre o item atual e os demais itens no contexto respeita
    regras mínimas de distância para evitar agrupamentos próximos e facilitar o jogo."""
    pos_jogador = contexto.get('JOGADOR')
    
    MIN_DIST_JOGADOR = 3  # distância mínima do jogador para outros itens
    if pos_jogador and tipo_item_atual not in ['JOGADOR', 'SAIDA']:
        if distancia_manhattan(pos_atual, pos_jogador) < MIN_DIST_JOGADOR:
            return False

    # Chave e espada não podem estar próximas (menos que 5 de distância)
    if tipo_item_atual == 'CHAVE':
        pos_espada = contexto.get('ESPADA')
        if pos_espada and distancia_manhattan(pos_atual, pos_espada) < 5:
            return False
            
    if tipo_item_atual == 'ESPADA':
        pos_chave = contexto.get('CHAVE')
        if pos_chave and distancia_manhattan(pos_atual, pos_chave) < 5:
            return False
        
    # Baús, chave e espada devem estar razoavelmente distantes entre si
    if tipo_item_atual.startswith('BAU') or tipo_item_atual in ['CHAVE', 'ESPADA']:
        for tipo, pos in contexto.items():
            if (tipo.startswith('BAU') or tipo in ['CHAVE', 'ESPADA']) and tipo != tipo_item_atual:
                if distancia_manhattan(pos_atual, pos) < 3:
                    return False

    return True

def resolver_backtracking(mapa, itens_a_colocar, contexto, estado_busca, linhas, colunas):
    """Função recursiva que tenta posicionar os itens no mapa com backtracking.
    Usa estado_busca para limitar a complexidade da busca e evitar loop infinito."""
    
    # Contador de passos para limitar busca
    estado_busca['passos'] += 1
    if estado_busca['passos'] > estado_busca['limite_passos']:
        return False, None, None  # aborta busca por limite excedido

    # Caso base: sem itens a colocar, mapa válido encontrado
    if not itens_a_colocar:
        return True, mapa, contexto

    # Pega o próximo item a ser posicionado (símbolo e tipo)
    item_atual, tipo_item = itens_a_colocar[0]
    
    # Para jogador e saída, usar bordas do mapa
    if tipo_item in ['JOGADOR', 'SAIDA']:
        posicoes_candidatas = get_posicoes_porta(linhas, colunas)
        random.shuffle(posicoes_candidatas)
    else:
        # Para outros itens, posições internas disponíveis
        posicoes_candidatas = obter_posicoes_disponiveis(mapa, linhas, colunas)

    for pos in posicoes_candidatas:
        r, c = pos
        char_original = mapa[r][c]

        # Verifica se pode colocar item na posição (parede para JOGADOR/SAIDA, chão para os outros)
        pode_colocar = (tipo_item in ['JOGADOR', 'SAIDA'] and char_original == 'P') or \
                       (tipo_item not in ['JOGADOR', 'SAIDA'] and char_original == 'V')
        
        if pode_colocar:
            mapa[r][c] = item_atual   # coloca item no mapa
            contexto[tipo_item] = pos # registra posição no contexto
            
            # Verifica se distribuição e caminhos parciais são válidos
            if eh_distribuicao_valida(contexto, tipo_item, pos):
                sucesso, mapa_final, contexto_final = resolver_backtracking(
                    mapa, itens_a_colocar[1:], contexto, estado_busca, linhas, colunas
                )
                if sucesso:
                    return True, mapa_final, contexto_final

            # Se falhou, desfaz (backtrack)
            mapa[r][c] = char_original
            del contexto[tipo_item]

    return False, None, None  # falha em posicionar o item atual

def gerar_mapa_com_backtracking(linhas, colunas, num_baus, num_inimigos):
    """Função principal que tenta gerar um mapa válido com backtracking, tentando
    várias vezes até atingir o limite máximo de tentativas."""
    print("Iniciando geração com Backtracking e regras de distribuição...")

    area = linhas * colunas
    max_tentativas = 20
    tentativas = 0

    while tentativas < max_tentativas:
        tentativas += 1
        
        # Cria mapa base com paredes nas bordas e chão no interior
        mapa_base = [['P' for _ in range(colunas)] for _ in range(linhas)]
        for i in range(1, linhas - 1):
            for j in range(1, colunas - 1):
                mapa_base[i][j] = 'V'
        
        # Itens essenciais (jogador, saída, chave e espada)
        itens_para_colocar = [
            ('J', 'JOGADOR'), ('S', 'SAIDA'), ('B', 'CHAVE'), ('B', 'ESPADA')
        ]
        # Baús, inimigos e armadilhas adicionais
        itens_para_colocar.extend([('B', f'BAU_{i}') for i in range(num_baus)])
        itens_para_colocar.extend([('I', f'INIMIGO_{i}') for i in range(num_inimigos)])
        itens_para_colocar.extend([('T', f'ARMADILHA_{i}') for i in range(2)])
        
        # Randomiza itens menos essenciais para variar a geração
        itens_essenciais = itens_para_colocar[:4]
        itens_randomizaveis = itens_para_colocar[4:]
        random.shuffle(itens_randomizaveis)
        itens_para_colocar = itens_essenciais + itens_randomizaveis

        # Estado de controle da busca para limitar passos
        estado_busca = {
            'passos': 0,
            'limite_passos': 500  # Limite para abortar busca que demora demais
        }
        print(f"Tentativa de geração nº {tentativas} (limite de {estado_busca['limite_passos']} passos)...")
        
        # Chama função recursiva para posicionar todos os itens
        sucesso_posicionamento, mapa_potencial, contexto_potencial = resolver_backtracking(
            copy.deepcopy(mapa_base), itens_para_colocar, {}, estado_busca, linhas, colunas
        )

        # Se ultrapassou limite de passos, ignora esta tentativa
        if estado_busca['passos'] > estado_busca['limite_passos']:
            print(f"Tentativa {tentativas} abortada: Limite de passos de busca atingido.")
            continue

        # Se posicionamento foi bem sucedido e caminhos críticos válidos, retorna resultado
        if sucesso_posicionamento and verificar_caminhos_criticos(mapa_potencial, contexto_potencial, linhas, colunas):
            print("Mapa válido gerado e validado com sucesso!\nPassos na busca:", estado_busca['passos'])
            pos_jogador = contexto_potencial['JOGADOR']
            # Cria estrutura de dados do jogador com posições e status inicial
            jogador = {
                "x": pos_jogador[0], "y": pos_jogador[1], "tem_chave": False,
                "tem_espada": False, "vida_espada": 3, "vida": 3
            }
            bau_com_chave = contexto_potencial['CHAVE']
            bau_com_espada = contexto_potencial['ESPADA']
            return mapa_potencial, jogador, bau_com_chave, bau_com_espada
        else:
            # Se posicionou mas falhou na validação dos caminhos, tenta novamente
            if sucesso_posicionamento:
                print(f"Posicionamento da tentativa {tentativas} bem-sucedido, mas falhou na validação de caminhos.")
    
    # Se esgotou tentativas sem sucesso, informa erro e encerra o programa
    print(f"\nNÃO FOI POSSÍVEL GERAR UM MAPA VÁLIDO APÓS {max_tentativas} TENTATIVAS.")
    print("A combinação de tamanho do mapa, número de itens e restrições de distância provavelmente torna a geração impossível.")
    print("Sugestão: Aumente o mapa, reduza o número de itens ou diminua a distância mínima entre eles.")
    pygame.quit()
    exit()

# ========== LÓGICA DO JOGO E MOVIMENTO ==========

def mover(dx, dy, jogador, mapa, bau_com_chave, bau_com_espada, linhas, colunas):
    """Função que tenta mover o jogador em (dx, dy) se possível,
    trata interações com baús, inimigos, armadilhas e saída."""
    x_atual, y_atual = jogador["x"], jogador["y"]
    nx, ny = jogador["x"] + dx, jogador["y"] + dy

    # Verifica limites do mapa
    if 0 <= nx < linhas and 0 <= ny < colunas:
        destino = mapa[nx][ny]

        if destino == 'P':
            # Parede, não pode andar
            return
        elif destino == 'S':
            # Saída: só pode vencer se tem chave
            if jogador["tem_chave"]:
                print("\033[33mVocê venceu!\033[0m")  # Texto amarelo
                pygame.quit()
                exit()
            else:
                print("Você precisa da chave para sair!")
                return
        elif destino == 'B':
            # Encontrou baú
            print("Você encontrou um baú!")
            if (nx, ny) == bau_com_chave:
                jogador["tem_chave"] = True
                print("\033[33mVocê encontrou a CHAVE!\033[0m")  # Amarelo
            elif (nx, ny) == bau_com_espada:
                jogador["tem_espada"] = True
                print("\033[34mVocê encontrou a ESPADA!, de durabilidade 3\033[0m")  # Azul
            else:
                print("Este baú está vazio.")
            mapa[nx][ny] = 'V'  # Baú aberto vira chão

        elif destino == 'I':
            # Encontrou inimigo
            print("você encontrou um inimigo!")
            if jogador["tem_espada"]:
                mapa[nx][ny] = 'V'  # inimigo eliminado vira chão
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
            # Armadilha
            jogador["vida"] -= 2
            print("você caiu em uma armadilha!\nVidas restantes:", jogador["vida"])
            mapa[nx][ny] = 'TA'  # marca armadilha como ativa
            if jogador["vida"] <= 0:
                print("\033[31mVocê perdeu todas as vidas!\nGAME OVER!\033[0m")  # Vermelho
                pygame.quit()
                exit()
        elif destino == 'V':
            # Chão vazio, movimenta jogador
            mapa[nx][ny] = 'J'
            mapa[x_atual][y_atual] = 'V'
            jogador["x"], jogador["y"] = nx, ny
            return
        elif destino == 'TA':
            # Armadilha já ativada, não pode passar
            return


def desenhar_hud(tela, jogador):
    # Define cores e tamanho dos elementos da HUD (Heads-Up Display)
    HUD_BG = (60, 60, 60)  # Fundo cinza escuro para os retângulos da HUD
    BORDER_COLOR = (255, 255, 255)  # Borda branca dos retângulos
    RECT_SIZE = (50, 50)  # Tamanho dos retângulos da HUD (largura x altura)

    # Define a posição inicial (x, y) onde a HUD será desenhada na tela
    x, y = 20, 20

    # --- Retângulo e ícone da chave ---
    pygame.draw.rect(tela, HUD_BG, (x + 4, y - 15, *RECT_SIZE))       # Fundo do retângulo
    pygame.draw.rect(tela, BORDER_COLOR, (x + 4, y - 15, *RECT_SIZE), 2)  # Borda do retângulo
    if jogador["tem_chave"] == True:   # Se o jogador possui a chave, desenha o ícone da chave
        tela.blit(imagens.img_chave, (x + 6, y - 12))  # Blita a imagem da chave na posição

    # --- Retângulo e ícone da espada ---
    x += RECT_SIZE[0] + 10  # Move a posição x para o próximo retângulo, com espaço entre eles
    pygame.draw.rect(tela, HUD_BG, (x + 4, y - 15, *RECT_SIZE))       # Fundo do retângulo
    pygame.draw.rect(tela, BORDER_COLOR, (x + 4, y - 15, *RECT_SIZE), 2)  # Borda do retângulo
    if jogador["tem_espada"] == True:  # Se o jogador possui a espada, desenha o ícone da espada
        tela.blit(imagens.img_espada, (x + 6, y - 12))

    # --- Desenha os corações que representam a vida do jogador ---
    x += RECT_SIZE[0] + 20  # Move mais para a direita para desenhar os corações
    for i in range(jogador["vida"]):  # Para cada ponto de vida, desenha um coração
        # Desenha o coração com espaçamento horizontal entre eles
        tela.blit(imagens.img_coracao, (x + i * (imagens.img_coracao.get_width() + 5), y - 15))


# ========== FUNÇÃO DE DESENHO DO MAPA ==========  
def desenhar_mapa(tela, mapa, linhas, colunas):
    # Percorre todas as células do mapa para desenhá-las na tela
    for i in range(linhas):
        for j in range(colunas):
            tipo = mapa[i][j]  # Tipo de célula na posição atual (ex: parede, chão, jogador, etc)
            pisos = IMAGENS.get(tipo, (0, 0, 0))  # Busca a imagem correspondente (não usada direto aqui)
            
            # Calcula a posição na tela para desenhar a célula
            x = j * config.TAMANHO_CELULA
            y = i * config.TAMANHO_CELULA + config.HUD_HEIGHT  # Compensa altura do HUD

            # Desenha o retângulo de borda da célula
            pygame.draw.rect(tela, (0, 0, 0), (x, y, config.TAMANHO_CELULA, config.TAMANHO_CELULA), 1)

            # Desenha a imagem correspondente ao tipo da célula
            if tipo == 'P':
                tela.blit(imagens.img_parede, (x, y))
            elif tipo == 'B':
                tela.blit(imagens.img_bau, (x, y))
            elif tipo == 'S':
                tela.blit(imagens.img_saida, (x, y))
            elif tipo == 'J':
                tela.blit(imagens.img_jogador, (x, y))
            elif tipo == 'I':
                tela.blit(imagens.img_inimigo, (x, y))
            elif tipo == 'TA':
                tela.blit(imagens.img_armadilha, (x, y))
            else:
                tela.blit(imagens.img_chao, (x, y))  # Caso seja chão ou outros tipos não listados


def dados_jogador_gui():
    # Função que cria duas janelas Tkinter para o usuário configurar o mapa antes do jogo começar
    resultado = {}

    # --- Primeira janela: Configuração de linhas e colunas do mapa ---
    def janela_linhas_colunas():
        def validar_linhas_colunas():
            try:
                linhas = int(entry_linhas.get())  # Pega valor digitado em linhas
                colunas = int(entry_colunas.get())  # Pega valor digitado em colunas
                # Verifica se os valores estão dentro do intervalo permitido
                if not (12 <= linhas <= 18 and 12 <= colunas <= 18):
                    raise ValueError("Linhas e colunas devem estar entre 12 e 18.")
                resultado['linhas'] = linhas
                resultado['colunas'] = colunas
                area = linhas * colunas
                janela1.destroy()  # Fecha essa janela
                janela_baus_inimigos(area)  # Abre a próxima janela para configurar baús e inimigos
            except ValueError as e:
                # Exibe mensagem de erro se entrada inválida
                messagebox.showerror("Erro de validação", str(e))

        janela1 = tk.Tk()
        janela1.title("Configuração do Mapa - Parte 1")

        # Labels e entradas para linhas e colunas
        tk.Label(janela1, text="Número de linhas (12 a 18):").grid(row=0, column=0, sticky="w")
        entry_linhas = tk.Entry(janela1)
        entry_linhas.grid(row=0, column=1)

        tk.Label(janela1, text="Número de colunas (12 a 18):").grid(row=1, column=0, sticky="w")
        entry_colunas = tk.Entry(janela1)
        entry_colunas.grid(row=1, column=1)

        btn_ok = tk.Button(janela1, text="Próximo", command=validar_linhas_colunas)
        btn_ok.grid(row=2, column=0, columnspan=2, pady=10)

        janela1.mainloop()

    # --- Segunda janela: Configuração do número de baús e inimigos ---
    def janela_baus_inimigos(area):
        def validar_baus_inimigos():
            try:
                baus = int(entry_baus.get())  # Número de baús digitado
                inimigos = int(entry_inimigos.get())  # Número de inimigos digitado
                # Valores recomendados baseados na área do mapa
                resultado['baus'] = baus
                resultado['inimigos'] = inimigos
                janela2.destroy()  # Fecha esta janela
            except ValueError as e:
                messagebox.showerror("Erro de validação", str(e))

        janela2 = tk.Tk()
        janela2.title("Configuração do Mapa - Parte 2")

        # Labels e entradas para baús e inimigos, com recomendações
        rec_baus = round(area // 10)
        rec_inimigos = round((area * 1.1) // 10)

        label_baus = tk.Label(janela2, text=f"Digite o número de baús (recomendado até {rec_baus}):")
        label_baus.grid(row=0, column=0, sticky="w")
        entry_baus = tk.Entry(janela2)
        entry_baus.grid(row=0, column=1)

        label_inimigos = tk.Label(janela2, text=f"Digite o número de inimigos (recomendado até {rec_inimigos}):")
        label_inimigos.grid(row=1, column=0, sticky="w")
        entry_inimigos = tk.Entry(janela2)
        entry_inimigos.grid(row=1, column=1)

        btn_ok = tk.Button(janela2, text="Confirmar", command=validar_baus_inimigos)
        btn_ok.grid(row=2, column=0, columnspan=2, pady=10)

        janela2.mainloop()

    # Executa a primeira janela para começar o processo
    janela_linhas_colunas()

    # Retorna as configurações obtidas (linhas, colunas, baús, inimigos)
    return resultado.get('linhas'), resultado.get('colunas'), resultado.get('baus'), resultado.get('inimigos')


# ========== LOOP PRINCIPAL DO JOGO ==========
def main():
    # Obtém as configurações do mapa a partir da interface gráfica Tkinter
    linhas, colunas, baus, inimigos = dados_jogador_gui()

    # Calcula as dimensões da janela Pygame
    altura_tela = config.HUD_HEIGHT + linhas * config.TAMANHO_CELULA
    largura_tela = colunas * config.TAMANHO_CELULA

    pygame.init()
    tela = pygame.display.set_mode((largura_tela, altura_tela))  # Cria a janela do jogo
    pygame.display.set_caption("Mapa Gerado com Backtracking v2")  # Título da janela
    fonte = pygame.font.SysFont(None, 36)  # Fonte padrão para texto (não usada muito aqui)

    # Gera o mapa inicial, jogador, baú da chave e baú da espada usando backtracking
    start_time = time.time()
    mapa, jogador, bau_com_chave, bau_com_espada = gerar_mapa_com_backtracking(linhas, colunas, baus, inimigos)
    end_time = time.time()
    print(f"Tempo de geração do mapa: {end_time - start_time:.4f} segundos")

    clock = pygame.time.Clock()  # Controla a taxa de atualização da tela
    rodando = True  # Flag para manter o loop do jogo rodando

    while rodando:
        tela.fill((0, 0, 0))  # Limpa a tela (preto)
        desenhar_mapa(tela, mapa, linhas, colunas)  # Desenha o mapa atual
        desenhar_hud(tela, jogador)  # Desenha a HUD com informações do jogador
        pygame.display.flip()  # Atualiza a tela com tudo que foi desenhado

        # Lida com eventos do teclado e janela
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:  # Se janela for fechada
                rodando = False  # Sai do loop principal
            elif evento.type == pygame.KEYDOWN:  # Tecla pressionada
                if evento.key == pygame.K_r:  # Pressionou 'r' para reiniciar mapa
                    mapa, jogador, bau_com_chave, bau_com_espada = gerar_mapa_com_backtracking()
                elif evento.key == pygame.K_UP:  # Seta para cima: mover jogador para cima
                    mover(-1, 0, jogador, mapa, bau_com_chave, bau_com_espada, linhas, colunas)
                elif evento.key == pygame.K_DOWN:  # Seta para baixo: mover para baixo
                    mover(1, 0, jogador, mapa, bau_com_chave, bau_com_espada, linhas, colunas)
                elif evento.key == pygame.K_LEFT:  # Seta para esquerda
                    mover(0, -1, jogador, mapa, bau_com_chave, bau_com_espada, linhas, colunas)
                elif evento.key == pygame.K_RIGHT:  # Seta para direita
                    mover(0, 1, jogador, mapa, bau_com_chave, bau_com_espada, linhas, colunas)

        clock.tick(60)  # Limita o jogo a rodar a 60 frames por segundo

    pygame.quit()  # Encerra o Pygame ao sair do loop


# Quando o arquivo é executado diretamente, executa a função main para iniciar o jogo
if __name__ == "__main__":
    main()
