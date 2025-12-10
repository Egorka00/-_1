#!/usr/bin/env python3
"""
Вариант №6 - Визуализация графа зависимостей
Требования:
1. Сформировать текстовое представление графа на языке D2
2. Сохранить изображение графа в формате SVG
3. Если задан параметр ascii_tree, вывести зависимости в виде ASCII-дерева
4. Продемонстрировать примеры визуализации для трех пакетов
5. Сравнить с выводом штатных инструментов визуализации
"""

import argparse
import json
import os
from visualizer import GraphVisualizer

def parse_arguments():
    parser = argparse.ArgumentParser(description='Визуализация графа зависимостей')
    parser.add_argument('--input', default='results_phase4.json',
                       help='Файл с результатами этапа 4')
    parser.add_argument('--config', default='config.yaml',
                       help='Конфигурационный файл')
    parser.add_argument('--output', default='graph_output.svg',
                       help='Файл для сохранения изображения')
    parser.add_argument('--ascii-tree', action='store_true',
                       help='Вывести ASCII-дерево')
    parser.add_argument('--demo', action='store_true',
                       help='Демонстрация для трех пакетов')
    
    return parser.parse_args()

def load_config(filename):
    """Загрузка конфигурации из файла"""
    config = {
        'ascii_tree': False,
        'output_image': 'graph.svg'
    }
    
    if os.path.exists(filename):
        try:
            if filename.endswith('.yaml'):
                import yaml
                with open(filename, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    config.update(yaml_config)
            elif filename.endswith('.json'):
                with open(filename, 'r') as f:
                    json_config = json.load(f)
                    config.update(json_config)
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
    
    return config

def load_phase4_results(filename):
    """Загрузка результатов этапа 4"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if 'graph' not in data:
            # Если в файле только результаты этапа 4
            return data
        
        return data
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Создаем демо-данные.")
        return create_demo_data()
    except json.JSONDecodeError:
        print(f"Некорректный формат файла {filename}. Создаем демо-данные.")
        return create_demo_data()

def create_demo_data():
    """Создание демо-данных"""
    return {
        "package": "A",
        "load_order": ["F", "G", "H", "I", "J", "L", "E", "B", "C", "D", "A"],
        "levels": {
            "F": 0, "G": 0, "H": 0, "I": 0, "J": 0, "L": 0,
            "E": 1, "B": 1, "C": 1, "D": 1,
            "A": 2
        },
        "cycles": [],
        "critical_paths": [["A", "B", "E", "L"]],
        "statistics": {
            "total_packages": 11,
            "cycles_count": 0,
            "critical_paths_count": 1
        }
    }

def load_graph_structure():
    """Загрузка структуры графа из этапа 3"""
    try:
        with open('graph_phase3.json', 'r') as f:
            data = json.load(f)
            return data['graph']
    except FileNotFoundError:
        # Создаем тестовую структуру
        return {
            'nodes': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'],
            'edges': [
                ['A', 'B'], ['A', 'C'], ['A', 'D'],
                ['B', 'E'], ['B', 'F'],
                ['C', 'G'], ['C', 'H'],
                ['D', 'I'], ['D', 'J'],
                ['E', 'K'], ['E', 'L']
            ],
            'adjacency': {
                'A': ['B', 'C', 'D'],
                'B': ['E', 'F'],
                'C': ['G', 'H'],
                'D': ['I', 'J'],
                'E': ['K', 'L']
            }
        }

def demonstrate_three_packages():
    """Демонстрация для трех различных пакетов"""
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ ВИЗУАЛИЗАЦИИ ДЛЯ ТРЕХ ПАКЕТОВ")
    print("=" * 70)
    
    demo_packages = [
        {
            'name': 'A',
            'deps': ['B', 'C', 'D'],
            'description': 'Простой граф с несколькими уровнями'
        },
        {
            'name': 'B', 
            'deps': ['E', 'F'],
            'description': 'Граф с минимальными зависимостями'
        },
        {
            'name': 'requests',
            'deps': ['urllib3', 'certifi', 'chardet', 'idna'],
            'description': 'Реальный пакет Python'
        }
    ]
    
    for i, package_info in enumerate(demo_packages, 1):
        print(f"\n{i}. Пакет: {package_info['name']}")
        print(f"   Описание: {package_info['description']}")
        
        # Создаем визуализатор для демо
        demo_visualizer = GraphVisualizer({'output_image': f'demo_{package_info["name"]}.svg'})
        
        # Создаем тестовый граф
        demo_graph = {
            'adjacency': {
                package_info['name']: package_info['deps']
            }
        }
        
        # Для реального пакета добавляем больше зависимостей
        if package_info['name'] == 'requests':
            demo_graph['adjacency'].update({
                'urllib3': ['idna', 'certifi'],
                'chardet': [],
                'certifi': [],
                'idna': []
            })
        
        # Генерация D2 кода
        print("   D2 код (фрагмент):")
        d2_code = demo_visualizer.generate_d2_simple(package_info['name'], demo_graph['adjacency'])
        lines = d2_code.split('\n')[:10]
        for line in lines:
            print(f"     {line}")
        if len(d2_code.split('\n')) > 10:
            print("     ...")
        
        # Создаем изображение
        try:
            demo_visualizer.save_svg_simple(package_info['name'], demo_graph['adjacency'])
            print(f"   Изображение: demo_{package_info['name']}.svg")
        except Exception as e:
            print(f"   Ошибка создания изображения: {e}")
        
        # ASCII-дерево
        if package_info['name'] != 'requests':  # Для простоты
            ascii_tree = demo_visualizer.generate_ascii_tree_simple(package_info['name'], demo_graph['adjacency'])
            print("   ASCII-дерево:")
            tree_lines = ascii_tree.split('\n')[:5]
            for line in tree_lines:
                print(f"     {line}")
            if len(ascii_tree.split('\n')) > 5:
                print("     ...")
    
    print("\n" + "=" * 70)

def compare_with_official_tools(package, graph_structure):
    """Сравнение с официальными инструментами визуализации"""
    print("\n" + "=" * 70)
    print("СРАВНЕНИЕ С ШТАТНЫМИ ИНСТРУМЕНТАМИ ВИЗУАЛИЗАЦИИ")
    print("=" * 70)
    
    # Имитация вывода pipdeptree
    print("\n1. Вывод pipdeptree (имитация):")
    print("-" * 40)
    
    adjacency = graph_structure.get('adjacency', {})
    
    def print_pipdeptree(pkg, level=0):
        indent = "  " * level
        print(f"{indent}{pkg}")
        
        deps = adjacency.get(pkg, [])
        for dep in sorted(deps):
            print_pipdeptree(dep, level + 1)
    
    if package in adjacency:
        print_pipdeptree(package)
    else:
        print(f"Пакет {package} не найден в графе")
    
    # Имитация вывода pip graph
    print("\n2. Вывод pip graph (имитация):")
    print("-" * 40)
    
    all_edges = []
    for node in adjacency:
        for dep in adjacency[node]:
            all_edges.append(f"{node} --> {dep}")
    
    for edge in sorted(all_edges)[:10]:
        print(f"  {edge}")
    if len(all_edges) > 10:
        print(f"  ... и еще {len(all_edges) - 10} зависимостей")
    
    # Сравнение возможностей
    print("\n3. СРАВНЕНИЕ ВОЗМОЖНОСТЕЙ:")
    print("-" * 40)
    
    comparison_table = [
        ["Функция", "Наш инструмент", "pipdeptree", "pip graph"],
        ["-"*40, "-"*40, "-"*40, "-"*40],
        ["Формат вывода", "D2, SVG, ASCII", "Текст, дерево", "Текст, граф"],
        ["Визуализация", "Графическая (SVG)", "Текстовая", "Текстовая"],
        ["Настройка стилей", "Да", "Нет", "Нет"],
        ["Фильтрация", "Да", "Ограниченная", "Нет"],
        ["Группировка", "По уровням", "По дереву", "Нет"],
        ["Цвета", "Настраиваемые", "Фиксированные", "Нет"],
        ["Экспорт", "SVG, D2, JSON", "Текст", "Текст"]
    ]
    
    for row in comparison_table:
        print(f"  {row[0]:<20} {row[1]:<15} {row[2]:<15} {row[3]:<15}")
    
    # Анализ расхождений
    print("\n4. АНАЛИЗ РАСХОЖДЕНИЙ:")
    print("-" * 40)
    
    print("  Наш инструмент может показывать больше зависимостей из-за:")
    print("  1. Полного обхода транзитивных зависимостей")
    print("  2. Учета всех уровней вложенности")
    print("  3. Отсутствия фильтрации тестовых/документационных пакетов")
    
    print("\n  pipdeptree может показывать меньше зависимостей из-за:")
    print("  1. Группировки одинаковых поддеревьев")
    print("  2. Игнорирования уже установленных пакетов")
    print("  3. Фильтрации по умолчанию")
    
    print("\n  Основные отличия в визуализации:")
    print("  1. Наш инструмент создает графические диаграммы")
    print("  2. pipdeptree показывает текстовое дерево")
    print("  3. pip graph показывает плоский список зависимостей")

def main():
    args = parse_arguments()
    
    print("=" * 70)
    print("ЭТАП 5: ВИЗУАЛИЗАЦИЯ ГРАФА ЗАВИСИМОСТЕЙ")
    print("Вариант №6")
    print("=" * 70)
    
    # Загрузка данных
    print("\nЗагрузка данных...")
    phase4_data = load_phase4_results(args.input)
    config = load_config(args.config)
    graph_structure = load_graph_structure()
    
    # Объединяем конфигурацию
    if args.ascii_tree:
        config['ascii_tree'] = True
    
    if args.output:
        config['output_image'] = args.output
    
    # Создаем визуализатор
    visualizer = GraphVisualizer(config)
    
    package = phase4_data.get('package', 'A')
    
    print(f"\nАнализируем пакет: {package}")
    print("-" * 40)
    
    # 1. Генерация D2 кода
    print("\n1. ГЕНЕРАЦИЯ ТЕКСТОВОГО ПРЕДСТАВЛЕНИЯ НА ЯЗЫКЕ D2:")
    print("-" * 40)
    
    d2_code = visualizer.generate_d2(package, graph_structure, phase4_data)
    
    # Показываем часть кода
    print("Сгенерированный код D2 (первые 20 строк):")
    lines = d2_code.split('\n')
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:3}: {line}")
    
    if len(lines) > 20:
        print(f"... и еще {len(lines) - 20} строк")
    
    # Сохраняем полный код
    with open('graph.d2', 'w') as f:
        f.write(d2_code)
    print("Полный код сохранен в файл: graph.d2")
    
    # 2. Сохранение SVG изображения
    print("\n2. СОХРАНЕНИЕ ИЗОБРАЖЕНИЯ В ФОРМАТЕ SVG:")
    print("-" * 40)
    
    success = visualizer.save_svg(package, graph_structure, phase4_data)
    
    if success:
        print(f"Изображение успешно сохранено в: {config['output_image']}")
        
        # Проверяем наличие файла
        if os.path.exists(config['output_image']):
            file_size = os.path.getsize(config['output_image'])
            print(f"Размер файла: {file_size} байт")
        else:
            print("Предупреждение: файл не найден после сохранения")
    else:
        print("Не удалось сохранить изображение. Проверьте установку Graphviz.")
        print("Установите Graphviz: https://graphviz.org/download/")
        print("Или используйте онлайн-конвертер: https://dreampuf.github.io/GraphvizOnline/")
        print("Скопируйте код из graph.d2 в онлайн-конвертер")
    
    # 3. ASCII-дерево
    if config.get('ascii_tree', False) or args.ascii_tree:
        print("\n3. ASCII-ДЕРЕВО ЗАВИСИМОСТЕЙ:")
        print("-" * 40)
        
        ascii_tree = visualizer.generate_ascii_tree(package, graph_structure)
        print(ascii_tree)
    
    # 4. Демонстрация для трех пакетов
    if args.demo:
        demonstrate_three_packages()
    else:
        print("\nДля демонстрации трех пакетов используйте флаг --demo")
    
    # 5. Сравнение с официальными инструментами
    print("\n5. СРАВНЕНИЕ С ОФИЦИАЛЬНЫМИ ИНСТРУМЕНТАМИ:")
    print("-" * 40)
    
    compare_with_official_tools(package, graph_structure)
    
    # Итоги
    print("\n" + "=" * 70)
    print("ИТОГИ ЭТАПА 5:")
    print("=" * 70)
    
    print("\nСозданы файлы:")
    print(f"  1. graph.d2 - текстовое представление на языке D2")
    print(f"  2. {config['output_image']} - графическое представление (SVG)")
    
    if config.get('ascii_tree', False):
        print("  3. ASCII-дерево выведено в консоль")
    
    print("\nДля использования D2 кода:")
    print("  1. Установите D2: https://d2lang.com/")
    print("  2. Выполните: d2 graph.d2 output.svg")
    print("  3. Или используйте онлайн: https://play.d2lang.com/")

if __name__ == "__main__":
    main()
