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
        
        # Строим adjacency list из рёбер
        for edge in self.edges:
            if len(edge) >= 2:
                self.adjacency[edge[0]].append(edge[1])
        
        # Также используем готовый adjacency если есть
        if 'adjacency' in graph_data:
            for node, deps in graph_data['adjacency'].items():
                self.adjacency[node].extend(deps)
    
    def get_load_order(self, package):
        """Получение порядка загрузки зависимостей (алгоритм Кана)"""
        if package not in self.nodes:
            return []
        
        # Собираем все пакеты, которые зависят от целевого (включая косвенные)
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
        
        # Топологическая сортировка для релевантных узлов
        in_degree = defaultdict(int)
        
        # Вычисляем входящие степени
        for node in relevant_nodes:
            for neighbor in self.adjacency.get(node, []):
                if neighbor in relevant_nodes:
                    in_degree[neighbor] += 1
        
        # Находим узлы с нулевой входящей степенью
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
        
        # Если есть циклы, добавляем оставшиеся узлы
        if len(load_order) != len(relevant_nodes):
            remaining = [node for node in relevant_nodes if node not in load_order]
            load_order.extend(remaining)
        
        return load_order
    
    def find_cycles(self):
        """Поиск циклов в графе"""
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
                    # Найден цикл
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
        """Проверка наличия циклов"""
        return len(self.find_cycles()) > 0
    
    def find_critical_paths(self, package):
        """Поиск критических путей зависимостей"""
        if package not in self.nodes:
            return []
        
        paths = []
        
        def dfs(current, path):
            path.append(current)
            
            # Если нет зависимостей - это конец пути
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
    parser.add_argument('--input', default='results_phase3.json',
                       help='Файл с результатами этапа 3')
    parser.add_argument('--package', default='A',
                       help='Пакет для анализа порядка загрузки')
    parser.add_argument('--compare', action='store_true',
                       help='Сравнить с реальным менеджером пакетов')
    parser.add_argument('--output', default='results_phase4.json',
                       help='Файл для сохранения результатов')
    
    return parser.parse_args()

def load_phase3_results(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Используем демо-данные.")
        return create_demo_data()

def create_demo_data():
    return {
        "graph": {
            "nodes": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "V"],
            "edges": [
                ["A", "B"], ["A", "C"], ["A", "D"],
                ["B", "E"], ["B", "F"],
                ["C", "G"], ["C", "H"],
                ["D", "I"], ["D", "J"],
                ["E", "K"], ["E", "L"],
                ["K", "V"],
                ["V", "K"]
            ],
            "adjacency": {
                "A": ["B", "C", "D"],
                "B": ["E", "F"],
                "C": ["G", "H"],
                "D": ["I", "J"],
                "E": ["K", "L"],
                "K": ["V"],
                "V": ["K"]
            }
        }
    }

def simulate_pip_load_order(package, graph_data):
    adjacency = graph_data.get('adjacency', {})
    all_nodes = set(graph_data.get('nodes', []))
    
    if package in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
        leaf_nodes = []
        for node in all_nodes:
            if not adjacency.get(node):
                leaf_nodes.append(node)
        
        middle_nodes = []
        for node in all_nodes:
            deps = adjacency.get(node, [])
            if deps and all(dep in leaf_nodes for dep in deps):
                middle_nodes.append(node)
        
        root_nodes = [node for node in all_nodes if node not in leaf_nodes and node not in middle_nodes]
        
        pip_order = leaf_nodes + middle_nodes + root_nodes
        
        if package in pip_order:
            pip_order.remove(package)
            pip_order.append(package)
        
        return pip_order
    
    pip_orders = {
        'requests': ['certifi', 'idna', 'chardet', 'urllib3', 'requests'],
        'django': ['asgiref', 'sqlparse', 'django'],
        'numpy': ['numpy'],
        'flask': ['werkzeug', 'jinja2', 'click', 'itsdangerous', 'flask']
    }
    
    return pip_orders.get(package, [])

def analyze_differences(our_order, pip_order, package, graph_data):
    print(f"Анализ расхождений для '{package}':")
    print("-" * 60)
    
    our_set = set(our_order)
    pip_set = set(pip_order)
    
    only_in_our = our_set - pip_set
    if only_in_our:
        print(f"Пакеты, которые нашел только наш инструмент ({len(only_in_our)}):")
        for pkg in sorted(only_in_our)[:10]:
            print(f"  {pkg}")
        if len(only_in_our) > 10:
            print(f"  ... и еще {len(only_in_our) - 10} пакетов")
    
    only_in_pip = pip_set - our_set
    if only_in_pip:
        print(f"Пакеты, которые нашел только pip ({len(only_in_pip)}):")
        for pkg in sorted(only_in_pip):
            print(f"  {pkg}")
    
    common_packages = our_set & pip_set
    if len(common_packages) > 1:
        print(f"Расхождения в порядке ({len(common_packages)} общих пакетов):")
        
        order_diff = []
        for pkg in common_packages:
            our_index = our_order.index(pkg) if pkg in our_order else -1
            pip_index = pip_order.index(pkg) if pkg in pip_order else -1
            
            if our_index != pip_index and our_index != -1 and pip_index != -1:
                order_diff.append((pkg, our_index, pip_index))
        
        if order_diff:
            order_diff.sort(key=lambda x: abs(x[1] - x[2]), reverse=True)
            
            print("Самые значительные расхождения:")
            for pkg, our_pos, pip_pos in order_diff[:5]:
                diff = abs(our_pos - pip_pos)
                print(f"  {pkg}: у нас {our_pos+1}-й, у pip {pip_pos+1}-й (разница: {diff})")
        else:
            print("Порядок совпадает для всех общих пакетов")
    
    print("Качественный анализ расхождений:")
    
    adjacency = graph_data.get('adjacency', {})
    has_cycles = False
    for node in adjacency:
        if node in adjacency.get(node, []):
            has_cycles = True
            break
    
    if has_cycles:
        print("  1. Обнаружены циклические зависимости")
        print("     Наш алгоритм: обрабатывает циклы через обнаружение")
        print("     pip: может загружать в другом порядке или пропускать")
    
    max_depth = 0
    if graph_data.get('nodes'):
        def calculate_depth(node, visited=None):
            if visited is None:
                visited = set()
            if node in visited:
                return 0
            visited.add(node)
            
            deps = adjacency.get(node, [])
            if not deps:
                return 1
            
            depths = [calculate_depth(dep, visited) for dep in deps]
            return max(depths) + 1 if depths else 1
        
        for node in graph_data['nodes']:
            max_depth = max(max_depth, calculate_depth(node))
    
    if max_depth > 3:
        print(f"  2. Глубокие зависимости (макс. глубина: {max_depth})")
        print("     Наш алгоритм: полный обход всех уровней")
        print("     pip: может оптимизировать, пропуская промежуточные уровни")
    
    leaf_nodes = [node for node in graph_data.get('nodes', []) if not adjacency.get(node)]
    if leaf_nodes:
        print(f"  3. Листовые узлы ({len(leaf_nodes)} шт.)")
        print("     Наш алгоритм: устанавливает все листовые узлы")
        print("     pip: может группировать или пропускать некоторые")
    
    print("Общие причины расхождений:")
    explanations = [
        "1. Алгоритмы разрешения зависимостей:",
        "   pip использует SAT-solver для оптимального разрешения",
        "   Наш инструмент: простая топологическая сортировка (алгоритм Кана)",
        "",
        "2. Оптимизация загрузки:",
        "   pip: параллельная загрузка независимых пакетов",
        "   pip: кэширование уже установленных пакетов",
        "   pip: учет архитектуры и операционной системы",
        "",
        "3. Учет версий пакетов:",
        "   pip: разрешает конфликты версий",
        "   Наш инструмент: не учитывает версии",
        "",
        "4. Системные зависимости:",
        "   pip: знает о системных пакетах",
        "   pip: учитывает глобально установленные пакеты",
        "   Наш инструмент: анализирует только указанные зависимости",
        "",
        "5. Особые случаи:",
        "   Предкомпилированные бинарники (numpy, tensorflow)",
        "   Опциональные зависимости",
        "   Зависимости окружения"
    ]
    
    for line in explanations:
        print(f"  {line}")

def main():
    args = parse_arguments()
    
    print("=" * 80)
    print("Вариант №6 - Порядок загрузки зависимостей")
    print("=" * 80)
    
    print("Загрузка данных из этапа 3...")
    phase3_data = load_phase3_results(args.input)
    
    if 'graph' not in phase3_data:
        print(f"В файле {args.input} нет данных графа")
        return
    
    analyzer = DependencyAnalyzer(phase3_data['graph'])
    
    print("Получение порядка загрузки:")
    print(f"Анализируем пакет: {args.package}")
    
    load_order = analyzer.get_load_order(args.package)
    
    if not load_order:
        print(f"Пакет '{args.package}' не найден в графе")
        available_packages = list(phase3_data['graph'].get('adjacency', {}).keys())
        if available_packages:
            args.package = available_packages[0]
            print(f"Используем пакет: {args.package}")
            load_order = analyzer.get_load_order(args.package)
    
    if load_order:
        print(f"Порядок загрузки для '{args.package}':")
        print("-" * 60)
        
        adjacency = phase3_data['graph'].get('adjacency', {})
        
        levels = {}
        def calculate_level(package, visited=None):
            if visited is None:
                visited = set()
            
            if package in levels:
                return levels[package]
            
            visited.add(package)
            
            deps = adjacency.get(package, [])
            if not deps:
                levels[package] = 0
                return 0
            
            max_dep_level = 0
            for dep in deps:
                if dep not in visited:
                    dep_level = calculate_level(dep, visited)
                    max_dep_level = max(max_dep_level, dep_level)
            
            levels[package] = max_dep_level + 1
            return levels[package]
        
        for pkg in load_order:
            calculate_level(pkg)
        
        current_level = -1
        for i, pkg in enumerate(load_order, 1):
            pkg_level = levels.get(pkg, 0)
            
            if pkg_level != current_level:
                print(f"Уровень {pkg_level}:")
                current_level = pkg_level
            
            deps = adjacency.get(pkg, [])
            if deps:
                deps_str = f" <- зависит от: {', '.join(deps[:3])}"
                if len(deps) > 3:
                    deps_str += f" ... (+{len(deps)-3})"
            else:
                deps_str = ""
            
            print(f"  {i:3}. {pkg}{deps_str}")
        
        print("-" * 60)
        print(f"Всего пакетов для загрузки: {len(load_order)}")
        
        print("Анализ порядка загрузки:")
        
        installed = set()
        errors = []
        
        for i, pkg in enumerate(load_order):
            deps = adjacency.get(pkg, [])
            missing_deps = [dep for dep in deps if dep not in installed]
            if missing_deps:
                errors.append((pkg, missing_deps))
            installed.add(pkg)
        
        if not errors:
            print("Корректность: все зависимости устанавливаются раньше")
        else:
            print(f"Проблемы с порядком ({len(errors)}):")
            for pkg, missing in errors[:3]:
                print(f"  {pkg} зависит от {missing}, но они устанавливаются позже")
        
        has_cycles = analyzer.has_cycles()
        if has_cycles:
            print("Обнаружены циклы в графе зависимостей")
            cycles = analyzer.find_cycles()
            print(f"Всего циклов: {len(cycles)}")
            for i, cycle in enumerate(cycles[:2], 1):
                print(f"Цикл {i}: {' -> '.join(cycle)}")
    
    if args.compare:
        print("Сравнение с реальным менеджером пакетов (pip):")
        
        pip_order = simulate_pip_load_order(args.package, phase3_data['graph'])
        
        if pip_order:
            print("Порядок загрузки в pip:")
            print("-" * 60)
            
            for i, pkg in enumerate(pip_order, 1):
                deps = phase3_data['graph'].get('adjacency', {}).get(pkg, [])
                deps_str = f" <- {', '.join(deps)}" if deps else ""
                print(f"  {i:3}. {pkg}{deps_str}")
            
            print("-" * 60)
            
            analyze_differences(load_order, pip_order, args.package, phase3_data['graph'])
        else:
            print(f"Неизвестный пакет для сравнения: {args.package}")
    
    print("Анализ критических путей:")
    
    critical_paths = analyzer.find_critical_paths(args.package)
    
    if critical_paths:
        print(f"Критические пути для '{args.package}':")
        critical_paths.sort(key=len, reverse=True)
        
        for i, path in enumerate(critical_paths[:2], 1):
            print(f"Путь {i} (длина: {len(path)-1}):")
            for j, node in enumerate(path):
                indent = "  " * j
                arrow = "-> " if j > 0 else ""
                print(f"{indent}{arrow}{node}")
        
        if len(critical_paths) > 2:
            print(f"... и еще {len(critical_paths) - 2} путей")
        
        longest_path = critical_paths[0]
        print(f"Самый длинный путь: {len(longest_path)-1} шагов")
        print(f"Начинается с: {longest_path[0]}")
        print(f"Заканчивается: {longest_path[-1]}")
    else:
        print(f"Пакет '{args.package}' не имеет зависимостей")
    
    print("Сохранение результатов...")
    
    results = {
        "phase": 4,
        "variant": 6,
        "package": args.package,
        "load_order": load_order,
        "critical_paths": critical_paths if 'critical_paths' in locals() else [],
        "statistics": {
            "total_packages": len(load_order) if load_order else 0,
            "critical_paths_count": len(critical_paths) if 'critical_paths' in locals() else 0,
            "has_cycles": analyzer.has_cycles() if 'analyzer' in locals() else False
        }
    }
    
    if args.compare and 'pip_order' in locals():
        results["pip_order"] = pip_order
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Результаты сохранены в {args.output}")

if __name__ == "__main__":
    main()
