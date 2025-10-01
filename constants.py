'''
Módulo para armazenar constantes do projeto, como cores, dimensões e layout.
'''
import pygame
from typing import List, Dict, Tuple, Any, Optional

# Dimensões da janela
LARGURA: int = 740
ALTURA: int = 350

# Cores (em formato RGB)
COR_FUNDO: Tuple[int, int, int] = (20, 20, 20)
COR_CORPO_CALCULADORA: Tuple[int, int, int] = (65, 60, 55)
COR_TELA_FUNDO: Tuple[int, int, int] = (140, 150, 140)
COR_TEXTO_TELA: Tuple[int, int, int] = (0, 0, 0)
COR_FAIXA_DECORATIVA: Tuple[int, int, int] = (180, 150, 90)

COR_BOTAO_PRETO: Tuple[int, int, int] = (45, 45, 45)
COR_BOTAO_AZUL: Tuple[int, int, int] = (50, 80, 120)
COR_BOTAO_LARANJA: Tuple[int, int, int] = (210, 140, 0)
COR_TEXTO_BOTAO_BRANCO: Tuple[int, int, int] = (255, 255, 255)
COR_TEXTO_BOTAO_AZUL: Tuple[int, int, int] = (120, 180, 255)
COR_TEXTO_BOTAO_LARANJA: Tuple[int, int, int] = (210, 140, 0)

# Layout da Calculadora
MARGEM_CORPO: int = 10
LARGURA_CORPO: int = LARGURA - 2 * MARGEM_CORPO
ALTURA_CORPO: int = ALTURA - 2 * MARGEM_CORPO

# Layout da Tela
MARGEM_TELA: int = 15
LARGURA_TELA: int = LARGURA_CORPO - 2 * MARGEM_TELA
ALTURA_TELA: int = 50
POS_X_TELA: int = MARGEM_CORPO + MARGEM_TELA
POS_Y_TELA: int = MARGEM_CORPO + 35

# Layout dos Botões
# Posições e tamanhos definidos manualmente para maior fidelidade.
BOTOES: List[Dict[str, Any]] = []

BW: int = 68  # Largura padrão do botão
BH: int = 38  # Altura padrão do botão
BX_START: int = 18  # Posição inicial X do primeiro botão (canto sup esq do corpo)
BY_START: int = 120  # Posição inicial Y do primeiro botão (canto sup esq do corpo)
BSX: int = 8  # Espaçamento entre botões X
BSY: int = 12  # Espaçamento entre botões Y

# Definição dos botões (main, f, g, cor)
LAYOUT: Dict[Tuple[int, int], Tuple[str, Optional[str], Optional[str], str]] = {
    (0, 0): ('n', '12x', 'AMORT', 'preto'),
    (0, 1): ('i', '12÷', 'INT', 'preto'),
    (0, 2): ('PV', 'CF0', 'NPV', 'preto'),
    (0, 3): ('PMT', 'CFj', 'IRR', 'preto'),
    (0, 4): ('7', None, 'YTM', 'preto'),
    (0, 5): ('8', 'SL', 'x̄', 'preto'),
    (0, 6): ('9', 'SOYD', 's', 'preto'),
    (0, 7): ('÷', None, 'DB', 'preto'),

    (1, 0): ('FV', 'Nj', 'RND', 'preto'),
    (1, 1): ('Δ%', 'FRAC', 'INTG', 'preto'),
    (1, 2): ('1/x', '%', 'LN', 'preto'),
    (1, 3): ('y^x', '√x', 'e^x', 'preto'),
    (1, 4): ('4', None, None, 'preto'),
    (1, 5): ('5', None, None, 'preto'),
    (1, 6): ('6', None, None, 'preto'),
    (1, 7): ('×', None, None, 'preto'),


    (2, 0): ('R↓', 'x<>y', 'PSE', 'preto'),
    (2, 1): ('SST', 'BST', 'GTO', 'preto'),
    (2, 2): ('EEX', 'ΔDYS', 'R/S', 'preto'),
    (2, 3): ('CHS', 'DATE', 'PRICE', 'preto'),
    (2, 4): ('1', None, None, 'preto'),
    (2, 5): ('2', None, None, 'preto'),
    (2, 6): ('3', None, None, 'preto'),
    (2, 7): ('-', None, None, 'preto'),

    (3, 0): ('ON', None, None, 'preto'),
    (3, 1): ('f', None, None, 'laranja'),
    (3, 2): ('g', None, None, 'azul'),
    (3, 3): ('STO', 'RCL', 'PREFIX', 'preto'),
    (3, 4): ('0', None, None, 'preto'),
    (3, 5): ('.', None, None, 'preto'),
    (3, 6): ('Σ+', 'CLΣ', 'MEM', 'preto'),
    (3, 7): ('+', None, None, 'preto'),
}

# Gerar BOTOES a partir do LAYOUT em grade
for (row, col), (main, f, g, color) in LAYOUT.items():
    rect = pygame.Rect(BX_START + col * (BW + BSX), BY_START + row * (BH + BSY), BW, BH)
    BOTOES.append({'rect': rect, 'main': main, 'f': f, 'g': g, 'color': color})

# Botões especiais que não se encaixam na grade principal
BOTOES.append({'rect': pygame.Rect(BX_START + 8 * (BW + BSX), BY_START + 0 * (BH + BSY), BW, BH*4.7 + BSY), 'main': 'ENTER', 'f': 'INPUT', 'g': 'FIN', 'color': 'preto'})


# Mapeamento do teclado para ações da calculadora
KEY_MAP: Dict[int, str] = {
    pygame.K_0: '0', pygame.K_KP0: '0',
    pygame.K_1: '1', pygame.K_KP1: '1',
    pygame.K_2: '2', pygame.K_KP2: '2',
    pygame.K_3: '3', pygame.K_KP3: '3',
    pygame.K_4: '4', pygame.K_KP4: '4',
    pygame.K_5: '5', pygame.K_KP5: '5',
    pygame.K_6: '6', pygame.K_KP6: '6',
    pygame.K_7: '7', pygame.K_KP7: '7',
    pygame.K_8: '8', pygame.K_KP8: '8',
    pygame.K_9: '9', pygame.K_KP9: '9',
    pygame.K_PERIOD: '.', pygame.K_KP_PERIOD: '.',
    pygame.K_PLUS: '+', pygame.K_KP_PLUS: '+',
    pygame.K_MINUS: '-', pygame.K_KP_MINUS: '-',
    pygame.K_ASTERISK: '×', pygame.K_KP_MULTIPLY: '×',
    pygame.K_SLASH: '÷', pygame.K_KP_DIVIDE: '÷',
    pygame.K_RETURN: 'ENTER', pygame.K_KP_ENTER: 'ENTER',
    pygame.K_BACKSPACE: 'CLx', # Mapeia backspace para limpar a entrada
    pygame.K_f: 'f',
    pygame.K_g: 'g',
    pygame.K_n: 'n',
    pygame.K_i: 'i',
    pygame.K_EQUALS: '+', # Para a tecla = que pode ser + com shift
    pygame.K_MINUS: '-',
    pygame.K_SLASH: '÷',
    pygame.K_8: '×', # Para a tecla 8 que pode ser * com shift
    # Adicionar outras teclas conforme necessário
}