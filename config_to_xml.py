#!/usr/bin/env python3
import sys
import re

#  ПРОСТОЙ ПАРСЕР 

def parse_config(text):
    """Простой парсер - ищет шаблоны в тексте"""
    lines = text.split('\n')
    result = []
    constants = {}
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # 1. Константа: var имя значение;
        if line.startswith('var '):
            match = re.match(r'var\s+(\w+)\s+([\d\.]+)\s*;', line)
            if match:
                name, value = match.groups()
                constants[name] = float(value) if '.' in value else int(value)
                result.append(('constant', name, value))
            continue
            
        # 2. Словарь: имя { ... }
        if '{' in line and '}' not in line:
            name = line.split('{')[0].strip()
            result.append(('start_dict', name))
            continue
            
        if '}' in line:
            result.append(('end_dict', ''))
            continue
            
        # 3. Пара ключ=значение
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().rstrip(',')
            
            # Убираем [[ и ]] у строк
            if value.startswith('[[') and value.endswith(']]'):
                value = value[2:-2]
                result.append(('pair', key, ('string', value)))
            
            # Число
            elif re.match(r'^[\d\.]+$', value):
                value = float(value) if '.' in value else int(value)
                result.append(('pair', key, ('number', value)))
            
            # Вычисление: §...§
            elif value.startswith('§') and value.endswith('§'):
                expr = value[1:-1]  # убираем §
                parts = expr.split()
                
                # Пытаемся вычислить
                try:
                    # Пример: §basePort offset +§
                    # или: §basePort 100 +§
                    
                    # Вариант 1: константа число операция (например: basePort 100 +)
                    if len(parts) == 3:
                        const_or_num1, const_or_num2, op = parts
                        
                        # Получаем первое значение
                        if const_or_num1 in constants:
                            val1 = constants[const_or_num1]
                        elif re.match(r'^[\d\.]+$', const_or_num1):
                            val1 = float(const_or_num1) if '.' in const_or_num1 else int(const_or_num1)
                        else:
                            val1 = 0  # по умолчанию
                        
                        # Получаем второе значение
                        if const_or_num2 in constants:
                            val2 = constants[const_or_num2]
                        elif re.match(r'^[\d\.]+$', const_or_num2):
                            val2 = float(const_or_num2) if '.' in const_or_num2 else int(const_or_num2)
                        else:
                            val2 = 0  # по умолчанию
                        
                        # Выполняем операцию
                        if op == '+':
                            result_val = val1 + val2
                        elif op == '-':
                            result_val = val1 - val2
                        else:
                            result_val = f"UNKNOWN_OP_{op}"
                        
                        result.append(('pair', key, ('number', result_val)))
                        
                    # Вариант 2: просто имя константы
                    elif len(parts) == 1 and parts[0] in constants:
                        result_val = constants[parts[0]]
                        result.append(('pair', key, ('number', result_val)))
                        
                    else:
                        result.append(('pair', key, ('string', f"EXPR:{expr}")))
                        
                except Exception as e:
                    result.append(('pair', key, ('string', f"ERROR:{e}")))
            
            # Массив: #(...)
            elif value.startswith('#(') and value.endswith(')'):
                items = value[2:-1].strip().split()
                # Преобразуем элементы массива
                array_items = []
                for item in items:
                    if item.startswith('[[') and item.endswith(']]'):
                        array_items.append(('string', item[2:-2]))
                    elif re.match(r'^[\d\.]+$', item):
                        val = float(item) if '.' in item else int(item)
                        array_items.append(('number', val))
                    else:
                        array_items.append(('string', item))
                result.append(('pair', key, ('array', array_items)))
            
            # Булево значение
            elif value in ['true', 'false']:
                result.append(('pair', key, ('boolean', value)))
            
            # Просто строка (что не распознано)
            else:
                result.append(('pair', key, ('string', value)))
    
    return result, constants

# ========== ПРОСТОЙ ГЕНЕРАТОР XML ==========

def to_xml(parsed_data, dict_name):
    """Преобразует распарсенные данные в простой XML"""
    xml_lines = [f'<?xml version="1.0" encoding="UTF-8"?>', f'<{dict_name}>']
    
    for item in parsed_data:
        if item[0] == 'pair':
            _, key, value_info = item
            value_type, value = value_info
            
            if value_type == 'string':
                xml_lines.append(f'  <{key}>{value}</{key}>')
            elif value_type == 'number':
                xml_lines.append(f'  <{key}>{value}</{key}>')
            elif value_type == 'boolean':
                xml_lines.append(f'  <{key}>{value}</{key}>')
            elif value_type == 'array':
                xml_lines.append(f'  <{key}>')
                for array_item in value:
                    item_type, item_val = array_item
                    xml_lines.append(f'    <item>{item_val}</item>')
                xml_lines.append(f'  </{key}>')
    
    xml_lines.append(f'</{dict_name}>')
    return '\n'.join(xml_lines)

# ========== ГЛАВНАЯ ФУНКЦИЯ ==========

def main():
    """Главная функция - читает файл и выводит XML"""
    if len(sys.argv) < 2:
        print("Использование: python config_to_xml.py файл.conf")
        print("Пример: python config_to_xml.py example.conf")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        # Читаем файл
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"Читаем файл: {filename}")
        print()
        
        # Парсим
        parsed, constants = parse_config(text)
        
        # Ищем имя главного словаря
        dict_name = "config"
        for item in parsed:
            if item[0] == 'start_dict':
                dict_name = item[1]
                break
        
        # Генерируем XML
        xml_output = to_xml(parsed, dict_name)
        
        # Выводим результат
        print(xml_output)
        
        # Также показываем, что распарсили (для отладки)
        print()
        print("=== Что распарсили (для отладки)")
        for item in parsed:
            print(f"  {item}")
        
        if constants:
            print()
            print("Константы")
            for name, value in constants.items():
                print(f"  {name} = {value}")
                
    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден")
    except Exception as e:
        print(f"Ошибка: {e}")

# ========== ПРИМЕР КОНФИГУРАЦИИ ==========

EXAMPLE_CONFIG = """
var basePort 8080;
var offset 20;

server {
    name = [[Мой сервер]],
    port = §basePort offset +§,
    version = 2.5,
    endpoints = #( [[/api]] [[/home]] [[/admin]] ),
    enabled = true,
    timeout = 30
}
"""

# ========== ТЕСТ ==========

def test():
    """Проверка работы программы"""
    print("ТЕСТ ПРОГРАММЫ")
    print()
    print("Тестовый конфиг:")
    print(EXAMPLE_CONFIG)
    print()
    
    # Тестируем на примере
    parsed, constants = parse_config(EXAMPLE_CONFIG)
    
    print("Распарсено:")
    for item in parsed:
        print(f"  {item}")
    
    print()
    print("Константы:", constants)
    
    # Генерируем XML
    xml = to_xml(parsed, "server")
    print()
    print("XML результат:")
    print(xml)

# ========== ЗАПУСК ==========

if __name__ == "main":
    # Если не переданы аргументы - показываем тест
    if len(sys.argv) == 1:
        test()
        print()
        print("="*50)
        print("Чтобы использовать с файлом:")
        print("python config_to_xml.py ваш_файл.conf")
    else:
        main()
