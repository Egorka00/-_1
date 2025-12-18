#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
from assembler import UVMAssembler

def main():
    parser = argparse.ArgumentParser(description='Ассемблер Учебной Виртуальной Машины (УВМ)')
    parser.add_argument('input_file', help='Путь к исходному файлу с текстом программы')
    parser.add_argument('output_file', help='Путь к двоичному файлу-результату')
    parser.add_argument('-t', '--test', action='store_true', 
                       help='Режим тестирования (вывод промежуточного представления)')
    
    args = parser.parse_args()
    
    try:
        # Чтение исходного файла
        with open(args.input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Ассемблирование
        assembler = UVMAssembler()
        intermediate_repr = assembler.assemble(source_code)
        
        # Сохранение бинарного файла
        assembler.save_binary(intermediate_repr, args.output_file)
        
        # Вывод промежуточного представления в режиме тестирования
        if args.test:
            assembler.display_intermediate(intermediate_repr)
            print(f"\nПрограмма успешно ассемблирована!")
            print(f"Исходный файл: {args.input_file}")
            print(f"Выходной файл: {args.output_file}")
            print(f"Размер программы: {sum(entry['size'] for entry in intermediate_repr)} байт")
        
    except FileNotFoundError:
        print(f"Ошибка: Файл {args.input_file} не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка ассемблирования: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
