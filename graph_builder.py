"""
Реализация графа зависимостей для этапа 3
BFS с рекурсией, фильтрация, обработка циклов
"""

from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple
import json

class DependencyGraph:
    def __init__(self, config: Dict):
        self.config = config
        self.max_depth = config.get('max_depth', -1)
        self.filter_substring = config.get('filter_substring', '')
        self.nodes: Set[str] = set()
        self.edges: List[Tuple[str, str]] = []
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)
        self.depth_limits: Dict[str, int] = {}
        
    def _apply_filters(self, package_name: str) -> bool:
        """Применение фильтров к имени пакета"""
        if self.filter_substring and self.filter_substring in package_name:
            return True
        return False
    
    def _get_test_dependencies(self, package: str) -> List[str]:
        """Эмуляция получения зависимостей для тестового режима"""
        # Простая эмуляция структуры зависимостей
        mock_data = {
            'A': ['B', 'C', 'D'],
            'B': ['E', 'F'],
            'C': ['G', 'H'],
            'D': ['I', 'J'],
            'E': ['K', 'L'],
            'F': ['M', 'N'],
            'G': ['O', 'P'],
            'H': ['Q', 'R'],
            'I': ['S'],
            'J': ['T', 'U'],
            'K': ['V'],
            'L': ['W'],
            'M': ['X'],
            'N': ['Y'],
            'O': ['Z', 'AA'],
            'P': ['BB'],
            'Q': ['CC'],
            'R': ['DD'],
            'S': ['EE'],
            'T': ['FF'],
            'U': ['GG'],
            'V': ['HH'],
            'W': ['II'],
            'X': ['JJ'],
            'Y': ['KK'],
            'Z': ['LL'],
            'AA': ['MM'],
            'BB': ['NN'],
            'CC': ['OO'],
            'DD': ['PP'],
            'EE': ['QQ'],
            'FF': ['RR'],
            'GG': ['SS'],
            'HH': ['TT'],
            'II': ['UU'],
            'JJ': ['VV'],
            'KK': ['WW'],
            'LL': ['XX'],
            'MM': ['YY'],
            'NN': ['ZZ'],
            'OO': ['TEST1'],
            'PP': ['TEST2']
        }
        return mock_data.get(package, [])
    
    def _get_real_dependencies(self, package: str) -> List[str]:
        """Эмуляция получения зависимостей из реального репозитория"""
        # Эмуляция популярных Python пакетов
        mock_real_data = {
            'requests': ['urllib3', 'certifi', 'chardet', 'idna'],
            'numpy': ['scipy', 'pandas', 'matplotlib'],
            'django': ['sqlparse', 'asgiref', 'pytz'],
            'flask': ['werkzeug', 'jinja2', 'click', 'itsdangerous'],
            'pandas': ['numpy', 'python-dateutil', 'pytz'],
            'matplotlib': ['numpy', 'pillow', 'cycler', 'kiwisolver'],
            'tensorflow': ['numpy', 'scipy', 'absl-py', 'protobuf'],
            'torch': ['numpy', 'typing-extensions'],
            'scikit-learn': ['numpy', 'scipy', 'joblib', 'threadpoolctl'],
            'scipy': ['numpy'],
            'pillow': [],
            'urllib3': ['idna', 'certifi'],
            'certifi': [],
            'chardet': [],
            'idna': [],
            'sqlparse': [],
            'asgiref': [],
            'pytz': [],
            'werkzeug': [],
            'jinja2': ['markupsafe'],
            'click': [],
            'itsdangerous': [],
            'python-dateutil': ['six'],
            'cycler': [],
            'kiwisolver': [],
            'absl-py': [],
            'protobuf': [],
            'typing-extensions': [],
            'joblib': [],
            'threadpoolctl': [],
            'markupsafe': [],
            'six': []
        }
        return mock_real_data.get(package.lower(), [])
    
    def bfs_with_recursion(self, start_package: str, visited: Set = None, 
                          depth: int = 0, parent: str = None) -> None:
        """Рекурсивный BFS для обхода зависимостей"""
        if visited is None:
            visited = set()
        
        # Проверка максимальной глубины
        if self.max_depth > 0 and depth >= self.max_depth:
            return
        
        # Применение фильтров
        if self._apply_filters(start_package):
            return
        
        # Проверка на посещение
        if start_package in visited:
            return
        
        visited.add(start_package)
        self.nodes.add(start_package)
        self.depth_limits[start_package] = depth
        
        # Добавляем ребро от родителя
        if parent:
            self.edges.append((parent, start_package))
            self.adjacency[parent].append(start_package)
            self.reverse_adjacency[start_package].append(parent)
        
        # Получаем зависимости
        dependencies = self._get_real_dependencies(start_package)
        
        for dep in dependencies:
            # Рекурсивный обход
            self.bfs_with_recursion(dep, visited, depth + 1, start_package)
    
    def build_from_real_repo(self, package: str) -> None:
        """Построение графа из реального репозитория"""
        self.bfs_with_recursion(package)
    
    def build_from_test_file(self, filename: str) -> None:
        """Построение графа из тестового файла"""
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    
                    package = parts[0]
                    dependencies = parts[1:]
                    
                    # Фильтрация основного пакета
                    if self._apply_filters(package):
                        continue
                    
                    self.nodes.add(package)
                    
                    for dep in dependencies:
                        # Фильтрация зависимостей
                        if self._apply_filters(dep):
                            continue
                        
                        self.nodes.add(dep)
                        self.edges.append((package, dep))
                        self.adjacency[package].append(dep)
                        self.reverse_adjacency[dep].append(package)
                        
        except FileNotFoundError:
            raise
    
    def detect_cycles(self) -> List[List[str]]:
        """Обнаружение циклических зависимостей"""
        cycles = []
        visited = set()
        recursion_stack = set()
        parent_map = {}
        
        def dfs(current: str, path: List[str]) -> None:
            visited.add(current)
            recursion_stack.add(current)
            
            for neighbor in self.adjacency.get(current, []):
                if neighbor not in visited:
                    parent_map[neighbor] = current
                    dfs(neighbor, path + [neighbor])
                elif neighbor in recursion_stack:
                    # Найден цикл
                    cycle = [neighbor]
                    node = current
                    while node != neighbor:
                        cycle.append(node)
                        node = parent_map.get(node, neighbor)
                    cycle.append(neighbor)
                    cycle.reverse()
                    cycles.append(cycle)
            
            recursion_stack.remove(current)
        
        for node in self.nodes:
            if node not in visited:
                parent_map.clear()
                dfs(node, [node])
        
        return cycles
    
    def print_structure(self, start_node: str, max_levels: int = 3):
        """Печать структуры графа"""
        visited = set()
        
        def print_node(node: str, level: int = 0):
            if level > max_levels or node in visited:
                return
            
            visited.add(node)
            prefix = "  " * level
            print(f"{prefix}├─ {node}")
            
            deps = self.adjacency.get(node, [])
            for dep in deps:
                print_node(dep, level + 1)
        
        print_node(start_node)
