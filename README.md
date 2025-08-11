# Gerador de Mapas com Backtracking para Jogo 2D

Este projeto apresenta um gerador de mapas para um jogo 2D de exploração RPG, desenvolvido como parte da disciplina de Inteligência Artificial. A principal característica deste sistema é o uso de um algoritmo de backtracking para garantir que cada mapa gerado processualmente seja não apenas aleatório, mas também válido, jogável e justo, de acordo com um conjunto de regras predefinidas.

<div align="center">
  <img src="https://github.com/user-attachments/assets/98a0122f-c698-423e-928b-e9cf834c4b32" alt="Gameplay do Jogo" width="600"/>
</div>

## Sobre o Projeto
O desafio central de muitos jogos que utilizam geração procedural é criar níveis que façam sentido. Um mapa aleatório pode, por acaso, ser impossível de resolver (ex: a chave estar em um local inacessível).

Este projeto aborda esse problema tratando a geração do mapa como um Problema de Satisfação de Restrições (PSR). Em vez de apenas espalhar itens, o algoritmo busca ativamente por uma configuração que respeite todas as regras, como:

Distância Mínima: Inimigos, tesouros e armadilhas não podem estar próximos demais uns dos outros ou do jogador.

Conectividade e Jogabilidade: O mapa deve ter um caminho lógico. O jogador precisa conseguir chegar à chave e, da chave, conseguir chegar à saída.

Distribuição Equilibrada: Os itens são distribuídos pelo mapa para incentivar a exploração.

## Funcionalidades
Geração Procedural de Mapas: Cria um novo layout de mapa a cada execução.

Algoritmo de Backtracking: Garante que 100% dos mapas gerados sejam válidos e solucionáveis.

Restrições Configuráveis: As regras de geração (distância, número de itens) podem ser facilmente ajustadas no código.

Interface Gráfica Simples: Uma interface jogável construída com Pygame para testar e visualizar os mapas gerados.

Mecânicas de Jogo Básicas: Inclui movimento do jogador, coleta de itens (chave, espada), combate simples e armadilhas.

## Tecnologias Utilizadas
Python 3: Linguagem principal do projeto.

Pygame: Biblioteca utilizada para a criação da janela, renderização do mapa e captura de eventos do teclado.

## Como Executar

Para executar este projeto em sua máquina local, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/vilas000/tp_IA.git
    ```
2.  **Navegue até o diretório do projeto:**
    ```bash
    cd tp_IA
    ```
3.  **Instale as dependências:**
    ```bash
    pip install pygame
    ```
4.  **Execute o script principal:**
    ```bash
    python jogo.py
    ```
    
## Controles
Setas Direcionais (Cima, Baixo, Esquerda, Direita): Mover o jogador pelo mapa.

Tecla 'R': Gerar um novo mapa sem fechar o jogo.

Fechar a Janela: Encerrar o programa.

## academic_context
Este projeto foi desenvolvido como avaliação final para a disciplina 

BCC325 - Inteligência Artificial da Universidade Federal de Ouro Preto (UFOP), no segundo semestre de 2025, ministrada pelo Prof. Jadson Castro Gertrudes. O objetivo do trabalho era aplicar conceitos e técnicas de IA para resolver um problema prático , e a técnica escolhida foi a de Algoritmos de Satisfação de Restrições. 

## Membros
[Camile Reis](https://github.com/camile16)

[Gabriel Vilas](https://github.com/vilas000)

[Gustavo Ferreira](https://github.com/gusthcf)

[João Henrique](https://github.com/JoaoHPS06)

[Marcus Vinicius](https://github.com/MarcusViniAraujo)


