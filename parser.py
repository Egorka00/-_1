"""
Парсер ассемблерного кода для УВМ (Вариант 6)
Синтаксис: мнемоника аргумент, аргумент, ...
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class Command:
    """Промежуточное представление команды"""
    opcode: int          # Код операции
    mnemonic: str       # Мнемоника
    args: List[Union[int, str]]  # Аргументы
    size: int          # Размер команды в байтах
    description: str   # Описание для отладки

class Parser:
    """Парсер ассемблерного кода"""
    
    # Словарь команд УВМ (Вариант 6)
    INSTRUCTIONS = {
        'LOAD': {'opcode': 6, 'size': 5, 'args': 1},      # Загрузка константы
        'READ': {'opcode': 3, 'size': 2, 'args': 1},      # Чтение из памяти
        'STORE': {'opcode': 2, 'size': 3, 'args': 1},     # Запись в память
        'BITREV': {'opcode': 1, 'size': 3, 'args': 1},    # Обращение битов
    }
    
    def __init__(self):
        self.labels = {}  # Таблица меток
        
    def parse(self, source_code: str) -> List[Command]:
        """Разбор исходного кода в промежуточное представление"""
        
        lines = source_code.split('\n')
        commands = []
        
        # Первый проход: сбор меток
        current_address = 0
        for line_num, line in enumerate(lines, 1):
            line = self._clean_line(line)
            if not line:
                continue
                
            # Проверка на метку
            if line.endswith(':'):
                label = line[:-1].strip()
                self.labels[label] = current_address
                continue
                
            # Определение команды и её размера
            parts = line.split()
            if parts:
                mnemonic = parts[0].upper()
                if mnemonic in self.INSTRUCTIONS:
                    current_address += self.INSTRUCTIONS[mnemonic]['size']
        
        # Второй проход: парсинг команд
        for line_num, line in enumerate(lines, 1):
            line = self._clean_line(line)
            if not line or line.endswith(':'):
                continue
                
            try:
                command = self._parse_line(line, line_num)
                commands.append(command)
            except Exception as e:
                raise SyntaxError(f"Строка {line_num}: {e}")
        
        return commands
    
    def _clean_line(self, line: str) -> str:
        """Очистка строки от комментариев и лишних пробелов"""
        # Удаление комментариев
        if ';' in line:
            line = line[:line.index(';')]
        return line.strip()
    
    def _parse_line(self, line: str, line_num: int) -> Command:
        """Разбор одной строки ассемблера"""
        
        parts = line.split()
        mnemonic = parts[0].upper()
        
        if mnemonic not in self.INSTRUCTIONS:
            raise ValueError(f"Неизвестная команда: {mnemonic}")
        
        info = self.INSTRUCTIONS[mnemonic]
        expected_args = info['args']
        
        # Проверка количества аргументов
        if len(parts) - 1 != expected_args:
            raise ValueError(
                f"Ожидалось {expected_args} аргумент(ов) для {mnemonic}, "
                f"получено {len(parts) - 1}"
            )
        
        # Парсинг аргументов
        args = []
        for arg_str in parts[1:]:
            arg = self._parse_argument(arg_str)
            args.append(arg)
        
        # Создание промежуточного представления
        return Command(
            opcode=info['opcode'],
            mnemonic=mnemonic,
            args=args,
            size=info['size'],
            description=f"Строка {line_num}: {line}"
        )
    
    def _parse_argument(self, arg_str: str) -> Union[int, str]:
        """Парсинг аргумента (число или метка)"""
        
        # Удаление возможных префиксов
        arg_str = arg_str.strip().upper()
        
        # Проверка на метку
        if arg_str in self.labels:
            return self.labels[arg_str]
        
        # Парсинг чисел
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
            # Если не число, считаем меткой (будет разрешена позже)
            return arg_str
    
    def _resolve_labels(self, commands: List[Command]) -> List[Command]:
        """Разрешение меток в числовые значения"""
        resolved = []
        for cmd in commands:
            resolved_args = []
            for arg in cmd.args:
                if isinstance(arg, str) and arg in self.labels:
                    resolved_args.append(self.labels[arg])
                else:
                    resolved_args.append(arg)
            cmd.args = resolved_args
            resolved.append(cmd)
        return resolved
