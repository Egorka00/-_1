#!/usr/bin/env python3
import argparse
import sys
import os
from parser import parser
from compiler import XMLCompiler

def main():
    # Настройка аргументов командной строки
    arg_parser = argparse.ArgumentParser(
        description='Конвертер учебного конфигурационного языка в XML (Вариант 6)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python cli.py -i config.conf
  python cli.py --input example.conf
        """
    )
    
    arg_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Путь к входному файлу с конфигурацией'
    )
    
    arg_parser.add_argument(
        '-o', '--output',
        help='Путь к выходному файлу (если не указан - вывод на экран)'
    )
    
    # Парсим аргументы
    args = arg_parser.parse_args()
    
    # Проверяем существование файла
    if not os.path.exists(args.input):
        print(f"Ошибка: файл '{args.input}' не найден", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Читаем входной файл
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Парсим конфигурацию
        data = parser.parse(text)
        
        if data is None:
            print("Ошибка при разборе конфигурации", file=sys.stderr)
            sys.exit(1)
        
        # Компилируем в XML
        xml_output = XMLCompiler.to_xml(data)
        
        # Выводим результат
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(xml_output)
            print(f"XML сохранён в файл: {args.output}")
        else:
            print(xml_output)
            
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
