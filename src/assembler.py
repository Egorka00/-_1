#!/usr/bin/env python3
"""
Ассемблер для учебной виртуальной машины (Вариант 6)
Этапы 1 и 2
"""

import argparse
import sys
from pathlib import Path
from .parser import Parser
from .encoder import Encoder


class Assembler:
    """Основной класс ассемблера"""
    
    def __init__(self):
        self.parser = Parser()
        self.encoder = Encoder()
    
    def assemble(self, source_path: Path, output_path: Path, test_mode: bool = False):
        """
        Ассемблирование исходного кода
        
        Args:
            source_path: путь к исходному файлу
            output_path: путь к выходному бинарному файлу
            test_mode: режим тестирования с дополнительным выводом
        """
        # Чтение исходного кода
        source_code = source_path.read_text(encoding='utf-8')
        
        # Парсинг (Этап 1)
        intermediate = self.parser.parse(source_code)
        
        # Вывод промежуточного представления в тестовом режиме
        if test_mode:
            print("=== ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ===")
            for i, cmd in enumerate(intermediate):
                print(f"{i:3d}: {cmd}")
            print()
        
        # Кодирование (Этап 2)
        binary_data = self.encoder.encode(intermediate)
        
        # Сохранение результата
        output_path.write_bytes(binary_data)
        
        # Вывод информации
        print(f"Размер двоичного файла: {len(binary_data)} байт")
        
        if test_mode:
            print("\n=== БАЙТОВОЕ ПРЕДСТАВЛЕНИЕ ===")
            hex_bytes = [f"0x{b:02X}" for b in binary_data]
            print(", ".join(hex_bytes))
        
        return intermediate, binary_data


def main():
    """Точка входа CLI"""
    parser = argparse.ArgumentParser(
        description='Ассемблер для УВМ (Вариант 6)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'source',
        type=Path,
        help='Путь к исходному файлу с программой'
    )
    
    parser.add_argument(
        'output',
        type=Path,
        help='Путь к двоичному файлу-результату'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Режим тестирования'
    )
    
    args = parser.parse_args()
    
    # Проверка файлов
    if not args.source.exists():
        print(f"Ошибка: файл {args.source} не найден")
        sys.exit(1)
    
    # Создание ассемблера и выполнение
    assembler = Assembler()
    
    try:
        print(f"Ассемблирование: {args.source} -> {args.output}")
        if args.test:
            print("Режим: ТЕСТИРОВАНИЕ")
        print("-" * 50)
        
        assembler.assemble(args.source, args.output, args.test)
        
        print("\n✅ Ассемблирование завершено успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка ассемблирования: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
