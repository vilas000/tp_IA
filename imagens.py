# tp_IA/imagens.py

import pygame
import random   
import config

# Carregar imagens
img_parede = pygame.image.load("imagens/parede.png")
img_parede = pygame.transform.scale(img_parede, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))

img_bau = pygame.image.load("imagens/bau.png")
img_bau = pygame.transform.scale(img_bau, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))

img_saida = pygame.image.load("imagens/saida.png")
img_saida = pygame.transform.scale(img_saida, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))

img_chao = pygame.image.load("imagens/chao.png")
img_chao = pygame.transform.scale(img_chao, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))

img_jogador = pygame.image.load("imagens/jogador.png")
img_jogador = pygame.transform.scale(img_jogador, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))

img_chave = pygame.image.load("imagens/chave.png")
img_chave = pygame.transform.scale(img_chave, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))

img_espada = pygame.image.load("imagens/espada.png")
img_espada = pygame.transform.scale(img_espada, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))

img_coracao = pygame.image.load("imagens/coracao.png")
img_coracao = pygame.transform.scale(img_coracao, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))

img_inimigo = pygame.image.load("imagens/inimigo.png")
img_inimigo = pygame.transform.scale(img_inimigo, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))

img_armadilha = pygame.image.load("imagens/armadilha.png")
img_armadilha = pygame.transform.scale(img_armadilha, (config.TAMANHO_CELULA, config.TAMANHO_CELULA))
