'''
Módulo Principal da Aplicação.

Este é o ponto de entrada do simulador da HP-12C. Ele inicializa a interface do usuário,
controla o loop principal de eventos e, futuramente, irá instanciar e se comunicar
com o motor da calculadora.
'''
import pygame
from ui import UI
from calculator import Calculator
import constants as c

def main() -> None:
    '''
    Função principal que executa a aplicação.
    '''
    calculator = Calculator()
    ui = UI(calculator) # Passa a instância da calculadora para a UI

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    key = ui.get_botao_clicado(event.pos)
                    if key:
                        calculator.press_key(key)
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                key_char = None

                # Verifica se a tecla Shift está pressionada
                if mods & pygame.KMOD_SHIFT:
                    key_char = c.SHIFT_KEY_MAP.get(event.key)
                
                # Se não encontrou no mapa de Shift, tenta no mapa principal
                if not key_char:
                    key_char = c.KEY_MAP.get(event.key)

                if key_char:
                    calculator.press_key(key_char)

        # Update UI
        ui.desenha_tudo(calculator.f_active, calculator.g_active) # Não passa texto_tela aqui

    pygame.quit()

if __name__ == "__main__":
    main()
