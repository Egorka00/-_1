#!/usr/bin/env python3
"""
Модуль визуализации графа зависимостей
"""

import os
import subprocess
import tempfile
from datetime import datetime
from collections import deque

class GraphVisualizer:
    def __init__(self, config):
        self.config = config
        self.output_image = config.get('output_image', 'graph.svg')
        
    def generate_d2(self, package, graph_structure, phase4_data):
        """Генерация D2 кода для графа"""
        
        adjacency = graph_structure.get('adjacency', {})
        levels = phase4_data.get('levels', {})
        load_order = phase4_data.get('load_order', [])
        
        d2_lines = []
        
        # Заголовок
        d2_lines.append("# Dependency Graph")
        d2_lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        d2_lines.append(f"# Package: {package}")
        d2_lines.append("")
        
        # Настройки
        d2_lines.append("direction: down")
        d2_lines.append("")
        
        # Основной пакет
        d2_lines.append(f"{package}: {{")
        d2_lines.append(f"  style.fill: lightgreen")
        d2_lines.append(f"  style.stroke: darkgreen")
        d2_lines.append(f"  style.stroke-width: 3")
        d2_lines.append(f"  label: \"{package} (main)\"")
        d2_lines.append("}")
        d2_lines.append("")
        
        # Все узлы
        all_nodes = set()
        for node in adjacency:
            all_nodes.add(node)
            for dep in adjacency[node]:
                all_nodes.add(dep)
        
        for node in sorted(all_nodes):
            if node == package:
                continue
            
            level = levels.get(node, 0)
            if level == 0:
                color = "lightyellow"
            elif level == 1:
                color = "lightpink"
            else:
                color = "lavender"
            
            d2_lines.append(f"{node}: {{")
            d2_lines.append(f"  style.fill: {color}")
            
            if node in load_order:
                index = load_order.index(node) + 1
                d2_lines.append(f"  label: \"{node} ({index})\"")
            
            d2_lines.append("}")
        
        d2_lines.append("")
        
        # Зависимости
        d2_lines.append("# Dependencies")
        for node in adjacency:
            for dep in adjacency[node]:
                d2_lines.append(f"{node} -> {dep}")
        
        return "\n".join(d2_lines)
    
    def generate_d2_simple(self, package, adjacency):
        """Простая версия для демонстрации"""
        d2_lines = []
        d2_lines.append(f"direction: down")
        d2_lines.append("")
        
        d2_lines.append(f"{package}: {{")
        d2_lines.append(f"  style.fill: lightgreen")
        d2_lines.append("}")
        
        if package in adjacency:
            for dep in adjacency[package]:
                d2_lines.append(f"{dep}: {{")
                d2_lines.append(f"  style.fill: lightblue")
                d2_lines.append("}")
                d2_lines.append(f"{package} -> {dep}")
        
        return "\n".join(d2_lines)
    
    def save_svg(self, package, graph_structure, phase4_data):
        """Сохранение графа в SVG"""
        
        try:
            # Используем Graphviz как основной вариант
            return self._save_with_graphviz(package, graph_structure, phase4_data)
                
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
            return False
    
    def _save_with_graphviz(self, package, graph_structure, phase4_data):
        """Использование Graphviz"""
        try:
            from graphviz import Digraph
            
            dot = Digraph(comment='Dependency Graph', format='svg')
            dot.attr(rankdir='TB')
            
            adjacency = graph_structure.get('adjacency', {})
            levels = phase4_data.get('levels', {})
            
            # Добавляем узлы
            all_nodes = set()
            for node in adjacency:
                all_nodes.add(node)
                for dep in adjacency[node]:
                    all_nodes.add(dep)
            
            # Добавляем основной пакет
            dot.node(package, style='filled', fillcolor='lightgreen')
            
            # Добавляем остальные узлы
            for node in all_nodes:
                if node != package:
                    level = levels.get(node, 0)
                    if level == 0:
                        dot.node(node, style='filled', fillcolor='lightyellow')
                    elif level == 1:
                        dot.node(node, style='filled', fillcolor='lightpink')
                    else:
                        dot.node(node, style='filled', fillcolor='lavender')
            
            # Добавляем рёбра
            for node in adjacency:
                for dep in adjacency[node]:
                    dot.edge(node, dep)
            
            # Сохраняем
            base_name = os.path.splitext(self.output_image)[0]
            dot.render(base_name, cleanup=True)
            
            print(f"Создано с помощью Graphviz: {self.output_image}")
            return True
            
        except ImportError:
            print("Graphviz не установлен. Установите: pip install graphviz")
            return False
    
    def save_svg_simple(self, package, adjacency):
        """Простая версия сохранения"""
        try:
            from graphviz import Digraph
            
            dot = Digraph(format='svg')
            dot.node(package, style='filled', fillcolor='lightgreen')
            
            if package in adjacency:
                for dep in adjacency[package]:
                    dot.node(dep, style='filled', fillcolor='lightblue')
                    dot.edge(package, dep)
            
            dot.render(f'demo_{package}', cleanup=True)
            return True
        except:
            return False
    
    def generate_ascii_tree(self, package, graph_structure, max_depth=10):
        """Генерация ASCII-дерева с защитой от циклов"""
        adjacency = graph_structure.get('adjacency', {})
        
        result = []
        visited_in_path = set()
        
        def build_tree(node, prefix="", is_last=True, depth=0):
            if depth > max_depth:
                result.append(f"{prefix}{'└── ' if is_last else '├── '}...")
                return
            
            if node in visited_in_path:
                result.append(f"{prefix}{'└── ' if is_last else '├── '}{node} (цикл)")
                return
            
            visited_in_path.add(node)
            
            if prefix:
                connector = '└── ' if is_last else '├── '
                result.append(f"{prefix}{connector}{node}")
                new_prefix = prefix + ("    " if is_last else "│   ")
            else:
                result.append(f"{node}")
                new_prefix = ""
            
            deps = adjacency.get(node, [])
            sorted_deps = sorted(deps)
            
            for i, dep in enumerate(sorted_deps):
                is_last_dep = (i == len(sorted_deps) - 1)
                build_tree(dep, new_prefix, is_last_dep, depth + 1)
            
            visited_in_path.remove(node)
        
        build_tree(package)
        return "\n".join(result)
    
    def generate_ascii_tree_simple(self, package, adjacency):
        """Простая версия ASCII-дерева (без рекурсии)"""
        result = []
        
        # Используем BFS для обхода
        visited = set()
        queue = deque([(package, 0, [])])  # (node, level, path)
        
        while queue:
            current, level, path = queue.popleft()
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Строим отступ
            line_parts = []
            for i in range(level):
                if i == level - 1:
                    line_parts.append("└── " if i == level - 1 else "├── ")
                else:
                    line_parts.append("    " if path[i] else "│   ")
            
            line = "".join(line_parts) + current
            result.append(line)
            
            # Добавляем зависимости
            deps = adjacency.get(current, [])
            for i, dep in enumerate(sorted(deps)):
                is_last = (i == len(deps) - 1)
                new_path = path + [is_last]
                queue.append((dep, level + 1, new_path))
        
        return "\n".join(result)
