# Simulador de Calculadora HP-12C em Python

Este projeto é uma recriação funcional da clássica calculadora financeira HP-12C, utilizando Python e a biblioteca Pygame para a interface gráfica.

O objetivo é simular o comportamento da calculadora original, incluindo sua lógica de Notação Polonesa Reversa (RPN) e suas principais funções financeiras.

## Recursos Implementados (Versão 1.0)

*   **Interface Gráfica**: Layout visual fiel à calculadora HP-12C física.
*   **Lógica RPN**: Operação baseada em pilha com as teclas `ENTER`, `CHS`, `CLx`, `R↓` (Rolar Pilha) e `x<>y` (Trocar X e Y).
*   **Operadores Aritméticos**: Adição (`+`), Subtração (`-`), Multiplicação (`×`), Divisão (`÷`).
*   **Funções Matemáticas**: Potência (`y^x`), Inverso (`1/x`) e Raiz Quadrada (`√x`).
*   **Funções de Porcentagem**: Porcentagem (`%`) e Variação Percentual (`Δ%`).
*   **Funções Financeiras (TVM)**: Implementação completa para cálculo de `n` (períodos), `i` (juros), `PV` (valor presente), `PMT` (pagamentos) e `FV` (valor futuro).
*   **Teclas Modificadoras**: Suporte para as teclas `f` (laranja) e `g` (azul) para acesso a funções secundárias, com indicadores visuais na tela.

## Como Executar

Siga os passos abaixo para rodar a calculadora em seu computador.

### Pré-requisitos

*   Python 3.6 ou superior instalado.

### 1. Instale a dependência (Pygame)

Abra o seu terminal ou prompt de comando e execute o seguinte comando para instalar a biblioteca Pygame:

```bash
pip install pygame
```

### 2. Execute a Calculadora

Navegue até o diretório do projeto no seu terminal e execute o arquivo `main.py`:

```bash
python main.py
```

Uma janela com a calculadora HP-12C irá aparecer, e você poderá começar a usá-la clicando nos botões com o mouse.
