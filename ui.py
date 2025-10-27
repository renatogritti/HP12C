"""
Módulo da Interface de Usuário (UI).

Este módulo é responsável por toda a renderização gráfica da calculadora HP-12C,
incluindo a janela principal, o corpo da calculadora, a tela de LCD e os botões.
Ele utiliza a biblioteca Pygame para desenhar os elementos na tela.
"""
import pygame
import constants as c
from typing import List, Tuple, Optional, Any

class UI:
    """
    A classe UI gerencia todos os aspectos visuais da aplicação.
    """
    screen: pygame.Surface
    font_tela: pygame.font.Font
    font_botao_main: pygame.font.Font
    font_botao_sub: pygame.font.Font
    font_indicador: pygame.font.Font
    botoes_rects: List[Tuple[pygame.Rect, str]]

    def __init__(self, calculator) -> None:
        """
        Inicializa o Pygame, a tela e as fontes necessárias para a UI.
        """
        self.calculator = calculator # Referência à instância da calculadora
        pygame.init()
        self.screen = pygame.display.set_mode((c.LARGURA, c.ALTURA))
        pygame.display.set_caption("HP-12C")
        self.font_tela = pygame.font.SysFont('monospace', 36, bold=True)
        self.font_stack_small = pygame.font.SysFont('monospace', 20) # Fonte menor para a pilha
        self.font_botao_main = pygame.font.SysFont('sans-serif', 20, bold=True)
        self.font_botao_sub = pygame.font.SysFont('sans-serif', 10, bold=True)
        self.font_indicador = pygame.font.SysFont('monospace', 14, bold=True)
        self.botoes_rects = [] # Armazenará tuplas (rect, main_text)

    def _desenha_corpo(self) -> None:
        """
        Desenha o corpo principal da calculadora, a faixa e o fundo da tela.
        """
        # Corpo da calculadora
        pygame.draw.rect(self.screen, c.COR_CORPO_CALCULADORA, 
                         (c.MARGEM_CORPO, c.MARGEM_CORPO, c.LARGURA_CORPO, c.ALTURA_CORPO), 
                         border_radius=15)
        
        # Faixa decorativa superior
        pygame.draw.rect(self.screen, c.COR_FAIXA_DECORATIVA, 
                         (c.MARGEM_CORPO + 5, c.MARGEM_CORPO + 15, c.LARGURA_CORPO - 10, 10), 
                         border_radius=3)

        # Fundo da tela
        pygame.draw.rect(self.screen, c.COR_TELA_FUNDO, 
                         (c.POS_X_TELA, c.POS_Y_TELA, c.LARGURA_TELA, c.ALTURA_TELA), 
                         border_radius=5)

    def _desenha_botoes(self) -> None:
        """
        Desenha todos os botões da calculadora na tela.

        Itera sobre a lista de botões definida em constants.py, que agora contém
        retângulos pré-definidos para cada botão, e os renderiza.
        """
        self.botoes_rects.clear()
        for botao_info in c.BOTOES:
            rect: pygame.Rect = botao_info['rect'].move(c.MARGEM_CORPO, c.MARGEM_CORPO)
            main_text: str = botao_info['main']
            f_text: Optional[str] = botao_info['f']
            g_text: Optional[str] = botao_info['g']
            color_key: str = botao_info['color']

            self.botoes_rects.append((rect, main_text))

            cor_map: Dict[str, Tuple[int, int, int]] = {
                'preto': c.COR_BOTAO_PRETO,
                'azul': c.COR_BOTAO_AZUL,
                'laranja': c.COR_BOTAO_LARANJA
            }
            pygame.draw.rect(self.screen, cor_map[color_key], rect, border_radius=5)

            # Desenha texto principal
            if main_text:
                texto_surf: pygame.Surface = self.font_botao_main.render(main_text, True, c.COR_TEXTO_BOTAO_BRANCO)
                texto_rect: pygame.Rect = texto_surf.get_rect(center=rect.center)
                self.screen.blit(texto_surf, texto_rect)

            # Desenha texto 'f' (laranja)
            if f_text:
                f_surf: pygame.Surface = self.font_botao_sub.render(f_text, True, c.COR_TEXTO_BOTAO_LARANJA)
                f_rect: pygame.Rect = f_surf.get_rect(center=(rect.centerx, rect.top + 6))
                self.screen.blit(f_surf, f_rect)

            # Desenha texto 'g' (azul)
            if g_text:
                g_surf: pygame.Surface = self.font_botao_sub.render(g_text, True, c.COR_TEXTO_BOTAO_AZUL)
                # Posição do texto g depende se há texto f
                g_pos_y: int = rect.bottom - 10 if not f_text else rect.bottom - 5
                g_rect: pygame.Rect = g_surf.get_rect(center=(rect.centerx, g_pos_y))
                self.screen.blit(g_surf, g_rect)

    def _desenha_pilha(self) -> None:
        """
        Desenha os valores da pilha (Y, Z, T) acima do display principal.
        """
        # Posições relativas ao display principal
        # A pilha é desenhada de baixo para cima (Y, Z, T)
        # O valor 'Y' (stack[1]) será o mais próximo do display principal
        base_y_pos = c.POS_Y_TELA +55 # Posição Y para a parte inferior do texto 'Y'
        line_height = 20 # Altura aproximada de uma linha de texto da pilha
        
        # Exibe Y, Z, T (índices 1, 2, 3 da pilha)
        # A ordem de exibição é T, Z, Y (de cima para baixo na tela)
        # Mas a iteração é feita para posicionar de baixo para cima
        for i, label_text in enumerate(["Y", "Z", "T"]): # Y é o primeiro a ser posicionado (mais baixo)
            stack_index = 1 + i # Y=stack[1], Z=stack[2], T=stack[3]
            stack_value = self.calculator.stack[stack_index]
            
            # Formata o valor da pilha
            formatted_value = self.calculator._format_number(stack_value, self.calculator.display_decimals)
            
            # Calcula a posição Y para a linha atual
            current_y_pos = base_y_pos - (i * line_height)

            text_surf = self.font_stack_small.render(f"{label_text}: {formatted_value}", True, c.COR_TEXTO_TELA)
            text_rect = text_surf.get_rect(midright=(c.POS_X_TELA + c.LARGURA_TELA - 15, current_y_pos))
            self.screen.blit(text_surf, text_rect)

    def desenha_tela(self, texto: str) -> None:
        """
        Desenha o texto fornecido na tela da calculadora.
        """
        pygame.draw.rect(self.screen, c.COR_TELA_FUNDO, 
                         (c.POS_X_TELA, c.POS_Y_TELA, c.LARGURA_TELA, c.ALTURA_TELA), 
                         border_radius=5)
        
        texto_surf: pygame.Surface = self.font_tela.render(texto, True, c.COR_TEXTO_TELA)
        texto_rect: pygame.Rect = texto_surf.get_rect(midright=(c.POS_X_TELA + c.LARGURA_TELA - 15, c.POS_Y_TELA +35+ c.ALTURA_TELA / 2))
        self.screen.blit(texto_surf, texto_rect)

    def _desenha_indicadores(self, f_active: bool, g_active: bool) -> None:
        """
        Desenha os indicadores 'f' e 'g' na tela se estiverem ativos.
        """
        if f_active:
            f_surf: pygame.Surface = self.font_indicador.render('f', True, c.COR_TEXTO_TELA)
            f_rect: pygame.Rect = f_surf.get_rect(bottomleft=(c.POS_X_TELA + 10, c.POS_Y_TELA + c.ALTURA_TELA - 5))
            self.screen.blit(f_surf, f_rect)
        if g_active:
            g_surf: pygame.Surface = self.font_indicador.render('g', True, c.COR_TEXTO_TELA)
            g_rect: pygame.Rect = g_surf.get_rect(bottomleft=(c.POS_X_TELA + 25, c.POS_Y_TELA + c.ALTURA_TELA - 5))
            self.screen.blit(g_surf, g_rect)

    def desenha_tudo(self, f_active: bool, g_active: bool) -> None:
        """
        Chama todos os métodos de desenho para renderizar a calculadora completa.
        """
        self.screen.fill(c.COR_FUNDO)
        self._desenha_corpo()
        self._desenha_botoes()
        self.desenha_tela(self.calculator.get_display()) # Obtém o texto do display principal da calculadora
        self._desenha_pilha() # Chama o novo método para desenhar a pilha
        self._desenha_indicadores(f_active, g_active)
        pygame.display.flip()

    def get_botao_clicado(self, pos: Tuple[int, int]) -> Optional[str]:
        """
        Verifica se uma posição de clique corresponde a algum botão.
        """
        for rect, acao in self.botoes_rects:
            if rect.collidepoint(pos):
                return acao
        return None
