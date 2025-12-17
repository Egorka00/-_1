#!/usr/bin/env python3
"""
Ассемблер УВМ - ЭТАП 1: Перевод программы в промежуточное представление

Требования Этапа 1:
1. CLI: путь к исходному файлу, режим тестирования
2. Язык ассемблера: LOAD, READ, WRITE, BITREVERSE
3. Документация в README.md
4. Транслятор в промежуточное представление
5. В тестовом режиме вывод в формате полей и значений
6. Тестовая программа по спецификации
7. Сохранение в репозиторий
"""

import sys
import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Dict

# ============================================================================
# КОНСТАНТЫ ИЗ СПЕЦИФИКАЦИИ
# ============================================================================

class CommandType(Enum):
    """Типы команд УВМ"""
    LOAD = "LOAD"
    READ = "READ"
    WRITE = "WRITE"
    BITREVERSE = "BITREVERSE"

# Коды операций (поле A)
OP_CODES = {
    CommandType.LOAD: 6,        # 110 в битах
    CommandType.READ: 3,        # 011 в битах
    CommandType.WRITE: 2,       # 010 в битах
    CommandType.BITREVERSE: 1,  # 001 в битах
}

# Размеры команд в байтах
COMMAND_SIZES = {
    CommandType.LOAD: 5,
    CommandType.READ: 2,
    CommandType.WRITE: 3,
    CommandType.BITREVERSE: 3,
}

# Диапазоны значений для полей B
B_FIELD_RANGES = {
    CommandType.LOAD: (0, (1 << 31) - 1),      # 31 бит: 0..2147483647
    CommandType.READ: (0, (1 << 8) - 1),       # 8 бит: 0..255
    CommandType.WRITE: (0, (1 << 20) - 1),     # 20 бит: 0..1048575
    CommandType.BITREVERSE: (0, (1 << 20) - 1), # 20 бит: 0..1048575
}

# Описания полей B
B_FIELD_NAMES = {
    CommandType.LOAD: "Константа",
    CommandType.READ: "Смещение",
    CommandType.WRITE: "Адрес",
    CommandType.BITREVERSE: "Адрес",
}

# ============================================================================
# ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ
# ============================================================================

@dataclass
class IntermediateInstruction:
    """Промежуточное представление команды УВМ"""
    line_number: int            # Номер строки в исходном файле
    command_type: CommandType   # Тип команды
    operand: int                # Значение поля B
    source_line: str            # Исходная строка кода
    address: int = 0            # Адрес в памяти (вычисляется)
    
    def __str__(self) -> str:
        return f"Line {self.line_number}: {self.command_type.value} {self.operand}"
    
    def get_field_description(self) -> Dict[str, any]:
        """Получить описание полей команды"""
        return {
            "command": self.command_type.value,
            "a_value": OP_CODES[self.command_type],
            "a_bits": "0-2",
            "b_name": B_FIELD_NAMES[self.command_type],
            "b_value": self.operand,
            "b_range": B_FIELD_RANGES[self.command_type],
        }

# ============================================================================
# КЛАСС АССЕМБЛЕРА ДЛЯ ЭТАПА 1
# ============================================================================

class UVMAssemblerStage1:
    """Ассемблер для Этапа 1 - только промежуточное представление"""
    
    def __init__(self):
        self.instructions: List[IntermediateInstruction] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.current_address = 0
        self.program_size = 0
        
    def parse_line(self, line: str, line_num: int) -> Optional[IntermediateInstruction]:
        """Парсинг строки ассемблера"""
        original_line = line.rstrip()
        line = original_line.strip()
        
        # Пропускаем пустые строки
        if not line:
            return None
        
        # Пропускаем комментарии
        if line.startswith(';'):
            return None
        
        # Удаляем комментарии в конце строки
        if ';' in line:
            line = line.split(';')[0].strip()
            if not line:
                return None
        
        # Разделяем на команду и операнд
        parts = line.split()
        if len(parts) < 2:
            self.errors.append(f"Строка {line_num}: Неполная команда '{original_line}'")
            return None
        
        mnemonic = parts[0].upper()
        operand_str = ' '.join(parts[1:])  # На случай если операнд содержит пробелы
        
        # Определяем тип команды
        try:
            command_type = CommandType(mnemonic)
        except ValueError:
            self.errors.append(f"Строка {line_num}: Неизвестная команда '{mnemonic}'")
            return None
        
        # Парсим операнд
        try:
            operand = self.parse_operand(operand_str)
        except ValueError as e:
            self.errors.append(f"Строка {line_num}: Неверный операнд '{operand_str}' - {e}")
            return None
        
        # Создаем промежуточное представление
        instr = IntermediateInstruction(
            line_number=line_num,
            command_type=command_type,
            operand=operand,
            source_line=original_line,
            address=self.current_address
        )
        
        # Обновляем адрес для следующей команды
        self.current_address += COMMAND_SIZES[command_type]
        
        return instr
    
    def parse_operand(self, operand_str: str) -> int:
        """Парсинг операнда с поддержкой разных систем счисления"""
        operand_str = operand_str.strip().upper()
        
        # Определяем систему счисления
        if operand_str.startswith('0X'):      # Шестнадцатеричная
            return int(operand_str[2:], 16)
        elif operand_str.startswith('0B'):    # Двоичная
            return int(operand_str[2:], 2)
        elif operand_str.startswith('0O'):    # Восьмеричная
            return int(operand_str[2:], 8)
        elif operand_str.startswith('0') and len(operand_str) > 1:  # Восьмеричная
            try:
                return int(operand_str, 8)
            except ValueError:
                return int(operand_str)  # Пробуем как десятичное
        elif operand_str.startswith('-'):     # Отрицательное
            return int(operand_str)
        else:                                 # Десятичное
            return int(operand_str)
    
    def validate_instruction(self, instr: IntermediateInstruction) -> bool:
        """Валидация инструкции"""
        cmd_type = instr.command_type
        operand = instr.operand
        min_val, max_val = B_FIELD_RANGES[cmd_type]
        
        if operand < min_val or operand > max_val:
            b_name = B_FIELD_NAMES[cmd_type]
            self.errors.append(f"Строка {instr.line_number}: "
                             f"{b_name} {operand} вне диапазона "
                             f"({min_val}-{max_val})")
            return False
        
        return True
    
    def assemble(self, source_code: str) -> bool:
        """Ассемблирование исходного кода в промежуточное представление"""
        # Сбрасываем состояние
        self.instructions = []
        self.errors = []
        self.warnings = []
        self.current_address = 0
        
        # Парсим каждую строку
        lines = source_code.split('\n')
        
        for i, line in enumerate(lines, 1):
            instr = self.parse_line(line, i)
            if instr:
                if self.validate_instruction(instr):
                    self.instructions.append(instr)
        
        # Вычисляем общий размер
        self.program_size = self.current_address
        
        return len(self.errors) == 0
    
    def assemble_file(self, filename: str) -> bool:
        """Ассемблирование из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            print(f"📋 Ассемблирование файла: {filename}")
            return self.assemble(source_code)
            
        except FileNotFoundError:
            print(f"❌ Ошибка: файл '{filename}' не найден", file=sys.stderr)
            return False
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}", file=sys.stderr)
            return False
    
    def print_intermediate_representation(self):
        """Вывод промежуточного представления (требование 5)"""
        if not self.instructions:
            print("⚠  Программа не содержит команд")
            return
        
        print("\n" + "=" * 70)
        print("ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ПРОГРАММЫ")
        print("=" * 70)
        
        for i, instr in enumerate(self.instructions):
            print(f"\n📍 Команда #{i+1} (строка {instr.line_number}):")
            print(f"   Исходная строка: {instr.source_line}")
            print(f"   Адрес в памяти: 0x{instr.address:04X} ({instr.address} байт)")
            
            a_value = OP_CODES[instr.command_type]
            b_name = B_FIELD_NAMES[instr.command_type]
            min_val, max_val = B_FIELD_RANGES[instr.command_type]
            size = COMMAND_SIZES[instr.command_type]
            
            print(f"   Тип команды: {instr.command_type.value}")
            print(f"   Поле A (биты 0-2): {a_value} (двоичное: {a_value:03b})")
            print(f"   Поле B ({b_name}): {instr.operand}")
            print(f"     Десятичное: {instr.operand}")
            print(f"     Шестнадцатеричное: 0x{instr.operand:X}")
            print(f"     Двоичное: 0b{instr.operand:b}")
            print(f"   Диапазон поля B: {min_val}..{max_val}")
            print(f"   Размер команды: {size} байт")
            
            if i < len(self.instructions) - 1:
                print("   " + "-" * 50)
    
    def print_test_format(self):
        """Вывод в формате тестов из спецификации"""
        print("\n" + "=" * 60)
        print("ФОРМАТ ПОЛЕЙ И ЗНАЧЕНИЙ (как в спецификации)")
        print("=" * 60)
        
        if not self.instructions:
            print("Нет команд для вывода")
            return
        
        for instr in self.instructions:
            a_value = OP_CODES[instr.command_type]
            b_name = B_FIELD_NAMES[instr.command_type]
            
            print(f"\n{instr.command_type.value} {instr.operand}:")
            print(f"  A = {a_value} (биты 0-2)")
            print(f"  {b_name} = {instr.operand}")
            
            # Определяем битовый диапазон для B
            if instr.command_type == CommandType.LOAD:
                b_bits = 31
                b_range = "биты 3-33"
            elif instr.command_type == CommandType.READ:
                b_bits = 8
                b_range = "биты 3-10"
            else:  # WRITE или BITREVERSE
                b_bits = 20
                b_range = "биты 3-22"
            
            print(f"  {b_range} = {instr.operand:0{b_bits}b}")
    
    def print_summary(self):
        """Вывод сводной информации"""
        print("\n" + "=" * 60)
        print("СВОДКА АССЕМБЛИРОВАНИЯ (ЭТАП 1)")
        print("=" * 60)
        
        print(f"📊 Всего команд: {len(self.instructions)}")
        print(f"💾 Размер программы: {self.program_size} байт")
        
        if self.instructions:
            # Статистика по командам
            stats = {}
            for instr in self.instructions:
                cmd = instr.command_type.value
                stats[cmd] = stats.get(cmd, 0) + 1
            
            print("\n📈 Распределение команд:")
            for cmd, count in sorted(stats.items()):
                print(f"  {cmd:12}: {count:3d}")
        
        if self.errors:
            print(f"\n❌ Ошибки ({len(self.errors)}):")
            for error in self.errors[:5]:  # Показываем первые 5
                print(f"  • {error}")
            if len(self.errors) > 5:
                print(f"  ... и еще {len(self.errors) - 5} ошибок")
        else:
            print("\n✅ Ошибок не обнаружено")
        
        if self.warnings:
            print(f"\n⚠  Предупреждения ({len(self.warnings)}):")
            for warning in self.warnings[:3]:
                print(f"  • {warning}")
            if len(self.warnings) > 3:
                print(f"  ... и еще {len(self.warnings) - 3} предупреждений")
        
        print("=" * 60)

# ============================================================================
# УТИЛИТЫ
# ============================================================================

def create_test_program() -> str:
    """Создание тестовой программы по спецификации (требование 6)"""
    test_source = """LOAD 63
READ 102
WRITE 120
BITREVERSE 88"""
    
    filename = "test_program.asm"
    
    with open(filename, 'w') as f:
        f.write(test_source)
    
    print(f"✅ Создан тестовый файл: {filename}")
    print("\n📝 Содержимое файла:")
    print("-" * 30)
    print(test_source)
    print("-" * 30)
    
    return test_source

def verify_test_sequences():
    """Проверка тестовых последовательностей из спецификации"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ТЕСТОВЫХ ПОСЛЕДОВАТЕЛЬНОСТЕЙ")
    print("=" * 60)
    
    assembler = UVMAssemblerStage1()
    
    # Тестовые данные из спецификации
    test_cases = [
        ("LOAD", 63, 6, "Константа", 31),
        ("READ", 102, 3, "Смещение", 8),
        ("WRITE", 120, 2, "Адрес", 20),
        ("BITREVERSE", 88, 1, "Адрес", 20),
    ]
    
    print("\nТесты из спецификации УВМ:")
    print("-" * 50)
    
    for mnemonic, operand, expected_a, b_name, b_bits in test_cases:
        print(f"\n{mnemonic} {operand}:")
        print(f"  Поле A (ожидается): {expected_a} (биты 0-2)")
        print(f"  Поле B ({b_name}): {operand}")
        print(f"  Диапазон B: {b_bits} бит")
        
        # Проверяем диапазон
        if mnemonic == "LOAD" and (0 <= operand <= (1 << 31) - 1):
            print(f"  ✅ Константа в допустимом диапазоне")
        elif mnemonic == "READ" and (0 <= operand <= 255):
            print(f"  ✅ Смещение в допустимом диапазоне")
        elif mnemonic in ["WRITE", "BITREVERSE"] and (0 <= operand <= (1 << 20) - 1):
            print(f"  ✅ Адрес в допустимом диапазоне")
        else:
            print(f"  ❌ Значение вне допустимого диапазона")

# ============================================================================
# CLI ИНТЕРФЕЙС
# ============================================================================

def print_usage():
    """Вывод справки"""
    print("Использование:")
    print("  python uvm_assembler_stage1.py <файл.asm>     Ассемблировать программу")
    print("  python uvm_assembler_stage1.py <файл.asm> -t  Ассемблировать с тестовым выводом")
    print("  python uvm_assembler_stage1.py --create-test  Создать тестовую программу")
    print("  python uvm_assembler_stage1.py --test         Проверить тестовые последовательности")
    print("  python uvm_assembler_stage1.py --help         Показать эту справку")
    print("\nПример:")
    print("  python uvm_assembler_stage1.py test_program.asm -t")

def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    # Обработка аргументов
    input_file = None
    test_mode = False
    
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        
        if arg == "-t" or arg == "--test-mode":
            test_mode = True
        elif arg == "--create-test":
            create_test_program()
            print("\nТестовая программа создана. Запуск ассемблирования:")
            print("-" * 50)
            
            assembler = UVMAssemblerStage1()
            if assembler.assemble_file('test_program.asm'):
                assembler.print_intermediate_representation()
                assembler.print_test_format()
                assembler.print_summary()
            return
        elif arg == "--test":
            verify_test_sequences()
            return
        elif arg == "--help" or arg == "-h":
            print_usage()
            return
        elif not arg.startswith("-"):
            input_file = arg
    
    if not input_file:
        print("❌ Ошибка: не указан входной файл")
        print_usage()
        sys.exit(1)
    
    # Проверяем существование файла
    if not os.path.exists(input_file):
        print(f"❌ Ошибка: файл '{input_file}' не найден")
        sys.exit(1)
    
    # Создаем и запускаем ассемблер
    assembler = UVMAssemblerStage1()
    
    if not assembler.assemble_file(input_file):
        print("\n❌ Ассемблирование завершилось с ошибками!")
        sys.exit(1)
    
    print("\n✅ Ассемблирование успешно завершено!")
    
    # Вывод результатов
    if test_mode:
        # Требование 5: вывод в формате полей и значений
        assembler.print_intermediate_representation()
        assembler.print_test_format()
    else:
        assembler.print_summary()

# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    main()
