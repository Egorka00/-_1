#!/usr/bin/env python3
"""
Ассемблер для учебной виртуальной машины (Вариант 6)
Этапы 1 и 2: Парсинг и кодирование
"""

import argparse
import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.parser import Parser
    from src.encoder import Encoder
except ImportError:
    # Альтернативный импорт для тестов
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
        
        # 2. Парсинг в промежуточное представление (Этап 1)
        intermediate = self.parser.parse(source_code)
        
        # 3. В тестовом режиме выводим промежуточное представление
        if test_mode:
            print("=" * 60)
            print("ЭТАП 1: ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ")
            print("=" * 60)
            for i, cmd in enumerate(intermediate):
                print(f"Команда {i}: {cmd}")
            print("-" * 60)
        
        # 4. Кодирование в бинарный формат (Этап 2)
        binary_data = self.encoder.encode(intermediate)
        
        # 5. Запись в выходной файл
        with open(output_file, 'wb') as f:
            f.write(binary_data)
        
        # 6. Вывод размера файла
        print(f"Размер двоичного файла: {len(binary_data)} байт")
        
        # 7. В тестовом режиме выводим байты
        if test_mode:
            print("\n" + "=" * 60)
            print("ЭТАП 2: БАЙТОВОЕ ПРЕДСТАВЛЕНИЕ")
            print("=" * 60)
            hex_bytes = [f"0x{b:02X}" for b in binary_data]
            print("Байты: " + ", ".join(hex_bytes))
            print("=" * 60)
        
        return intermediate, binary_data


def main():
    parser = argparse.ArgumentParser(
        description='Ассемблер для УВМ (Вариант 6) - Этапы 1 и 2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python assembler.py program.asm program.bin
  python assembler.py program.asm program.bin --test
  python assembler.py examples/simple.asm output.bin --test
        """
    )
    parser.add_argument('source', help='Путь к исходному файлу с программой')
    parser.add_argument('output', help='Путь к двоичному файлу-результату')
    parser.add_argument('--test', action='store_true', 
                       help='Режим тестирования с выводом промежуточных результатов')
    
    args = parser.parse_args()
    
    # Проверка существования файла
    if not os.path.exists(args.source):
        print(f"Ошибка: файл '{args.source}' не найден")
        sys.exit(1)
    
    assembler = Assembler()
    try:
        print(f"Ассемблирование файла: {args.source}")
        print(f"Выходной файл: {args.output}")
        print(f"Режим тестирования: {'ВКЛ' if args.test else 'ВЫКЛ'}")
        print("-" * 40)
        
        assembler.assemble(args.source, args.output, args.test)
        
        if not args.test:
            print("\n✓ Ассемблирование успешно завершено!")
        else:
            print("\n✓ Тестовый режим завершен успешно!")
            
    except FileNotFoundError as e:
        print(f"Ошибка файла: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка в исходном коде: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
