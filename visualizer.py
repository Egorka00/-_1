#!/usr/bin/env python3
"""
Модуль визуализации графа зависимостей
Вариант №6: D2 диаграммы, SVG, ASCII-дерево
"""

import os
import subprocess
import tempfile
from datetime import datetime

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
        
        # Стили узлов по уровням
        d2_lines.append("styles: {")
        d2_lines.append("  node: {")
        d2_lines.append("    style: {")
        d2_lines.append("      fill: lightblue")
        d2_lines.append("      stroke: darkblue")
        d2_lines.append("      stroke-width: 2")
        d2_lines.append("    }")
        d2_lines.append("  }")
        d2_lines.append("}")
        d2_lines.append("")
        
        # Основной пакет
        d2_lines.append(f"{package}: {{")
        d2_lines.append(f"  style.fill: lightgreen")
        d2_lines.append(f"  style.stroke: darkgreen")
        d2_lines.append(f"  style.stroke-width: 3")
        d2_lines.append(f"  label: \"{package} (main)\"")
        d2_lines.append("}")
        d2_lines.append("")
        
        # Все узлы с уровнями
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
        
        # Группировка по уровням
        d2_lines.append("")
        d2_lines.append("# Group by levels")
        
        max_level = max(levels.values()) if levels else 0
        for level in range(max_level + 1):
            nodes_in_level = [n for n, l in levels.items() if l == level]
            if nodes_in_level:
                d2_lines.append(f"level_{level}: {{")
                d2_lines.append(f"  shape: rectangle")
                d2_lines.append(f"  style.stroke-dash: 3")
                d2_lines.append(f"  style.fill: transparent")
                d2_lines.append(f"  label: \"Level {level}\"")
                d2_lines.append("}")
                
                for node in nodes_in_level:
                    d2_lines.append(f"{node}: {{")
                    d2_lines.append(f"  container: level_{level}")
                    d2_lines.append("}")
        
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
        """Сохранение графа в SVG с помощью D2"""
        
        try:
            # Проверяем наличие D2
            result = subprocess.run(['d2', '--version'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            
            if result.returncode != 0:
                print("D2 не установлен. Используем Graphviz как fallback.")
                return self._save_with_graphviz(package, graph_structure, phase4_data)
            
            # Генерируем D2 код
            d2_code = self.generate_d2(package, graph_structure, phase4_data)
            
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as tmp:
                tmp.write(d2_code)
                d2_file = tmp.name
            
            # Конвертируем в SVG
            svg_file = self.output_image
            cmd = ['d2', d2_file, svg_file]
            
            print(f"Выполняю: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Удаляем временный файл
            try:
                os.unlink(d2_file)
            except:
                pass
            
            if result.returncode == 0:
                return True
            else:
                print(f"Ошибка D2: {result.stderr}")
                return self._save_with_graphviz(package, graph_structure, phase4_data)
                
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"Ошибка при использовании D2: {e}")
            return self._save_with_graphviz(package, graph_structure, phase4_data)
    
    def _save_with_graphviz(self, package, graph_structure, phase4_data):
        """Fallback: использование Graphviz"""
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
            
            for node in all_nodes:
                if node == package:
                    dot.node(node, style='filled', fillcolor='lightgreen')
                else:
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
    
    def generate_ascii_tree(self, package, graph_structure):
        """Генерация ASCII-дерева"""
        adjacency = graph_structure.get('adjacency', {})
        
        result = []
        visited = set()
        
        def build_tree(node, prefix="", is_last=True):
            if node in visited:
                result.append(f"{prefix}{'└── ' if is_last else '├── '}{node} (цикл)")
                return
            
            visited.add(node)
            
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
                build_tree(dep, new_prefix, is_last_dep)
        
        build_tree(package)
        return "\n".join(result)
    
    def generate_ascii_tree_simple(self, package, adjacency):
        """Простая версия ASCII-дерева"""
        result = []
        
        result.append(package)
        if package in adjacency:
            for i, dep in enumerate(adjacency[package]):
                if i == len(adjacency[package]) - 1:
                    result.append(f"└── {dep}")
                else:
                    result.append(f"├── {dep}")
        
        return "\n".join(result)
