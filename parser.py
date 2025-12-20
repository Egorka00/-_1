from lark import Lark, Transformer
from lark.exceptions import LarkError
import json

class ConfigParser:
    def __init__(self):
        # Загружаем грамматику из файла
        with open('grammar.lark', 'r', encoding='utf-8') as f:
            grammar = f.read()
        
        self.parser = Lark(
            grammar,
            start='start',
            parser='lalr',
            propagate_positions=True
        )
        self.transformer = ConfigTransformer()
    
    def parse(self, text):
        """Разбирает текст и возвращает структуру данных"""
        try:
            tree = self.parser.parse(text)
            result = self.transformer.transform(tree)
            return result
        except LarkError as e:
            print(f"Ошибка разбора: {e}")
            return None

class ConfigTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.constants = {}
    
    # Константы
    def constant_decl(self, items):
        name = str(items[0])
        value = items[1]
        self.constants[name] = value
        return {"type": "constant", "name": name, "value": value}
    
    # Словари
    def dictionary(self, items):
        name = str(items[0])
        pairs = items[1:]
        return {"type": "dict", "name": name, "pairs": pairs}
    
    # Пары ключ-значение
    def pair(self, items):
        key = str(items[0])
        value = items[1]
        return (key, value)
    
    # Значения
    def number(self, items):
        return float(items[0]) if '.' in str(items[0]) else int(items[0])
    
    def string(self, items):
        text = str(items[0])
        return text[2:-2]  # Убираем [[ и ]]
    
    def array(self, items):
        return {"type": "array", "values": items}
    
    # Выражения
    def constant_expr(self, items):
        return {"type": "expr", "value": items[0]}
    
    def expr(self, items):
        # Простая обработка: a b + -> a + b
        if len(items) == 3:  # a b +
            a = self._get_value(items[0])
            b = self._get_value(items[1])
            op = str(items[2])
            
            if op == '+':
                return a + b
            elif op == '-':
                return a - b
        return self._get_value(items[0])
    
    def _get_value(self, item):
        """Получает значение: либо число, либо значение константы"""
        if isinstance(item, (int, float)):
            return item
        elif isinstance(item, str):
            # Если это имя константы
            return self.constants.get(item, item)
        return item
    
    # Корневой элемент
    def start(self, items):
        return {
            "constants": self.constants,
            "configs": [item for item in items if item and item.get("type") != "constant"]
        }

# Создаём глобальный парсер
parser = ConfigParser()
