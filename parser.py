"""
Парсер ассемблерного кода для УВМ (Вариант 6)
Этап 1: Перевод в промежуточное представление
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any


@dataclass
class Command:
    """Промежуточное представление команды"""
    opcode: int          # Код операции
    mnemonic: str       # Мнемоника
    args: List[int]     # Числовые аргументы
    size: int          # Размер команды в байтах
    line_num: int      # Номер строки в исходном коде
    raw_line: str      # Исходная строка


class Parser:
    """Парсер ассемблерного кода"""
    
    # Словарь команд УВМ (Вариант 6)
    INSTRUCTIONS: Dict[str, Dict[str, Any]] = {
        'LOAD': {
            'opcode': 6, 
            'size': 5, 
            'args': 1,
            'desc': 'Загрузка константы в аккумулятор'
        },
        'READ': {
            'opcode': 3, 
            'size': 2, 
            'args': 1,
            'desc': 'Чтение из памяти по адресу (аккум + смещение)'
        },
        'STORE': {
            'opcode': 2, 
            'size': 3, 
            'args': 1,
            'desc': 'Запись аккумулятора в память по адресу'
        },
        'BITREV': {
            'opcode': 1, 
            'size': 3, 
            'args': 1,
            'desc': 'Обращение битов значения в памяти'
        },
    }
    
    def __init__(self):
        self.labels: Dict[str, int] = {}  # Таблица меток: имя -> адрес
        self.current_line = 0
        self.current_address = 0
    
    def parse(self, source_code: str) -> List[Command]:
        """Разбор исходного кода в промежуточное представление"""
        
        lines = source_code.split('\n')
        commands: List[Command] = []
        
        # Первый проход: сбор меток и определение адресов
        self._first_pass(lines)
        
        # Второй проход: парсинг команд
        for line_num, line in enumerate(lines, 1):
            line = self._clean_line(line)
            if not line:
                continue
                
            # Пропускаем метки (они уже обработаны)
            if line.endswith(':'):
                continue
                
            try:
                command = self._parse_line(line, line_num)
                commands.append(command)
            except Exception as e:
                raise ValueError(f"Строка {line_num}: {e}\n  Текст: '{line}'")
        
        return commands
    
    def _first_pass(self, lines: List[str]) -> None:
        """Первый проход: сбор меток"""
        self.current_address = 0
        
        for line_num, line in enumerate(lines, 1):
            line = self._clean_line(line)
            if not line:
                continue
                
            # Проверка на метку
            if line.endswith(':'):
                label = line[:-1].strip()
                if label in self.labels:
                    raise ValueError(f"Повторное определение метки '{label}'")
                self.labels[label] = self.current_address
                continue
                
            # Определение размера команды
            parts = line.split()
            if parts:
                mnemonic = parts[0].upper()
                if mnemonic in self.INSTRUCTIONS:
                    self.current_address += self.INSTRUCTIONS[mnemonic]['size']
    
    def _clean_line(self, line: str) -> str:
        """Очистка строки от комментариев и лишних пробелов"""
        # Удаление комментариев (начинаются с ;)
        if ';' in line:
            line = line[:line.index(';')]
        
        # Удаление лишних пробелов
        line = line.strip()
        
        # Замена нескольких пробелов одним
        line = re.sub(r'\s+', ' ', line)
        
        # Удаление запятых (для совместимости)
        line = line.replace(',', ' ')
        
        return line
    
    def _parse_line(self, line: str, line_num: int) -> Command:
        """Разбор одной строки ассемблера"""
        
        parts = line.split()
        if not parts:
            raise ValueError("Пустая строка")
            
        mnemonic = parts[0].upper()
        
        if mnemonic not in self.INSTRUCTIONS:
            available = ', '.join(self.INSTRUCTIONS.keys())
            raise ValueError(
                f"Неизвестная команда: '{mnemonic}'. "
                f"Доступные команды: {available}"
            )
        
        info = self.INSTRUCTIONS[mnemonic]
        expected_args = info['args']
        
        # Проверка количества аргументов
        if len(parts) - 1 != expected_args:
            raise ValueError(
                f"Ожидалось {expected_args} аргумент(ов) для '{mnemonic}', "
                f"получено {len(parts) - 1}"
            )
        
        # Парсинг аргументов
        args: List[int] = []
        for i, arg_str in enumerate(parts[1:], 1):
            try:
                arg = self._parse_argument(arg_str)
                args.append(arg)
            except ValueError as e:
                raise ValueError(f"Аргумент {i}: {e}")
        
        # Проверка диапазонов аргументов
        self._validate_arguments(mnemonic, args)
        
        # Создание промежуточного представления
        return Command(
            opcode=info['opcode'],
            mnemonic=mnemonic,
            args=args,
            size=info['size'],
            line_num=line_num,
            raw_line=line
        )
    
    def _parse_argument(self, arg_str: str) -> int:
        """Парсинг аргумента в число"""
        
        arg_str = arg_str.strip().upper()
        
        # Проверка на метку
        if arg_str in self.labels:
            return self.labels[arg_str]
        
        # Парсинг чисел в разных системах счисления
        try:
            if arg_str.startswith('0X'):
                return int(arg_str[2:], 16)
            elif arg_str.startswith('0B'):
                return int(arg_str[2:], 2)
            elif arg_str.startswith('0'):
                return int(arg_str, 8)
            else:
                return int(arg_str)
        except ValueError:
            # Пробуем разрешить как выражение
            try:
                # Простые выражения типа 100+20
                return eval(arg_str, {"__builtins__": {}})
            except:
                raise ValueError(f"Не могу распознать аргумент: '{arg_str}'")
    
    def _validate_arguments(self, mnemonic: str, args: List[int]) -> None:
        """Проверка диапазонов аргументов"""
        
        if mnemonic == 'LOAD':
            if args[0] < 0 or args[0] >= (1 << 31):
                raise ValueError(
                    f"Константа {args[0]} вне диапазона 0..{2**31-1}"
                )
        
        elif mnemonic == 'READ':
            if args[0] < 0 or args[0] >= (1 << 8):
                raise ValueError(
                    f"Смещение {args[0]} вне диапазона 0..255"
                )
        
        elif mnemonic == 'STORE':
            if args[0] < 0 or args[0] >= (1 << 20):
                raise ValueError(
                    f"Адрес {args[0]} вне диапазона 0..{2**20-1}"
                )
        
        elif mnemonic == 'BITREV':
            if args[0] < 0 or args[0] >= (1 << 20):
                raise ValueError(
                    f"Адрес {args[0]} вне диапазона 0..{2**20-1}"
                )
    
    def get_instruction_info(self) -> Dict[str, Dict[str, Any]]:
        """Получить информацию о всех инструкциях"""
        return self.INSTRUCTIONS.copy()
