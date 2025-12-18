#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import sys
from typing import List, Tuple, Dict, Any

class UVMAssembler:
    """Ассемблер для учебной виртуальной машины (УВМ)"""
    
    # Коды операций
    OPCODES = {
        'bitreverse': 1,  # Унарная операция bitreverse()
        'store': 2,       # Запись значения в память
        'load': 3,        # Чтение значения из памяти
        'const': 6        # Загрузка константы
    }
    
    # Размеры команд в байтах
    COMMAND_SIZES = {
        1: 3,  # bitreverse
        2: 3,  # store
        3: 2,  # load
        6: 5   # const
    }
    
    def __init__(self):
        self.symbol_table = {}
        self.current_address = 0
        
    def parse_instruction(self, line: str) -> Tuple[str, List[str]]:
        """Разбор строки ассемблера на мнемонику и аргументы"""
        line = line.strip()
        
        # Пропускаем комментарии и пустые строки
        if not line or line.startswith(';'):
            return None, []
            
        # Удаляем комментарии в конце строки
        if ';' in line:
            line = line.split(';')[0].strip()
            
        # Разделяем мнемонику и аргументы
        parts = line.split()
        if not parts:
            return None, []
            
        mnemonic = parts[0].lower()
        args = []
        
        if len(parts) > 1:
            # Обрабатываем аргументы, разделенные запятыми
            args_str = ' '.join(parts[1:])
            args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
            
        return mnemonic, args
    
    def encode_constant(self, opcode: int, value: int) -> bytes:
        """Кодирование команды загрузки константы (5 байт)"""
        # A (биты 0-2): opcode
        # B (биты 3-33): значение
        if not (0 <= value <= 0x7FFFFFFF):
            raise ValueError(f"Значение константы вне диапазона: {value}")
            
        # Создаем 5-байтовое представление
        # Первый байт: opcode в младших 3 битах
        first_byte = opcode & 0x07
        
        # Добавляем 3 младших бита значения к первому байту
        first_byte |= (value & 0x07) << 3
        value >>= 3
        
        # Остальные 4 байта - оставшиеся биты значения
        encoded = bytearray([first_byte])
        for _ in range(4):
            encoded.append(value & 0xFF)
            value >>= 8
            
        return bytes(encoded)
    
    def encode_load(self, opcode: int, offset: int) -> bytes:
        """Кодирование команды чтения из памяти (2 байта)"""
        # A (биты 0-2): opcode
        # B (биты 3-10): смещение
        if not (0 <= offset <= 0xFF):
            raise ValueError(f"Смещение вне диапазона: {offset}")
            
        first_byte = opcode & 0x07
        first_byte |= (offset & 0x07) << 3
        second_byte = (offset >> 3) & 0xFF
        
        return bytes([first_byte, second_byte])
    
    def encode_store(self, opcode: int, address: int) -> bytes:
        """Кодирование команды записи в память (3 байта)"""
        # A (биты 0-2): opcode
        # B (биты 3-22): адрес
        if not (0 <= address <= 0x3FFFF):
            raise ValueError(f"Адрес вне диапазона: {address}")
            
        first_byte = opcode & 0x07
        first_byte |= (address & 0x07) << 3
        address >>= 3
        
        encoded = bytearray([first_byte])
        encoded.append(address & 0xFF)
        encoded.append((address >> 8) & 0xFF)
        
        return bytes(encoded)
    
    def encode_bitreverse(self, opcode: int, address: int) -> bytes:
        """Кодирование команды bitreverse (3 байта)"""
        # Формат такой же как у store
        return self.encode_store(opcode, address)
    
    def assemble_line(self, mnemonic: str, args: List[str]) -> bytes:
        """Ассемблирование одной команды"""
        if mnemonic not in self.OPCODES:
            raise ValueError(f"Неизвестная мнемоника: {mnemonic}")
            
        opcode = self.OPCODES[mnemonic]
        
        if mnemonic == 'const':
            if len(args) != 1:
                raise ValueError(f"const требует 1 аргумент, получено {len(args)}")
            value = self.parse_number(args[0])
            return self.encode_constant(opcode, value)
            
        elif mnemonic == 'load':
            if len(args) != 1:
                raise ValueError(f"load требует 1 аргумент, получено {len(args)}")
            offset = self.parse_number(args[0])
            return self.encode_load(opcode, offset)
            
        elif mnemonic == 'store':
            if len(args) != 1:
                raise ValueError(f"store требует 1 аргумент, получено {len(args)}")
            address = self.parse_number(args[0])
            return self.encode_store(opcode, address)
            
        elif mnemonic == 'bitreverse':
            if len(args) != 1:
                raise ValueError(f"bitreverse требует 1 аргумент, получено {len(args)}")
            address = self.parse_number(args[0])
            return self.encode_bitreverse(opcode, address)
    
    def parse_number(self, num_str: str) -> int:
        """Парсинг числового значения из строки"""
        num_str = num_str.strip().lower()
        
        if num_str.startswith('0x'):
            return int(num_str[2:], 16)
        elif num_str.startswith('0b'):
            return int(num_str[2:], 2)
        elif num_str.startswith('0o'):
            return int(num_str[2:], 8)
        else:
            return int(num_str)
    
    def assemble(self, source_code: str) -> List[Dict[str, Any]]:
        """Ассемблирование всей программы"""
        lines = source_code.split('\n')
        intermediate_repr = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            try:
                mnemonic, args = self.parse_instruction(line)
                if mnemonic is None:
                    continue
                    
                # Кодируем команду
                binary = self.assemble_line(mnemonic, args)
                
                # Создаем промежуточное представление
                ir_entry = {
                    'line': line_num,
                    'mnemonic': mnemonic,
                    'args': args,
                    'binary': binary,
                    'opcode': self.OPCODES[mnemonic],
                    'size': len(binary)
                }
                
                # Добавляем информацию о полях
                if mnemonic == 'const':
                    ir_entry['fields'] = {
                        'A': self.OPCODES[mnemonic],
                        'B': self.parse_number(args[0])
                    }
                elif mnemonic == 'load':
                    ir_entry['fields'] = {
                        'A': self.OPCODES[mnemonic],
                        'B': self.parse_number(args[0])
                    }
                elif mnemonic == 'store':
                    ir_entry['fields'] = {
                        'A': self.OPCODES[mnemonic],
                        'B': self.parse_number(args[0])
                    }
                elif mnemonic == 'bitreverse':
                    ir_entry['fields'] = {
                        'A': self.OPCODES[mnemonic],
                        'B': self.parse_number(args[0])
                    }
                    
                intermediate_repr.append(ir_entry)
                
            except Exception as e:
                raise ValueError(f"Ошибка на строке {line_num}: {str(e)}")
                
        return intermediate_repr
    
    def save_binary(self, intermediate_repr: List[Dict[str, Any]], output_file: str):
        """Сохранение бинарного файла"""
        with open(output_file, 'wb') as f:
            for entry in intermediate_repr:
                f.write(entry['binary'])
    
    def display_intermediate(self, intermediate_repr: List[Dict[str, Any]]):
        """Отображение промежуточного представления"""
        print("Промежуточное представление программы:")
        print("-" * 60)
        
        for entry in intermediate_repr:
            print(f"Строка {entry['line']}: {entry['mnemonic']} {', '.join(entry['args'])}")
            print(f"  Код операции (A): {entry['opcode']}")
            
            if 'fields' in entry:
                for field, value in entry['fields'].items():
                    if field == 'B':
                        print(f"  Поле {field}: {value} (0x{value:X})")
                    else:
                        print(f"  Поле {field}: {value}")
            
            print(f"  Бинарное представление: {entry['binary'].hex()}")
            
            # Отображаем байты как в тестах спецификации
            bytes_list = list(entry['binary'])
            formatted_bytes = ', '.join(f'0x{b:02X}' for b in bytes_list)
            print(f"  Байты: [{formatted_bytes}]")
            print()
