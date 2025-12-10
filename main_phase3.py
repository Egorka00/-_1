#!/usr/bin/env python3
"""
ЭТАП 3: Основные операции
"""

import argparse
import json
from graph_builder import DependencyGraph

def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Этап 3: Построение графа зависимостей')
    parser.add_argument('--mode', choices=['test', 'real'], default='test',
                       help='Режим работы: test (тестовый файл) или real (реальный пакет)')
    parser.add_argument('--package', default='requests',
                       help='Имя пакета для анализа (в режиме real)')
    parser.add_argument('--test-file', default='test_repo.txt',
                       help='Путь к тестовому файлу (в режиме test)')
    parser.add_argument('--max-depth', type=int, default=3,
                       help='Максимальная глубина анализа зависимостей')
    parser.add_argument('--filter', default='test',
                       help='Подстрока для фильтрации пакетов')
    parser.add_argument('--output', default='graph_phase3.json',
                       help='Файл для сохранения результатов')
    
    return parser.parse_args()

def print_header():
    """Вывод заголовка этапа"""
    print("=" * 80)
    print("ЭТАП 3: ОСНОВНЫЕ ОПЕРАЦИИ")
    print("Вариант №6 - Построение графа зависимостей")
    print("=" * 80)

def print_config(args):
    """Вывод конфигурации"""
    print("\n⚙️  КОНФИГУРАЦИЯ:")
    print(f"  Режим работы:     {args.mode}")
    print(f"  Пакет:           {args.package}")
    print(f"  Макс. глубина:   {args.max_depth}")
    print(f"  Фильтр:          '{args.filter}'")
    print(f"  Выходной файл:   {args.output}")
    print("-" * 40)

def create_test_data():
    """Создание тестового файла, если его нет"""
    test_data = """# Test repository for Variant 6
# Format: package dependency1 dependency2 ...
A B C D
B E F
C G H
D I J
E K L
F M N
G O P
H Q R
I S
J T U
K V
L W
M X
N Y
O Z AA
P BB
Q CC
R DD
S EE
T FF
U GG
V HH
W II
X JJ
Y KK
Z LL
AA MM
BB NN
CC OO
DD PP
EE QQ
FF RR
GG SS
HH TT
II UU
JJ VV
KK WW
LL XX
MM YY
NN ZZ
OO TEST1  # Будет отфильтрован
PP TEST2  # Будет отфильтрован"""
    
    with open('test_repo.txt', 'w') as f:
        f.write(test_data)
    print("Создан тестовый файл test_repo.txt")

def main():
    """Основная функция этапа 3"""
    args = parse_arguments()
    print_header()
    print_config(args)
    
    # Создаём конфигурацию для графа
    config = {
        'max_depth': args.max_depth,
        'filter_substring': args.filter
    }
    
    # Инициализация графа
    print("\n🔧 ИНИЦИАЛИЗАЦИЯ ГРАФА...")
    graph = DependencyGraph(config)
    
    # Построение графа в зависимости от режима
    if args.mode == 'test':
        print(f"\n РЕЖИМ ТЕСТИРОВАНИЯ")
        print(f"Чтение из файла: {args.test_file}")
        
        try:
            graph.build_from_test_file(args.test_file)
        except FileNotFoundError:
            print(f"Файл {args.test_file} не найден, создаём тестовые данные...")
            create_test_data()
            graph.build_from_test_file('test_repo.txt')
    else:
        print(f"\n РЕЖИМ РЕАЛЬНОГО РЕПОЗИТОРИЯ")
        print(f"Анализ пакета: {args.package}")
        graph.build_from_real_repo(args.package)
    
    # ============ РЕЗУЛЬТАТЫ ЭТАПА 3 ============
    print(f"\n{'='*80}")
    print("РЕЗУЛЬТАТЫ ЭТАПА 3:")
    print(f"{'='*80}")
    
    # 1. Статистика графа
    print(f"\n📊 СТАТИСТИКА ГРАФА:")
    print(f"  Всего узлов (пакетов): {len(graph.nodes)}")
    print(f"  Всего рёбер (зависимостей): {len(graph.edges)}")
    print(f"  Максимальная глубина анализа: {args.max_depth}")
    
    # 2. Обход графа (BFS с рекурсией)
    print(f"\n ОБХОД ГРАФА (BFS с рекурсией):")
    print("  Иерархия зависимостей:")
    
    # Показываем структуру графа
    if args.mode == 'test':
        root_package = 'A' if 'A' in graph.nodes else list(graph.nodes)[0]
    else:
        root_package = args.package
    
    print(f"\n  Корневой пакет: {root_package}")
    print("  Структура (первые 3 уровня):")
    
    # Выводим первые 3 уровня для наглядности
    def print_level(package, level=0, visited=None):
        if visited is None:
            visited = set()
        
        if level > 2:  # Ограничиваем вывод
            print(f"{'  ' * level}└─ ...")
            return
        
        if package in visited:
            print(f"{'  ' * level}└─ {package} (цикл)")
            return
        
        visited.add(package)
        print(f"{'  ' * level}├─ {package}")
        
        deps = graph.adjacency.get(package, [])
        for i, dep in enumerate(deps):
            is_last = (i == len(deps) - 1)
            prefix = '└─' if is_last else '├─'
            if dep not in visited and level < 2:
                print_level(dep, level + 1, visited)
    
    visited_set = set()
    print_level(root_package, 0, visited_set)
    
    # 3. Фильтрация по подстроке
    print(f"\n🔍 ФИЛЬТРАЦИЯ ПО ПОДСТРОКЕ:")
    print(f"  Исключаются пакеты, содержащие: '{args.filter}'")
    
    filtered_count = sum(1 for node in graph.nodes if args.filter in node)
    print(f"  Отфильтровано пакетов: {filtered_count}")
    
    # 4. Обработка циклических зависимостей
    print(f"\n🔄 ОБРАБОТКА ЦИКЛИЧЕСКИХ ЗАВИСИМОСТЕЙ:")
    cycles = graph.detect_cycles()
    
    if cycles:
        print(f"Обнаружено циклов: {len(cycles)}")
        for i, cycle in enumerate(cycles, 1):
            print(f"    Цикл {i}: {' → '.join(cycle)}")
        
        print(f"\n ОБРАБОТКА ЦИКЛОВ:")
        print("    1. Обнаружение с помощью DFS с отслеживанием стека")
        print("    2. Визуальная маркировка циклических зависимостей")
        print("    3. Предотвращение бесконечной рекурсии")
    else:
        print(f"Циклические зависимости не обнаружены")
    
    # 5. Демонстрация режима тестирования
    print(f"\n🧪 ДЕМОНСТРАЦИЯ РЕЖИМА ТЕСТИРОВАНИЯ:")
    
    # Создаём разные тестовые сценарии
    test_scenarios = [
        {"max_depth": 2, "filter": ""},
        {"max_depth": -1, "filter": "TEST"},
        {"max_depth": 1, "filter": ""}
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n  Сценарий {i}:")
        print(f"    • Макс. глубина: {scenario['max_depth'] if scenario['max_depth'] > 0 else 'без ограничений'}")
        print(f"    • Фильтр: '{scenario['filter']}'")
        
        test_graph = DependencyGraph(scenario)
        test_graph.build_from_test_file('test_repo.txt' if args.mode == 'test' else args.test_file)
        
        cycles = test_graph.detect_cycles()
        print(f"    • Узлов: {len(test_graph.nodes)}")
        print(f"    • Рёбер: {len(test_graph.edges)}")
        print(f"    • Циклов: {len(cycles)}")
    
    # Сохранение результатов
    print(f"\n СОХРАНЕНИЕ РЕЗУЛЬТАТОВ...")
    
    results = {
        "phase": 3,
        "variant": 6,
        "config": {
            "mode": args.mode,
            "package": args.package,
            "max_depth": args.max_depth,
            "filter": args.filter
        },
        "graph": {
            "nodes": list(graph.nodes),
            "edges": graph.edges,
            "adjacency": {k: v for k, v in graph.adjacency.items()},
            "statistics": {
                "total_nodes": len(graph.nodes),
                "total_edges": len(graph.edges),
                "cycles_count": len(cycles),
                "max_depth_actual": max(graph.depth_limits.values()) if graph.depth_limits else 0
            }
        },
        "algorithms": {
            "traversal": "BFS с рекурсией",
            "cycle_detection": "DFS с отслеживанием стека",
            "filtering": f"Исключение пакетов, содержащих '{args.filter}'"
        }
    }
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f" Результаты сохранены в {args.output}")

if __name__ == "__main__":
    main()
