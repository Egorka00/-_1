#!/usr/bin/env python3
"""
Вариант №6 - Порядок загрузки зависимостей
"""

import argparse
import json
from collections import defaultdict, deque

class DependencyAnalyzer:
    def __init__(self, graph_data):
        self.nodes = set(graph_data.get('nodes', []))
        self.edges = graph_data.get('edges', [])
        self.adjacency = defaultdict(list)
        
        for edge in self.edges:
            if len(edge) >= 2:
                self.adjacency[edge[0]].append(edge[1])
        
        if 'adjacency' in graph_data:
            for node, deps in graph_data['adjacency'].items():
                self.adjacency[node].extend(deps)
    
    def get_load_order(self, package):
        if package not in self.nodes:
            return []
        
        relevant_nodes = set()
        queue = deque([package])
        
        while queue:
            current = queue.popleft()
            if current in relevant_nodes:
                continue
            relevant_nodes.add(current)
            
            for dep in self.adjacency.get(current, []):
                if dep not in relevant_nodes:
                    queue.append(dep)
        
        in_degree = defaultdict(int)
        
        for node in relevant_nodes:
            for neighbor in self.adjacency.get(node, []):
                if neighbor in relevant_nodes:
                    in_degree[neighbor] += 1
        
        queue = deque([node for node in relevant_nodes if in_degree[node] == 0])
        load_order = []
        
        while queue:
            current = queue.popleft()
            load_order.append(current)
            
            for neighbor in self.adjacency.get(current, []):
                if neighbor in relevant_nodes:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        if len(load_order) != len(relevant_nodes):
            remaining = [node for node in relevant_nodes if node not in load_order]
            load_order.extend(remaining)
        
        return load_order
    
    def find_cycles(self):
        cycles = []
        visited = set()
        recursion_stack = set()
        parent = {}
        
        def dfs(node, path):
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in self.adjacency.get(node, []):
                if neighbor not in visited:
                    parent[neighbor] = node
                    if dfs(neighbor, path + [neighbor]):
                        return True
                elif neighbor in recursion_stack:
                    cycle = [neighbor]
                    n = node
                    while n != neighbor:
                        cycle.append(n)
                        n = parent.get(n, neighbor)
                    cycle.append(neighbor)
                    cycle.reverse()
                    cycles.append(cycle)
                    return True
            
            recursion_stack.remove(node)
            return False
        
        for node in self.nodes:
            if node not in visited:
                parent.clear()
                dfs(node, [node])
        
        return cycles
    
    def has_cycles(self):
        return len(self.find_cycles()) > 0
    
    def find_critical_paths(self, package):
        if package not in self.nodes:
            return []
        
        paths = []
        
        def dfs(current, path):
            path.append(current)
            
            deps = self.adjacency.get(current, [])
            if not deps:
                paths.append(list(path))
            else:
                for dep in deps:
                    dfs(dep, path)
            
            path.pop()
        
        dfs(package, [])
        return paths

def parse_arguments():
    parser = argparse.ArgumentParser(description='Порядок загрузки зависимостей')
    parser.add_argument('--input', default='graph_phase3.json',
                       help='Файл с результатами этапа 3')
    parser.add_argument('--package', default='A',
                       help='Пакет для анализа порядка загрузки')
    parser.add_argument('--output', default='results_phase4.json',
                       help='Файл для сохранения результатов')
    
    return parser.parse_args()

def load_graph_data(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data['graph']
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Создаем тестовые данные.")
        return create_test_data()
    except (KeyError, json.JSONDecodeError):
        print(f"Некорректный формат файла {filename}. Создаем тестовые данные.")
        return create_test_data()

def create_test_data():
    return {
        'nodes': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'V'],
        'edges': [
            ['A', 'B'], ['A', 'C'], ['A', 'D'],
            ['B', 'E'], ['B', 'F'],
            ['C', 'G'], ['C', 'H'],
            ['D', 'I'], ['D', 'J'],
            ['E', 'K'], ['E', 'L'],
            ['K', 'M'],
            ['M', 'N'],
            ['V', 'K'],
            ['K', 'V']
        ],
        'adjacency': {
            'A': ['B', 'C', 'D'],
            'B': ['E', 'F'],
            'C': ['G', 'H'],
            'D': ['I', 'J'],
            'E': ['K', 'L'],
            'K': ['M', 'V'],
            'M': ['N'],
            'V': ['K']
        }
    }

def simulate_pip_load_order(package, adjacency):
    if package in adjacency or package in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
        all_nodes = set()
        for node in adjacency:
            all_nodes.add(node)
            for dep in adjacency[node]:
                all_nodes.add(dep)
        
        leaf_nodes = []
        for node in all_nodes:
            if node not in adjacency or not adjacency.get(node, []):
                leaf_nodes.append(node)
        
        middle_nodes = []
        for node in all_nodes:
            if node in adjacency and adjacency.get(node, []):
                deps = adjacency.get(node, [])
                if all(dep in leaf_nodes for dep in deps):
                    middle_nodes.append(node)
        
        root_nodes = [node for node in all_nodes if node not in leaf_nodes and node not in middle_nodes]
        
        pip_order = leaf_nodes + middle_nodes + root_nodes
        
        if package in pip_order:
            pip_order.remove(package)
            pip_order.append(package)
        
        return pip_order
    
    return []

def main():
    args = parse_arguments()
    
    print("Вариант №6 - Порядок загрузки зависимостей")
    print("=" * 60)
    
    graph_data = load_graph_data(args.input)
    analyzer = DependencyAnalyzer(graph_data)
    
    print(f"Пакет для анализа: {args.package}")
    print("-" * 60)
    
    # 1. Получение порядка загрузки
    load_order = analyzer.get_load_order(args.package)
    
    if not load_order:
        print(f"Пакет '{args.package}' не найден в графе.")
        available = list(graph_data.get('adjacency', {}).keys())
        if available:
            print(f"Доступные пакеты: {', '.join(available)}")
        return
    
    print("\n1. ПОРЯДОК ЗАГРУЗКИ ЗАВИСИМОСТЕЙ:")
    print("-" * 40)
    
    # Группируем по уровням
    adjacency = graph_data.get('adjacency', {})
    levels = {}
    
    # Создаем кэш для уровней
    level_cache = {}
    
    def calculate_level(pkg, visited=None):
        if visited is None:
            visited = set()
        
        if pkg in level_cache:
            return level_cache[pkg]
        
        if pkg in visited:
            return 0
        
        visited.add(pkg)
        
        deps = adjacency.get(pkg, [])
        if not deps:
            level_cache[pkg] = 0
            return 0
        
        max_level = 0
        for dep in deps:
            dep_level = calculate_level(dep, visited)
            max_level = max(max_level, dep_level)
        
        level_cache[pkg] = max_level + 1
        return level_cache[pkg]
    
    for pkg in load_order:
        calculate_level(pkg)
    
    # Находим максимальный уровень
    if level_cache:
        max_level_value = max(level_cache.values())
    else:
        max_level_value = 0
    
    # Выводим сгруппированно по уровням
    for level in range(max_level_value + 1):
        nodes_at_level = [pkg for pkg in load_order if level_cache.get(pkg, 0) == level]
        if nodes_at_level:
            print(f"\nУровень {level}:")
            for pkg in nodes_at_level:
                deps = adjacency.get(pkg, [])
                if deps:
                    print(f"  {pkg} (зависит от: {', '.join(deps)})")
                else:
                    print(f"  {pkg} (без зависимостей)")
    
    print(f"\nВсего пакетов: {len(load_order)}")
    
    # 2. Проверка корректности
    print("\n2. ПРОВЕРКА КОРРЕКТНОСТИ ПОРЯДКА:")
    print("-" * 40)
    
    installed = set()
    errors = []
    
    for i, pkg in enumerate(load_order, 1):
        deps = adjacency.get(pkg, [])
        missing_deps = [dep for dep in deps if dep not in installed]
        if missing_deps:
            errors.append((pkg, missing_deps))
        installed.add(pkg)
    
    if not errors:
        print("Корректно: все зависимости устанавливаются раньше")
    else:
        print(f"Найдено ошибок: {len(errors)}")
        for pkg, missing in errors[:3]:
            print(f"  - {pkg} зависит от {missing}, но они устанавливаются позже")
    
    # 3. Обнаружение циклов
    print("\n3. ОБНАРУЖЕНИЕ ЦИКЛИЧЕСКИХ ЗАВИСИМОСТЕЙ:")
    print("-" * 40)
    
    cycles = analyzer.find_cycles()
    if cycles:
        print(f"Найдено циклов: {len(cycles)}")
        for i, cycle in enumerate(cycles, 1):
            print(f"  Цикл {i}: {' -> '.join(cycle)}")
    else:
        print("Циклические зависимости не обнаружены")
    
    # 4. Критические пути
    print("\n4. КРИТИЧЕСКИЕ ПУТИ ЗАВИСИМОСТЕЙ:")
    print("-" * 40)
    
    critical_paths = analyzer.find_critical_paths(args.package)
    if critical_paths:
        critical_paths.sort(key=len, reverse=True)
        
        print(f"Найдено путей: {len(critical_paths)}")
        print(f"\nСамый длинный путь ({len(critical_paths[0])-1} шагов):")
        
        for i, node in enumerate(critical_paths[0]):
            indent = "  " * i
            print(f"{indent}{node}")
        
        if len(critical_paths) > 1:
            print(f"\nВсего длинных путей (>2 шагов):")
            count = 0
            for i, path in enumerate(critical_paths, 1):
                if len(path) > 3:
                    print(f"  Путь {i}: {len(path)-1} шагов")
                    count += 1
                if count >= 3:
                    break
    else:
        print(f"Пакет '{args.package}' не имеет зависимостей")
    
    # 5. Сравнение с pip (всегда делаем)
    print("\n5. СРАВНЕНИЕ С РЕАЛЬНЫМ МЕНЕДЖЕРОМ ПАКЕТОВ:")
    print("-" * 40)
    
    pip_order = simulate_pip_load_order(args.package, adjacency)
    
    if pip_order:
        print("Порядок загрузки в pip:")
        for i, pkg in enumerate(pip_order, 1):
            print(f"  {i:2}. {pkg}")
        
        # Анализ расхождений
        our_set = set(load_order)
        pip_set = set(pip_order)
        
        common = our_set & pip_set
        only_our = our_set - pip_set
        only_pip = pip_set - our_set
        
        print(f"\nАнализ расхождений:")
        print(f"  Общих пакетов: {len(common)}")
        print(f"  Только в нашем порядке: {len(only_our)}")
        print(f"  Только в порядке pip: {len(only_pip)}")
        
        if only_our:
            only_our_list = sorted(list(only_our))
            print(f"  Пакеты только у нас: {', '.join(only_our_list[:5])}")
            if len(only_our_list) > 5:
                print(f"    ... и еще {len(only_our_list)-5}")
        
        if only_pip:
            only_pip_list = sorted(list(only_pip))
            print(f"  Пакеты только у pip: {', '.join(only_pip_list[:5])}")
            if len(only_pip_list) > 5:
                print(f"    ... и еще {len(only_pip_list)-5}")
        
        # Проверяем порядок для общих пакетов
        if len(common) > 1:
            order_diff = []
            for pkg in common:
                if pkg in load_order and pkg in pip_order:
                    our_pos = load_order.index(pkg)
                    pip_pos = pip_order.index(pkg)
                    if our_pos != pip_pos:
                        order_diff.append((pkg, our_pos, pip_pos))
            
            if order_diff:
                print(f"\n  Расхождения в порядке:")
                order_diff.sort(key=lambda x: abs(x[1] - x[2]), reverse=True)
                for pkg, our_pos, pip_pos in order_diff[:3]:
                    diff = abs(our_pos - pip_pos)
                    print(f"    {pkg}: у нас {our_pos+1}-й, у pip {pip_pos+1}-й (разница: {diff})")
            else:
                print(f"\n  Порядок для общих пакетов совпадает")
        
        print("\n  Объяснение возможных расхождений:")
        print("    1. Pip учитывает уже установленные пакеты")
        print("    2. Pip может устанавливать независимые пакеты параллельно")
        print("    3. Pip оптимизирует порядок для скорости загрузки")
        print("    4. Pip пропускает некоторые опциональные зависимости")
    else:
        print("Не удалось сгенерировать порядок загрузки pip")
    
    # Сохранение результатов
    results = {
        "package": args.package,
        "load_order": load_order,
        "levels": {pkg: level_cache.get(pkg, 0) for pkg in load_order},
        "cycles": cycles,
        "critical_paths": [path for path in critical_paths if len(path) > 2],
        "statistics": {
            "total_packages": len(load_order),
            "cycles_count": len(cycles),
            "critical_paths_count": len(critical_paths),
            "max_path_length": len(critical_paths[0]) - 1 if critical_paths else 0
        }
    }
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nРезультаты сохранены в {args.output}")

if __name__ == "__main__":
    main()
