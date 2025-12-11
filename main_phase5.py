#!/usr/bin/env python3
"""
Вариант №6 - Визуализация графа зависимостей
"""

import argparse
import json
import os
import sys
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
        # Создаем тестовую структуру без циклов
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
    print("ДЕМОНСТРАЦИЯ ВИЗУАЛИЗАЦИИ ДЛЯ ТРЕХ ПАКЕТОВ")
    
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
            'name': 'simple',
            'deps': ['dep1', 'dep2'],
            'description': 'Простой пример'
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
        
        # Генерация D2 кода
        print("   D2 код (фрагмент):")
        d2_code = demo_visualizer.generate_d2_simple(package_info['name'], demo_graph['adjacency'])
        lines = d2_code.split('\n')[:5]
        for line in lines:
            print(f"     {line}")
        if len(d2_code.split('\n')) > 5:
            print("     ...")
        
        # Создаем изображение
        try:
            demo_visualizer.save_svg_simple(package_info['name'], demo_graph['adjacency'])
            print(f"   Изображение: demo_{package_info['name']}.svg")
        except Exception as e:
            print(f"   Ошибка создания изображения: {e}")
        
        # ASCII-дерево
        ascii_tree = demo_visualizer.generate_ascii_tree_simple(package_info['name'], demo_graph['adjacency'])
        print("   ASCII-дерево:")
        tree_lines = ascii_tree.split('\n')[:5]
        for line in tree_lines:
            print(f"     {line}")
    

def compare_with_official_tools(package, graph_structure):
    """Сравнение с официальными инструментами визуализации"""
    print("СРАВНЕНИЕ С ШТАТНЫМИ ИНСТРУМЕНТАМИ ВИЗУАЛИЗАЦИИ")

    
    # Имитация вывода pipdeptree (без рекурсии!)
    print("\n1. Вывод pipdeptree (имитация):")

    
    adjacency = graph_structure.get('adjacency', {})
    
    if package in adjacency:
        # Используем BFS вместо рекурсии
        visited = set()
        queue = [(package, 0)]
        
        while queue:
            current_pkg, level = queue.pop(0)
            if current_pkg in visited:
                continue
                
            indent = "  " * level
            print(f"{indent}{current_pkg}")
            visited.add(current_pkg)
            
            # Добавляем зависимости
            deps = adjacency.get(current_pkg, [])
            for dep in sorted(deps):
                if dep not in visited:
                    queue.append((dep, level + 1))
    else:
        print(f"Пакет {package} не найден в графе")
    
    # Имитация вывода pip graph
    print("\n2. Вывод pip graph (имитация):")
    
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
    
    comparison_table = [
        ["Функция", "Наш инструмент", "pipdeptree", "pip graph"],
        ["-"*15, "-"*15, "-"*15, "-"*15],
        ["Формат вывода", "D2, SVG, ASCII", "Текст, дерево", "Текст, граф"],
        ["Визуализация", "Графическая (SVG)", "Текстовая", "Текстовая"],
        ["Настройка стилей", "Да", "Нет", "Нет"],
        ["Фильтрация", "Да", "Ограниченная", "Нет"],
        ["Группировка", "По уровням", "По дереву", "Нет"],
        ["Цвета", "Настраиваемые", "Фиксированные", "Нет"],
        ["Экспорт", "SVG, D2, JSON", "Текст", "Текст"]
    ]
    
    for row in comparison_table:
        print(f"  {row[0]:<15} {row[1]:<15} {row[2]:<15} {row[3]:<15}")
    
    # Анализ расхождений
    print("\n4. АНАЛИЗ РАСХОЖДЕНИЙ:")
    

def main():
    args = parse_arguments()    

    print("ЭТАП 5: ВИЗУАЛИЗАЦИЯ ГРАФА ЗАВИСИМОСТЕЙ")
    
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
    
    # 1. Генерация D2 кода
    print("\n1. ГЕНЕРАЦИЯ ТЕКСТОВОГО ПРЕДСТАВЛЕНИЯ НА ЯЗЫКЕ D2:")

    
    d2_code = visualizer.generate_d2(package, graph_structure, phase4_data)
    
    # Показываем часть кода
    print("Сгенерированный код D2 (первые 15 строк):")
    lines = d2_code.split('\n')
    for i, line in enumerate(lines[:15], 1):
        print(f"{i:3}: {line}")
    
    if len(lines) > 15:
        print(f"... и еще {len(lines) - 15} строк")
    
    # Сохраняем полный код
    with open('graph.d2', 'w') as f:
        f.write(d2_code)
    print("Полный код сохранен в файл: graph.d2")
    
    # 2. Сохранение SVG изображения
    print("\n2. СОХРАНЕНИЕ ИЗОБРАЖЕНИЯ В ФОРМАТЕ SVG:")

    
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
        print("Не удалось сохранить изображение.")

    # 3. ASCII-дерево
    if config.get('ascii_tree', False) or args.ascii_tree:
        print("\n3. ASCII-ДЕРЕВО ЗАВИСИМОСТЕЙ:")
        
        try:
            ascii_tree = visualizer.generate_ascii_tree(package, graph_structure)
            print(ascii_tree)
        except RecursionError:
            print("Не удалось построить ASCII-дерево (циклы в графе)")
            # Показываем простое дерево
            adjacency = graph_structure.get('adjacency', {})
            simple_tree = visualizer.generate_ascii_tree_simple(package, adjacency)
            print(simple_tree)
    
    # 4. Демонстрация для трех пакетов
    if args.demo:
        demonstrate_three_packages()
    else:
        print("\nДля демонстрации трех пакетов используйте флаг --demo")
    
    # 5. Сравнение с официальными инструментами
    print("\n5. СРАВНЕНИЕ С ОФИЦИАЛЬНЫМИ ИНСТРУМЕНТАМИ:")
    
    compare_with_official_tools(package, graph_structure)
    
    # Итоги
    print("ИТОГИ ЭТАПА 5:")
    
    print("\nСозданы файлы:")
    print(f"  1. graph.d2 - текстовое представление на языке D2")
    if success:
        print(f"  2. {config['output_image']} - графическое представление (SVG)")
    
    if config.get('ascii_tree', False):
        print("  3. ASCII-дерево выведено в консоль")


if __name__ == "__main__":
    # Увеличиваем лимит рекурсии на всякий случай
    sys.setrecursionlimit(10000)
    main()
