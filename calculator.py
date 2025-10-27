"""
Módulo da Calculadora (Engine).

Este módulo contém a classe `Calculator`, que implementa toda a lógica funcional
da calculadora HP-12C, incluindo a pilha RPN, o registro de entrada e as
operações matemáticas e financeiras.
"""

from decimal import Decimal, getcontext
import math
import datetime
import constants as c
from typing import List, Dict, Optional, Callable, Any

# Configura a precisão para as operações com Decimal
getcontext().prec = 28

class Calculator:
    """
    A classe Calculator simula o funcionamento interno de uma HP-12C.
    """
    # Atributos da classe com type hints
    f_map: Dict[str, Optional[str]]
    g_map: Dict[str, Optional[str]]
    storage_regs: List[Decimal]
    fin_regs: Dict[str, Decimal]
    stat_regs: Dict[str, Decimal]
    stack: List[Decimal]
    entry_buffer: str
    is_entering: bool
    f_active: bool
    g_active: bool
    sto_active: bool
    rcl_active: bool
    display_decimals: int
    is_entering_exponent: bool
    exponent_buffer: str

    def __init__(self) -> None:
        """
        Inicializa a calculadora, a pilha RPN, o estado de entrada e os mapas de função.
        """
        # Mapeia a tecla principal para suas funções f e g
        self.f_map = {b['main']: b['f'] for b in c.BOTOES if b.get('f')}
        self.g_map = {b['main']: b['g'] for b in c.BOTOES if b.get('g')}

        # Registradores de Armazenamento (0-9)
        self.storage_regs = [Decimal(0)] * 10

        # Registradores Financeiros
        self.fin_regs = {
            'n': Decimal(0),
            'i': Decimal(0),
            'PV': Decimal(0),
            'PMT': Decimal(0),
            'FV': Decimal(0),
        }

        # Registradores Estatísticos
        self.stat_regs = {
            'n': Decimal(0),
            'Σx': Decimal(0),
            'Σx²': Decimal(0),
            'Σy': Decimal(0),
            'Σy²': Decimal(0),
            'Σxy': Decimal(0),
        }

        self._reset()
    def _format_number(self, number: Decimal, decimals: int) -> str:
        """Formata um número com separadores de milhares e casas decimais."""
        if number.is_nan():
            return "Error"

        # Formata o número com as casas decimais corretas
        formatted_str = f"{number:.{decimals}f}"
        
        # Separa a parte inteira da parte decimal
        if '.' in formatted_str:
            integer_part, decimal_part = formatted_str.split('.')
        else:
            integer_part, decimal_part = formatted_str, None

        # Adiciona separadores de milhares à parte inteira
        sign = ''
        if integer_part.startswith('-'):
            sign = '-'
            integer_part = integer_part[1:]
            
        if len(integer_part) > 3:
            # Inverte a string para facilitar a inserção dos pontos
            reversed_integer = integer_part[::-1]
            # Insere um ponto a cada 3 dígitos
            with_separators = '.'.join(reversed_integer[i:i+3] for i in range(0, len(reversed_integer), 3))
            # Desinverte para obter o formato correto
            integer_part = with_separators[::-1]

        # Remonta o número formatado
        if decimal_part is not None:
            return f"{sign}{integer_part},{decimal_part}"
        else:
            return f"{sign}{integer_part}"

    def _format_entry_buffer(self) -> str:
        """Formata o buffer de entrada com separadores de milhares."""
        if self.entry_buffer == "Error":
            return self.entry_buffer

        # O buffer interno e a exibição usam vírgula
        if ',' in self.entry_buffer:
            integer_part, decimal_part = self.entry_buffer.split(',', 1)
        else:
            integer_part, decimal_part = self.entry_buffer, None

        sign = ''
        if integer_part.startswith('-'):
            sign = '-'
            integer_part = integer_part[1:]
        
        # Adiciona separador de milhar na parte inteira
        if len(integer_part) > 3:
            reversed_integer = integer_part[::-1]
            with_separators = '.'.join(reversed_integer[i:i+3] for i in range(0, len(reversed_integer), 3))
            integer_part = with_separators[::-1]
        
        # Remonta a string para exibição
        if decimal_part is not None:
            return f"{sign}{integer_part},{decimal_part}"
        
        # Se o usuário acabou de digitar a vírgula
        if self.entry_buffer.endswith(','):
            return f"{sign}{integer_part},"

        return f"{sign}{integer_part}"

    def get_display(self) -> str:
        """
        Retorna o valor a ser exibido na tela.
        """
        if self.is_entering:
            if self.is_entering_exponent:
                # Formata a mantissa e anexa o expoente
                formatted_mantissa = self._format_entry_buffer()
                return f"{formatted_mantissa} {self.exponent_buffer.zfill(2)}"
            return self._format_entry_buffer()
        
        return self._format_number(self.stack[0], self.display_decimals)

    def press_key(self, key: str) -> None:
        """
        Processa o pressionamento de uma tecla, considerando os modificadores f e g.
        """
        # Lógica de STO/RCL tem prioridade
        if self.sto_active and key.isdigit() and len(key) == 1:
            self._handle_sto(int(key))
            return
        elif self.rcl_active and key.isdigit() and len(key) == 1:
            self._handle_rcl(int(key))
            return
        
        # Desativa os modos STO/RCL se outra tecla for pressionada
        self.sto_active = False
        self.rcl_active = False

        if self.f_active:
            # Tratamento especial para definir formato do display (f + dígito)
            if key.isdigit() and len(key) == 1:
                self._set_display_format(int(key))
                self.f_active = False
                return

            function_name: Optional[str] = self.f_map.get(key)
            self._execute_function(function_name)
            self.f_active = False
            return

        if self.g_active:
            function_name: Optional[str] = self.g_map.get(key)
            self._execute_function(function_name)
            self.g_active = False
            return

        self._execute_function(key) # Executa a função principal da tecla

    def _execute_function(self, func_name: Optional[str]) -> None:
        """
        Chama o método de tratamento correspondente ao nome da função.
        """
        if not func_name: return

        method_map = {
            '0': self._handle_digit, '1': self._handle_digit, '2': self._handle_digit,
            '3': self._handle_digit, '4': self._handle_digit, '5': self._handle_digit,
            '6': self._handle_digit, '7': self._handle_digit, '8': self._handle_digit,
            '9': self._handle_digit, ',': self._handle_digit,
            'ENTER': self._handle_enter,
            '+': self._handle_operator, '-': self._handle_operator,
            '×': self._handle_operator, '÷': self._handle_operator,
            'CHS': self._handle_chs,
            'ON': self._reset,
            'f': self._activate_f,
            'g': self._activate_g,
            'CLx': self._handle_clx,
            'x<>y': self._handle_swap_xy,
            'R↓': self._handle_roll_down,
            'y^x': self._handle_power,
            '1/x': self._handle_reciprocal,
            '√x': self._handle_sqrt,
            '%': self._handle_percent,
            'Δ%': self._handle_percent_delta,
            'STO': self._activate_sto,
            'RCL': self._activate_rcl,
            'Σ+': self._handle_sigma_plus,
            'CLΣ': self._handle_clear_sigma,
            'x̄': self._handle_mean,
            's': self._handle_std_dev,
            'SL': self._handle_sl_depreciation,
            'SOYD': self._handle_soyd_depreciation,
            'DB': self._handle_db_depreciation,
            'EEX': self._handle_eex,
            'ΔDYS': self._handle_delta_days,
            'DATE': self._handle_date_calc,
            'n': self._handle_fin_op, 'i': self._handle_fin_op, 'PV': self._handle_fin_op,
            'PMT': self._handle_fin_op, 'FV': self._handle_fin_op,
        }
        
        method = method_map.get(func_name)
        if method:
            # Passa o nome da função para métodos que tratam múltiplos casos
            if func_name in ['+', '-', '×', '÷'] or func_name.isdigit() or func_name == ',' or func_name in self.fin_regs:
                method(func_name)
            else:
                method()
        else:
            print(f"Função '{func_name}' não implementada.")

    # --- MÉTODOS DE ESTADO E MODIFICADORES ---
    def _reset(self) -> None:
        self.stack = [Decimal(0)] * 4
        self.entry_buffer = "0"
        self.is_entering = False
        self.f_active = False
        self.g_active = False
        self.sto_active = False
        self.rcl_active = False
        self.display_decimals = 2
        self.is_entering_exponent = False
        self.exponent_buffer = ''
        # Limpa também os registros estatísticos
        for key in self.stat_regs:
            self.stat_regs[key] = Decimal(0)

    def _activate_f(self) -> None:
        self.f_active = True
        self.g_active = False

    def _activate_g(self) -> None:
        self.g_active = True
        self.f_active = False
        self.sto_active = False
        self.rcl_active = False

    def _activate_sto(self) -> None:
        self.sto_active = True
        self.rcl_active = False
        self.f_active = False
        self.g_active = False

    def _activate_rcl(self) -> None:
        self.rcl_active = True
        self.sto_active = False
        self.f_active = False
        self.g_active = False

    def _set_display_format(self, num_decimals: int) -> None:
        """Define o número de casas decimais para exibição."""
        if 0 <= num_decimals <= 9:
            self.display_decimals = num_decimals

    def _finalize_entry(self) -> None:
        if self.is_entering:
            if not self.entry_buffer or self.entry_buffer == '-':
                self.is_entering = False
                return

            # Substitui a vírgula do buffer por um ponto para o construtor Decimal
            entry_str_for_decimal = self.entry_buffer.replace(',', '.')

            full_number_str = entry_str_for_decimal
            if self.is_entering_exponent:
                if self.exponent_buffer:
                    full_number_str += 'e' + self.exponent_buffer
                else:
                    full_number_str += 'e0'

            try:
                # Se o buffer terminar com um ponto (após a substituição da vírgula), remove-o
                if full_number_str.endswith('.'):
                    full_number_str = full_number_str[:-1]
                
                value = Decimal(full_number_str)
                self._push_stack(value)
            except Exception as e:
                print(f"Erro ao finalizar entrada: {e}")
                self.stack[0] = Decimal('nan')
            
            self.is_entering = False
            self.is_entering_exponent = False
            self.exponent_buffer = ''

    # --- MÉTODOS DE MANIPULAÇÃO DA PILHA ---
    def _push_stack(self, value: Decimal) -> None:
        self.stack = [value] + self.stack[:-1]

    def _pop_stack(self) -> Decimal:
        x: Decimal = self.stack[0]
        self.stack = self.stack[1:] + [self.stack[-1]]
        return x

    def _handle_roll_down(self) -> None:
        self._finalize_entry()
        self.stack = self.stack[1:] + self.stack[:1]

    def _handle_swap_xy(self) -> None:
        self._finalize_entry()
        self.stack[0], self.stack[1] = self.stack[1], self.stack[0]

    # --- MÉTODOS DE ARMAZENAMENTO ---
    def _handle_sto(self, reg_idx: int) -> None:
        """Armazena o valor de X no registro de memória especificado."""
        self._finalize_entry()
        if 0 <= reg_idx < len(self.storage_regs):
            self.storage_regs[reg_idx] = self.stack[0]
            print(f"Valor {self.stack[0]} armazenado no registro {reg_idx}")

    def _handle_rcl(self, reg_idx: int) -> None:
        """Recupera um valor do registro de memória e o empurra para a pilha."""
        self._finalize_entry()
        if 0 <= reg_idx < len(self.storage_regs):
            value: Decimal = self.storage_regs[reg_idx]
            self._push_stack(value)
            print(f"Valor {value} recuperado do registro {reg_idx}")

    # --- MÉTODOS DE ENTRADA E OPERAÇÕES BÁSICAS ---
    def _handle_digit(self, digit: str) -> None:
        if self.is_entering_exponent:
            if len(self.exponent_buffer) < 2:  # Limita o expoente a 2 dígitos
                self.exponent_buffer += digit
            return

        if not self.is_entering or self.entry_buffer == "Error":
            self.is_entering = True
            # Internamente, o buffer de entrada usa vírgula
            self.entry_buffer = "0," if digit == ',' else digit
        else:
            # Apenas um separador decimal é permitido
            if digit == ',' and ',' in self.entry_buffer: return
            
            # Adiciona o dígito ou a vírgula ao buffer
            self.entry_buffer += digit

    def _handle_enter(self) -> None:
        self._finalize_entry()
        if not self.is_entering: self._push_stack(self.stack[0])

    def _handle_clx(self) -> None:
        if self.is_entering:
            self.entry_buffer = "0"
            self.is_entering = False
        else:
            self.stack[0] = Decimal(0)

    def _handle_chs(self) -> None:
        if self.is_entering:
            if self.is_entering_exponent:
                if self.exponent_buffer.startswith('-'): self.exponent_buffer = self.exponent_buffer[1:]
                elif self.exponent_buffer != '0': self.exponent_buffer = '-' + self.exponent_buffer
            else:
                if self.entry_buffer.startswith('-'): self.entry_buffer = self.entry_buffer[1:]
                elif self.entry_buffer != '0': self.entry_buffer = '-' + self.entry_buffer
        else:
            self.stack[0] = -self.stack[0]

    def _handle_eex(self) -> None:
        """Ativa o modo de entrada de expoente."""
        if not self.is_entering: # Se não estiver digitando um número, assume 0 EEX
            self.entry_buffer = "0"
            self.is_entering = True
        self.is_entering_exponent = True
        self.exponent_buffer = "0"

    def _handle_operator(self, op: str) -> None:
        self._finalize_entry()
        x: Decimal = self._pop_stack()
        y: Decimal = self._pop_stack()
        result: Decimal = Decimal(0)
        if op == '+': result = y + x
        elif op == '-': result = y - x
        elif op == '×': result = y * x
        elif op == '÷':
            if x == 0: self.stack[0] = Decimal('nan'); return
            result = y / x
        self._push_stack(result)

    # --- NOVAS FUNÇÕES MATEMÁTICAS ---
    def _handle_power(self) -> None:
        """Calcula y^x."""
        self._finalize_entry()
        x: Decimal = self._pop_stack()
        y: Decimal = self._pop_stack()
        try:
            result: Decimal = y ** x
        except:
            result = Decimal('nan')
        self._push_stack(result)

    def _handle_reciprocal(self) -> None:
        """Calcula 1/x."""
        self._finalize_entry()
        x: Decimal = self.stack[0]
        if x == 0:
            self.stack[0] = Decimal('nan')
            return
        self.stack[0] = 1 / x

    def _handle_sqrt(self) -> None:
        """Calcula a raiz quadrada de x."""
        self._finalize_entry()
        x: Decimal = self.stack[0]
        if x < 0:
            self.stack[0] = Decimal('nan')
            return
        self.stack[0] = x.sqrt()

    def _handle_percent(self) -> None:
        """Calcula a porcentagem de y em relação a x (y * (x/100))."""
        self._finalize_entry()
        x: Decimal = self._pop_stack()
        y: Decimal = self._pop_stack()
        result: Decimal = y * (x / 100)
        self._push_stack(result)

    def _handle_percent_delta(self) -> None:
        """Calcula a variação percentual de y para x."""
        self._finalize_entry()
        x: Decimal = self._pop_stack()
        y: Decimal = self._pop_stack()
        if y == 0:
            self.stack[0] = Decimal('nan')
            return
        result: Decimal = ((x - y) / y) * 100
        self._push_stack(result)

    # --- FUNÇÕES ESTATÍSTICAS ---
    def _handle_clear_sigma(self) -> None:
        """Limpa todos os registros estatísticos."""
        for key in self.stat_regs:
            self.stat_regs[key] = Decimal(0)
        print("Registros estatísticos limpos.")

    def _handle_sigma_plus(self) -> None:
        """Adiciona os valores de x e y aos somatórios estatísticos."""
        self._finalize_entry()
        x: Decimal = self.stack[0]
        y: Decimal = self.stack[1]

        self.stat_regs['n'] += 1
        self.stat_regs['Σx'] += x
        self.stat_regs['Σx²'] += x**2
        self.stat_regs['Σy'] += y
        self.stat_regs['Σy²'] += y**2
        self.stat_regs['Σxy'] += x * y

        # Após Σ+, o visor mostra o novo n
        self._push_stack(self.stat_regs['n'])

    def _handle_mean(self) -> None:
        """Calcula a média de x (x̄)."""
        n: Decimal = self.stat_regs['n']
        if n == 0:
            self.stack[0] = Decimal('nan')
            return
        mean_x: Decimal = self.stat_regs['Σx'] / n
        self._push_stack(mean_x)

    def _handle_std_dev(self) -> None:
        """Calcula o desvio padrão amostral de x (s)."""
        n: Decimal = self.stat_regs['n']
        if n < 2:
            self.stack[0] = Decimal('nan')
            return
        
        sum_x: Decimal = self.stat_regs['Σx']
        sum_x_sq: Decimal = self.stat_regs['Σx²']
        
        # Fórmula: sqrt( (n * Σx² - (Σx)²) / (n * (n-1)) )
        try:
            numerator: Decimal = n * sum_x_sq - sum_x**2
            denominator: Decimal = n * (n - 1)
            if denominator == 0: self.stack[0] = Decimal('nan'); return
            
            variance: Decimal = numerator / denominator
            if variance < 0: self.stack[0] = Decimal('nan'); return

            std_dev: Decimal = variance.sqrt()
            self._push_stack(std_dev)
        except:
            self.stack[0] = Decimal('nan')


    # --- FUNÇÕES DE DATA ---
    def _parse_date_number(self, date_num: Decimal) -> Optional[datetime.date]:
        """Converte um número no formato DD.MMYYYY para um objeto datetime.date."""
        try:
            # Remove separadores de milhar e converte separador decimal para formato interno
            date_str = str(date_num).replace('.', '').replace(',', '.')
            
            # Se o número for um inteiro, pode não ter parte decimal
            if '.' in date_str:
                day_month_year = date_str.split('.')
                day = int(day_month_year[0])
                # A lógica para extrair mês e ano precisa ser robusta
                if len(day_month_year[1]) == 4: # Formato MMYY
                    month = int(day_month_year[1][:2])
                    year = int(day_month_year[1][2:])
                elif len(day_month_year[1]) >= 5: # Formato MMDDDDAAAA
                    month = int(day_month_year[1][:2])
                    year = int(day_month_year[1][2:6])
                else:
                    raise ValueError("Formato de data inválido")
            else: # Formato DDMMAAAA
                date_str = str(int(date_num))
                day = int(date_str[:2])
                month = int(date_str[2:4])
                year = int(date_str[4:])

            # Ajuste para anos de 2 dígitos (ex: 79 -> 1979)
            if year < 100:
                year += 1900

            return datetime.date(year, month, day)
        except (ValueError, IndexError):
            return None

    def _format_date_to_number(self, date_obj: datetime.date) -> Decimal:
        """Converte um objeto datetime.date para um número no formato DD,MMYYYY."""
        if not date_obj: return Decimal('nan')
        # O formato para Decimal deve usar ponto
        return Decimal(f"{date_obj.day:02d}.{date_obj.month:02d}{date_obj.year}")

    def _handle_delta_days(self) -> None:
        """Calcula o número de dias entre duas datas (Y e X)."""
        self._finalize_entry()
        date2_num: Decimal = self._pop_stack()
        date1_num: Decimal = self._pop_stack()

        date2: Optional[datetime.date] = self._parse_date_number(date2_num)
        date1: Optional[datetime.date] = self._parse_date_number(date1_num)

        if not date1 or not date2:
            self.stack[0] = Decimal('nan')
            return
        
        delta: datetime.timedelta = date2 - date1
        self._push_stack(Decimal(delta.days))

    def _handle_date_calc(self) -> None:
        """Calcula uma data futura ou passada (Y + X dias)."""
        self._finalize_entry()
        days_to_add: Decimal = self._pop_stack()
        start_date_num: Decimal = self._pop_stack()

        start_date: Optional[datetime.date] = self._parse_date_number(start_date_num)

        if not start_date:
            self.stack[0] = Decimal('nan')
            return
        
        try:
            result_date: datetime.date = start_date + datetime.timedelta(days=int(days_to_add))
            self._push_stack(self._format_date_to_number(result_date))
        except OverflowError:
            self.stack[0] = Decimal('nan') # Data fora do range suportado
            return

    # --- FUNÇÕES DE DEPRECIAÇÃO ---
    def _handle_sl_depreciation(self) -> None:
        """Calcula a depreciação anual pelo método da Linha Reta (Straight-Line)."""
        self._finalize_entry()
        life: Decimal = self._pop_stack()
        salvage_value: Decimal = self._pop_stack()
        cost: Decimal = self._pop_stack()

        if life == 0: self.stack[0] = Decimal('nan'); return
        
        depreciation: Decimal = (cost - salvage_value) / life
        self._push_stack(depreciation)

    def _handle_soyd_depreciation(self) -> None:
        """Calcula a depreciação pelo método da Soma dos Dígitos dos Anos (SOYD)."""
        self._finalize_entry()
        period: Decimal = self._pop_stack()
        life: Decimal = self._pop_stack()
        salvage_value: Decimal = self._pop_stack()
        cost: Decimal = self._pop_stack()

        if life == 0 or period == 0 or period > life: self.stack[0] = Decimal('nan'); return

        sum_of_years_digits: Decimal = life * (life + 1) / 2
        remaining_life: Decimal = life - period + 1
        
        depreciation: Decimal = (cost - salvage_value) * (remaining_life / sum_of_years_digits)
        self._push_stack(depreciation)

    def _handle_db_depreciation(self) -> None:
        """Calcula a depreciação pelo método dos Saldos Decrescentes (Declining Balance)."""
        self._finalize_entry()
        rate_percent: Decimal = self._pop_stack() # Taxa de depreciação em porcentagem (e.g., 200 para 200%)
        period: Decimal = self._pop_stack()
        life: Decimal = self._pop_stack()
        salvage_value: Decimal = self._pop_stack()
        cost: Decimal = self._pop_stack()

        if life == 0 or period == 0 or period > life: self.stack[0] = Decimal('nan'); return
        if rate_percent <= 0: self.stack[0] = Decimal('nan'); return

        depreciation_rate: Decimal = rate_percent / 100 / life
        book_value: Decimal = cost
        depreciation: Decimal = Decimal(0)

        for p in range(1, int(period) + 1):
            if book_value <= salvage_value: # Não deprecia abaixo do valor residual
                depreciation = Decimal(0)
                break
            
            current_depreciation: Decimal = book_value * depreciation_rate
            if book_value - current_depreciation < salvage_value:
                current_depreciation = book_value - salvage_value
            
            book_value -= current_depreciation
            depreciation = current_depreciation # Apenas o último período é retornado

        self._push_stack(depreciation)

    def _handle_fin_op(self, key: str):
        """
        Lida com o armazenamento ou cálculo de uma variável financeira.
        """
        was_entering = self.is_entering
        self._finalize_entry()

        if was_entering:
            # Armazena o valor do registrador X no registrador financeiro
            self.fin_regs[key] = self.stack[0]
            print(f"Armazenado {self.stack[0]} em {key}")
        else:
            # Calcula o valor para a tecla pressionada
            n = self.fin_regs['n']
            i = self.fin_regs['i'] / 100
            pv = self.fin_regs['PV']
            pmt = self.fin_regs['PMT']
            fv = self.fin_regs['FV']

            if key == 'FV':
                if i == 0:
                    result = - (pv + pmt * n)
                else:
                    result = - (pv * (1 + i)**n + pmt * (((1 + i)**n - 1) / i))
            elif key == 'PV':
                if i == 0:
                    result = - (fv + pmt * n)
                else:
                    result = - (fv + pmt * (((1 + i)**n - 1) / i)) / (1 + i)**n
            elif key == 'PMT':
                if i == 0:
                    if n == 0: self.stack[0] = Decimal('nan'); return
                    result = - (pv + fv) / n
                else:
                    denominator = ((1 + i)**n - 1) / i
                    if denominator == 0: self.stack[0] = Decimal('nan'); return
                    result = - (pv * (1 + i)**n + fv) / denominator
            elif key == 'n':
                if i == 0:
                    if pmt == 0: self.stack[0] = Decimal('nan'); return
                    result = - (pv + fv) / pmt
                else:
                    # log( (PMT - FV*i) / (PV*i + PMT) ) / log(1+i)
                    try:
                        log_arg_num = pmt - fv * i
                        log_arg_den = pv * i + pmt
                        if log_arg_den == 0 or log_arg_num / log_arg_den <= 0:
                            self.stack[0] = Decimal('nan'); return
                        
                        log_arg = log_arg_num / log_arg_den
                        result = Decimal(math.log(log_arg)) / Decimal(math.log(1+i))
                    except (ValueError, ZeroDivisionError):
                        self.stack[0] = Decimal('nan'); return
            elif key == 'i':
                result = self._solve_for_i(n, pv, pmt, fv) * 100 # Converte para porcentagem
            else:
                print(f"Cálculo para '{key}' ainda não implementado.")
                return
            
            self.fin_regs[key] = result
            self.stack[0] = result

    def _solve_for_i(self, n: Decimal, pv: Decimal, pmt: Decimal, fv: Decimal) -> Decimal:
        """
        Usa um método numérico (método da Secante) para encontrar a taxa de juros i.
        """
        if n <= 0: return Decimal('nan')

        # Função TVM (Time Value of Money) que queremos zerar
        def f(rate: Decimal) -> Decimal:
            if rate == 0:
                return pv + pmt * n + fv
            else:
                return pv * (1 + rate)**n + pmt * (1 + rate/12) * (((1 + rate)**n - 1) / rate) + fv

        # Chutes iniciais e parâmetros do solucionador
        i0: Decimal = Decimal('0.005')
        i1: Decimal = Decimal('0.01')
        max_iter: int = 100
        tol: Decimal = Decimal('1e-9')

        for _ in range(max_iter):
            f0: Decimal = f(i0)
            f1: Decimal = f(i1)
            if abs(f1) < tol:
                return i1
            
            if (f1 - f0) == 0: return Decimal('nan') # Divisão por zero
            
            i_next: Decimal = i1 - f1 * (i1 - i0) / (f1 - f0)

            if abs(i_next - i1) < tol:
                return i_next

            i0, i1 = i1, i_next

        return Decimal('nan') # Não convergiu
