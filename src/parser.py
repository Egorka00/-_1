"""
Парсер ассемблера для УВМ (Вариант 6)
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import re


@dataclass
class Command:
    """Промежуточное представление команды"""
    opcode: int
    mnemonic: str
    args: List[int]
    size: int
    line_num: int
    source: str
    
    def __str__(self):
        args_str = ', '.join(str(arg) for arg in self.args)
        return f"{self.mnemonic} {args_str}"


class Parser:
    """Парсер исходного кода"""
    
    # Инструкции УВМ (Вариант 6)
    INSTRUCTIONS: Dict[str, Dict[str, Any]] = {
        'LOAD': {
            'opcode': 6,
            'size': 5,
            'args_count': 1,
            'format': 'A=6 (0-2 биты), B=константа (3-33 биты)'
        },
        'READ': {
            'opcode': 3,
            'size': 2,
            'args_count': 1,
            'format': 'A=3 (0-2 биты), B=смещение (3-10 биты)'
        },
        'STORE': {
            'opcode': 2,
            'size': 3,
            'args_count': 1,
            'format': 'A=2 (0-2 биты), B=адрес (3-22 биты)'
        },
        'BITREV': {
            'opcode': 1,
            'size': 3,
            'args_count': 1,
            'format': 'A=1 (0-2 биты), B=адрес (3-22 биты)'
        }
    }
    
    def __init__(self):
        self.labels: Dict[str, int] = {}
        self.errors: List[str] = []
    
    def parse(self, source_code: str) -> List[Command]:
        """
        Парсинг исходного кода
        
        Returns:
            Список команд в промежуточном представлении
        """
        lines = source_code.split('\n')
        commands: List[Command] = []
        
        # Первый проход: сбор меток
        address = 0
        for line_num, line in enumerate(lines, 1):
            line = self._clean_line(line)
            if not line:
                continue
            
            # Проверка на метку
            if line.endswith(':'):
                label = line[:-1].strip()
                if label in self.labels:
                    self.errors.append(f"Повторная метка '{label}' в строке {line_num}")
                else:
                    self.labels[label] = address
                continue
            
            # Определение команды и её размера
            parts = line.split()
            if parts:
                mnemonic = parts[0].upper()
                if mnemonic in self.INSTRUCTIONS:
                    address += self.INSTRUCTIONS[mnemonic]['size']
        
        # Второй проход: парсинг команд
        address = 0
        for line_num, line in enumerate(lines, 1):
            line = self._clean_line(line)
            if not line or line.endswith(':'):
                continue
            
            try:
                command = self._parse_line(line, line_num, address)
                commands.append(command)
                address += command.size
            except ValueError as e:
                self.errors.append(f"Строка {line_num}: {e}")
        
        if self.errors:
            error_msg = "\n".join(self.errors)
            raise ValueError(f"Ошибки парсинга:\n{error_msg}")
        
        return commands
    
    def _clean_line(self, line: str) -> str:
        """Очистка строки от комментариев и лишних пробелов"""
        # Удаление комментариев
        if ';' in line:
            line = line[:line.index(';')]
        
        # Удаление лишних пробелов
        line = ' '.join(line.split())
        
        return line.strip()
    
    def _parse_line(self, line: str, line_num: int, address: int) -> Command:
        """Парсинг одной строки"""
        parts = line.split()
        mnemonic = parts[0].upper()
        
        if mnemonic not in self.INSTRUCTIONS:
            raise ValueError(f"Неизвестная инструкция: {mnemonic}")
        
        info = self.INSTRUCTIONS[mnemonic]
        args_count = info['args_count']
        
        # Проверка количества аргументов
        if len(parts) - 1 != args_count:
            raise ValueError(
                f"Инструкция {mnemonic} требует {args_count} аргумент(ов), "
                f"получено {len(parts) - 1}"
            )
        
        # Парсинг аргументов
        args: List[int] = []
        for i, arg_str in enumerate(parts[1:], 1):
            try:
                arg = self._parse_argument(arg_str)
                args.append(arg)
            except ValueError:
                raise ValueError(f"Неверный аргумент {i}: {arg_str}")
        
        # Проверка диапазонов
        self._validate_args(mnemonic, args)
        
        return Command(
            opcode=info['opcode'],
            mnemonic=mnemonic,
            args=args,
            size=info['size'],
            line_num=line_num,
            source=line
        )
    
    def _parse_argument(self, arg_str: str) -> int:
        """Парсинг аргумента"""
        arg_str = arg_str.strip().upper()
        
        # Проверка на метку
        if arg_str in self.labels:
            return self.labels[arg_str]
        
        # Разные системы счисления
        if arg_str.startswith('0X'):
            return int(arg_str[2:], 16)
        elif arg_str.startswith('0B'):
            return int(arg_str[2:], 2)
        elif arg_str.startswith('0'):
            return int(arg_str, 8)
        else:
            return int(arg_str)
    
    def _validate_args(self, mnemonic: str, args: List[int]):
        """Проверка диапазонов аргументов"""
        if mnemonic == 'LOAD':
            if args[0] < 0 or args[0] >= (1 << 31):
                raise ValueError(f"Константа вне диапазона: 0..{2**31-1}")
        
        elif mnemonic == 'READ':
            if args[0] < 0 or args[0] >= (1 << 8):
                raise ValueError(f"Смещение вне диапазона: 0..255")
        
        elif mnemonic in ['STORE', 'BITREV']:
            if args[0] < 0 or args[0] >= (1 << 20):
                raise ValueError(f"Адрес вне диапазона: 0..{2**20-1}")
