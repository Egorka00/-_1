class XMLCompiler:
    @staticmethod
    def to_xml(data, root_name="config"):
        """Преобразует структуру данных в XML"""
        if not data or "configs" not in data:
            return ""
        
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        
        for config in data["configs"]:
            if config["type"] == "dict":
                xml_parts.append(XMLCompiler._dict_to_xml(config))
        
        return "\n".join(xml_parts)
    
    @staticmethod
    def _dict_to_xml(dict_obj, level=0):
        """Рекурсивно преобразует словарь в XML"""
        indent = "  " * level
        name = dict_obj["name"]
        
        lines = [f"{indent}<{name}>"]
        
        for key, value in dict_obj["pairs"]:
            if isinstance(value, dict):
                if value["type"] == "dict":
                    lines.append(XMLCompiler._dict_to_xml(value, level + 1))
                elif value["type"] == "array":
                    lines.append(XMLCompiler._array_to_xml(key, value, level + 1))
            elif isinstance(value, (int, float)):
                lines.append(f"{indent}  <{key}>{value}</{key}>")
            else:  # строка
                lines.append(f"{indent}  <{key}>{value}</{key}>")
        
        lines.append(f"{indent}</{name}>")
        return "\n".join(lines)
    
    @staticmethod
    def _array_to_xml(name, array_obj, level=0):
        """Преобразует массив в XML"""
        indent = "  " * level
        lines = [f"{indent}<{name}>"]
        
        for value in array_obj["values"]:
            if isinstance(value, dict) and value["type"] == "dict":
                lines.append(XMLCompiler._dict_to_xml(value, level + 1))
            else:
                lines.append(f"{indent}  <item>{value}</item>")
        
        lines.append(f"{indent}</{name}>")
        return "\n".join(lines)
