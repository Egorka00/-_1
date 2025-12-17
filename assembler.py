#!/usr/bin/env python3
"""
Ассемблер для учебной виртуальной машины (Вариант 6)
Этап 1: Перевод программы в промежуточное представление
"""

import argparse
import sys
from pathlib import Path
from parser import Parser
from encoder import Encoder

class Assembler:
    def __init__(self):
        self.parser = Parser()
        self.encoder = Encoder()
        
    def assemble(self, source_file, output_file, test_mode=False):
        """Основная функция ассемблирования"""
        
        # 1. Чтение исходного файла
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 2. Парсинг в промежуточное представление
        intermediate = self.parser.parse(source_code)
        
        # 3. В тестовом режиме выводим промежуточное представление
        if test_mode:
            print("=== ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ===")
            for i, cmd in enumerate(intermediate):
                print(f"Команда {i}: {cmd}")
            print("=" * 40)
        
        # 4. Кодирование в бинарный формат (Этап 2)
        binary_data = self.encoder.encode(intermediate)
        
        # 5. Запись в выходной файл
        with open(output_file, 'wb') as f:
            f.write(binary_data)
        
        # 6. Вывод размера файла
        print(f"Размер двоичного файла: {len(binary_data)} байт")
        
        # 7. В тестовом режиме выводим байты
        if test_mode:
            print("\n=== БАЙТОВОЕ ПРЕДСТАВЛЕНИЕ ===")
            hex_bytes = [f"0x{b:02X}" for b in binary_data]
            print(", ".join(hex_bytes))
        
        return intermediate, binary_data

def main():
    parser = argparse.ArgumentParser(
        description='Ассемблер для УВМ (Вариант 6)'
    )
    parser.add_argument('source', help='Путь к исходному файлу с программой')
    parser.add_argument('output', help='Путь к двоичному файлу-результату')
    parser.add_argument('--test', action='store_true', 
                       help='Режим тестирования')
    
    args = parser.parse_args()
    
    assembler = Assembler()
    try:
        assembler.assemble(args.source, args.output, args.test)
        print("Ассемблирование успешно завершено!")
    except Exception as e:
        print(f"Ошибка ассемблирования: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
