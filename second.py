#!/usr/bin/env python3
"""
Ассемблер УВМ - Этап 2: Формирование машинного кода
"""

import argparse
import struct
import sys
import os
from typing import List, Tuple, Optional

# ============================================================================
# КОНСТАНТЫ СПЕЦИФИКАЦИИ УВМ
# ============================================================================

# Коды операций (поле A, биты 0-2)
OP_LOAD = 6        # 110 - Загрузка константы
OP_READ = 3        # 011 - Чтение из памяти
OP_WRITE = 2       # 010 - Запись в память
OP_BITREVERSE = 1  # 001 - Реверс битов

# Размеры команд в байтах
CMD_SIZE_LOAD = 5
CMD_SIZE_READ = 2
CMD_SIZE_WRITE = 3
CMD_SIZE_BITREVERSE = 3

# Максимальные значения полей
MAX_LOAD = (1 << 31) - 1      # 31 бит: 0..2147483647
MAX_READ = (1 << 8) - 1       # 8 бит: 0..255
MAX_WRITE = (1 << 20) - 1     # 20 бит: 0..1048575
MAX_BITREVERSE = (1 << 20) - 1 # 20 бит: 0..1048575

# ============================================================================
# КЛАСС АССЕМБЛЕРА
# ============================================================================

class UVMAssembler:
    """Ассемблер УВМ для Этапа 2"""
    
    def __init__(self):
        self.commands: List[Tuple[str, int]] = []  # (команда, операнд)
        self.binary_data = bytearray()
        self.errors: List[str] = []
        self.test_mode = False
    
    def parse_operand(self, operand_str: str) -> int:
        """Парсинг операнда с поддержкой разных систем счисления"""
        operand_str = operand_str.strip().upper()
        
        try:
            if operand_str.startswith('0X'):      # Hex
                return int(operand_str[2:], 16)
            elif operand_str.startswith('0B'):    # Binary
                return int(operand_str[2:], 2)
            elif operand_str.startswith('0O'):    # Octal
                return int(operand_str[2:], 8)
            elif operand_str.startswith('0') and len(operand_str) > 1:  # Octal
                try:
                    return int(operand_str, 8)
                except ValueError:
                    return int(operand_str)
            else:                                 # Decimal
                return int(operand_str)
        except ValueError:
            raise ValueError(f"Неверный формат числа: '{operand_str}'")
    
    def validate_command(self, command: str, operand: int) -> bool:
        """Валидация команды"""
        if command == "LOAD":
            if operand < 0 or operand > MAX_LOAD:
                self.errors.append(f"Константа {operand} вне диапазона 31 бит (0-{MAX_LOAD})")
                return False
        elif command == "READ":
            if operand < 0 or operand > MAX_READ:
                self.errors.append(f"Смещение {operand} вне диапазона 8 бит (0-255)")
                return False
        elif command == "WRITE":
            if operand < 0 or operand > MAX_WRITE:
                self.errors.append(f"Адрес {operand} вне диапазона 20 бит (0-{MAX_WRITE})")
                return False
        elif command == "BITREVERSE":
            if operand < 0 or operand > MAX_BITREVERSE:
                self.errors.append(f"Адрес {operand} вне диапазона 20 бит (0-{MAX_BITREVERSE})")
                return False
        return True
    
    def parse_line(self, line: str, line_num: int) -> Optional[Tuple[str, int]]:
        """Парсинг строки ассемблера"""
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith(';'):
            return None
        
        # Удаляем комментарии
        if ';' in line:
            line = line.split(';')[0].strip()
            if not line:
                return None
        
        parts = line.split()
        if len(parts) < 2:
            self.errors.append(f"Строка {line_num}: Неполная команда '{line}'")
            return None
        
        command = parts[0].upper()
        operand_str = parts[1]
        
        # Проверяем команду
        valid_commands = {"LOAD", "READ", "WRITE", "BITREVERSE"}
        if command not in valid_commands:
            self.errors.append(f"Строка {line_num}: Неизвестная команда '{command}'")
            return None
        
        # Парсим операнд
        try:
            operand = self.parse_operand(operand_str)
        except ValueError as e:
            self.errors.append(f"Строка {line_num}: {e}")
            return None
        
        # Валидация
        if not self.validate_command(command, operand):
            return None
        
        return (command, operand)
    
    def encode_load(self, operand: int) -> bytes:
        """Кодирование команды LOAD (5 байт)"""
        # Формат: биты 0-2: A=6, биты 3-33: B (31 бит)
        value = (operand << 3) | OP_LOAD
        return struct.pack('<Q', value)[:5]  # 5 байт
    
    def encode_read(self, operand: int) -> bytes:
        """Кодирование команды READ (2 байта)"""
        # Формат: биты 0-2: A=3, биты 3-10: B (8 бит)
        value = (operand << 3) | OP_READ
        return struct.pack('<H', value)  # 2 байта
    
    def encode_write(self, operand: int) -> bytes:
        """Кодирование команды WRITE (3 байта)"""
        # Формат: биты 0-2: A=2, биты 3-22: B (20 бит)
        value = (operand << 3) | OP_WRITE
        return struct.pack('<I', value)[:3]  # 3 байта
    
    def encode_bitreverse(self, operand: int) -> bytes:
        """Кодирование команды BITREVERSE (3 байта)"""
        # Формат: биты 0-2: A=1, биты 3-22: B (20 бит)
        value = (operand << 3) | OP_BITREVERSE
        return struct.pack('<I', value)[:3]  # 3 байта
    
    def encode_instruction(self, command: str, operand: int) -> bytes:
        """Кодирование инструкции в машинный код"""
        if command == "LOAD":
            return self.encode_load(operand)
        elif command == "READ":
            return self.encode_read(operand)
        elif command == "WRITE":
            return self.encode_write(operand)
        elif command == "BITREVERSE":
            return self.encode_bitreverse(operand)
        else:
            raise ValueError(f"Неизвестная команда: {command}")
    
    def assemble(self, source_code: str) -> bool:
        """Ассемблирование исходного кода"""
        self.commands = []
        self.binary_data = bytearray()
        self.errors = []
        
        lines = source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            instruction = self.parse_line(line, line_num)
            if instruction:
                command, operand = instruction
                self.commands.append((command, operand))
                
                # Кодируем в машинный код
                machine_code = self.encode_instruction(command, operand)
                self.binary_data.extend(machine_code)
                
                # Вывод в тестовом режиме
                if self.test_mode:
                    hex_bytes = ', '.join(f'0x{b:02X}' for b in machine_code)
                    print(f"Строка {line_num}: {command} {operand} -> {hex_bytes}")
        
        return len(self.errors) == 0
    
    def assemble_file(self, input_file: str) -> bool:
        """Ассемблирование из файла"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            print(f"Ассемблирование файла: {input_file}")
            return self.assemble(source_code)
            
        except FileNotFoundError:
            print(f"Ошибка: файл '{input_file}' не найден", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Ошибка чтения файла: {e}", file=sys.stderr)
            return False
    
    def save_binary(self, output_file: str) -> bool:
        """Сохранение машинного кода в файл"""
        try:
            with open(output_file, 'wb') as f:
                f.write(self.binary_data)
            
            print(f"Создан двоичный файл: {output_file}")
            return True
            
        except Exception as e:
            print(f"Ошибка записи файла: {e}", file=sys.stderr)
            return False
    
    def print_summary(self):
        """Вывод сводки ассемблирования"""
        print("\n" + "=" * 60)
        print("СВОДКА АССЕМБЛИРОВАНИЯ")
        print("=" * 60)
        
        # Требование 3: Число ассемблированных команд
        print(f"✅ Число ассемблированных команд: {len(self.commands)}")
        print(f"📊 Размер машинного кода: {len(self.binary_data)} байт")
        
        if self.commands:
            # Статистика
            stats = {}
            for cmd, _ in self.commands:
                stats[cmd] = stats.get(cmd, 0) + 1
            
            print("\n📈 Распределение команд:")
            for cmd, count in sorted(stats.items()):
                print(f"  {cmd:12}: {count:3d} команд")
        
        if self.errors:
            print(f"\n❌ Ошибки ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print("\n✅ Ошибок не обнаружено")
        
        print("=" * 60)
    
    def print_test_output(self):
        """Вывод в тестовом формате (требование 4)"""
        if not self.commands:
            print("Нет команд для вывода")
            return
        
        print("\n" + "=" * 60)
        print("ТЕСТОВЫЙ ВЫВОД (байтовый формат)")
        print("=" * 60)
        
        for command, operand in self.commands:
            machine_code = self.encode_instruction(command, operand)
            hex_bytes = ', '.join(f'0x{b:02X}' for b in machine_code)
            print(f"{command} {operand}:")
            print(f"  {hex_bytes}")

# ============================================================================
# ФУНКЦИИ ДЛЯ ТЕСТИРОВАНИЯ
# ============================================================================

def create_test_program():
    """Создание тестовой программы по спецификации (требование 5)"""
    test_source = """LOAD 63
READ 102
WRITE 120
BITREVERSE 88"""
    
    filename = "test_spec.asm"
    
    with open(filename, 'w') as f:
        f.write(test_source)
    
    print(f"✅ Создан тестовый файл: {filename}")
    print("\n📝 Содержимое файла:")
    print("-" * 30)
    print(test_source)
    print("-" * 30)
    
    return test_source

def verify_test_sequences():
    """Проверка соответствия тестовым последовательностям"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ТЕСТОВЫХ ПОСЛЕДОВАТЕЛЬНОСТЕЙ")
    print("=" * 60)
    
    assembler = UVMAssembler()
    
    # Тестовые данные из спецификации
    test_cases = [
        ("LOAD", 63, [0xFE, 0x01, 0x00, 0x00, 0x00]),
        ("READ", 102, [0x33, 0x03]),
        ("WRITE", 120, [0xC2, 0x03, 0x00]),
        ("BITREVERSE", 88, [0xC1, 0x02, 0x00]),
    ]
    
    all_correct = True
    
    for command, operand, expected_bytes in test_cases:
        actual_bytes = list(assembler.encode_instruction(command, operand))
        
        print(f"\n{command} {operand}:")
        print(f"  Ожидается: {', '.join(f'0x{b:02X}' for b in expected_bytes)}")
        print(f"  Получено:  {', '.join(f'0x{b:02X}' for b in actual_bytes)}")
        
        if actual_bytes == expected_bytes:
            print("  ✅ СООТВЕТСТВУЕТ СПЕЦИФИКАЦИИ")
        else:
            print("  ❌ НЕ СООТВЕТСТВУЕТ СПЕЦИФИКАЦИИ")
            all_correct = False
    
    if all_correct:
        print("\n🎉 ВСЕ ТЕСТОВЫЕ ПОСЛЕДОВАТЕЛЬНОСТИ КОРРЕКТНЫ!")
    else:
        print("\n⚠  ОБНАРУЖЕНЫ РАСХОЖДЕНИЯ СО СПЕЦИФИКАЦИЕЙ")
    
    return all_correct

# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ С ПРОСТЫМ CLI
# ============================================================================

def main():
    """Главная функция с простым интерфейсом"""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python uvm_assembler.py <команда> [аргументы]")
        print("\nКоманды:")
        print("  assemble <input.asm> <output.bin>   Ассемблировать программу")
        print("  assemble -t <input.asm> <output.bin> Ассемблировать с тестовым выводом")
        print("  create-test                         Создать тестовую программу")
        print("  test                                Проверить тестовые последовательности")
        print("  demo                                Демонстрация полного процесса")
        print("\nПримеры:")
        print("  python uvm_assembler.py assemble program.asm output.bin")
        print("  python uvm_assembler.py create-test")
        return
    
    command = sys.argv[1]
    
    if command == "create-test":
        # Создание тестовой программы
        create_test_program()
        
    elif command == "test":
        # Проверка тестовых последовательностей
        verify_test_sequences()
        
    elif command == "demo":
        # Демонстрация полного процесса
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ ПОЛНОГО ПРОЦЕССА АССЕМБЛИРОВАНИЯ")
        print("=" * 60)
        
        # Создаем тестовую программу
        source = create_test_program()
        
        # Создаем ассемблер
        assembler = UVMAssembler()
        assembler.test_mode = True
        
        # Ассемблируем
        print(f"\n🔧 Ассемблирование тестовой программы:")
        print("-" * 40)
        
        if not assembler.assemble(source):
            print("❌ Ошибка ассемблирования")
            return
        
        # Сохраняем в файл
        output_file = "output.bin"
        assembler.save_binary(output_file)
        
        # Выводим результаты
        assembler.print_summary()
        assembler.print_test_output()
        
        # Проверяем тестовые последовательности
        verify_test_sequences()
        
        # Показываем созданные файлы
        print("\n📁 СОЗДАННЫЕ ФАЙЛЫ:")
        print("-" * 40)
        for file in ["test_spec.asm", output_file]:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"  {file:20} - {size:6} байт")
    
    elif command == "assemble":
        # Ассемблирование программы
        if len(sys.argv) < 4:
            print("Ошибка: для команды assemble нужны входной и выходной файлы")
            print("Использование: python uvm_assembler.py assemble <input.asm> <output.bin>")
            print("Или с тестовым выводом: python uvm_assembler.py assemble -t <input.asm> <output.bin>")
            return
        
        # Проверяем наличие флага -t
        test_mode = False
        input_file = ""
        output_file = ""
        
        if sys.argv[2] == "-t":
            test_mode = True
            if len(sys.argv) < 5:
                print("Ошибка: недостаточно аргументов")
                return
            input_file = sys.argv[3]
            output_file = sys.argv[4]
        else:
            input_file = sys.argv[2]
            output_file = sys.argv[3]
        
        # Проверяем файлы
        if not os.path.exists(input_file):
            print(f"Ошибка: файл '{input_file}' не найден")
            return
        
        # Создаем и настраиваем ассемблер
        assembler = UVMAssembler()
        assembler.test_mode = test_mode
        
        # Ассемблируем
        if not assembler.assemble_file(input_file):
            print("\n❌ Ассемблирование завершилось с ошибками!")
            return
        
        # Сохраняем машинный код
        if not assembler.save_binary(output_file):
            return
        
        # Выводим сводку
        assembler.print_summary()
        
        # Дополнительный вывод в тестовом режиме
        if test_mode:
            assembler.print_test_output()
        
        print(f"\n✅ Ассемблирование успешно завершено!")
        
    else:
        print(f"Неизвестная команда: {command}")
        print("Используйте: python uvm_assembler.py для справки")

# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    main()
