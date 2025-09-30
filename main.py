"""
Módulo Principal da Aplicação.

Este é o ponto de entrada do simulador da HP-12C. Ele inicializa a interface do usuário,
controla o loop principal de eventos e, futuramente, irá instanciar e se comunicar
com o motor da calculadora.
"""
import pygame
from ui import UI
from calculator import Calculator
import constants as c
from typing import Optional, Tuple

def main() -> None:
    """
    Função principal que executa a aplicação.
    """
    ui: UI = UI()
    calc: Calculator = Calculator()
    
    rodando: bool = True

    while rodando:
        texto_tela: str = calc.get_display()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # event.pos é uma tupla (x, y)
                botao_clicado: Optional[str] = ui.get_botao_clicado(event.pos)
                if botao_clicado:
                    print(f"Botão clicado: {botao_clicado}")
                    calc.press_key(botao_clicado)
            
            if event.type == pygame.KEYDOWN:
                if event.key in c.KEY_MAP:
                    acao: str = c.KEY_MAP[event.key]
                    print(f"Tecla pressionada: {pygame.key.name(event.key)} -> Ação: {acao}")
                    calc.press_key(acao)

        ui.desenha_tudo(texto_tela, calc.f_active, calc.g_active)

    pygame.quit()

if __name__ == "__main__":
    main()
