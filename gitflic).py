import urllib.request
import json

def get_package_dependencies(package_name, repo_url):
    """Получает прямые зависимости пакета из PyPI репозитория"""
    try:
        # Формируем URL для получения информации о пакете
        url = f"{repo_url}/{package_name}/json"
        
        # Отправляем запрос к PyPI API
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            # Извлекаем информацию о зависимостях
            requires_dist = data.get('info', {}).get('requires_dist', [])
            return requires_dist
            
    except Exception as e:
        print(f"Ошибка при получении зависимостей: {e}")
        return []

def main():
    # Чтение конфигурации из config.yaml
    config = {}
    with open("config2.yaml", "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                config[key.strip()] = value.strip().strip('"\'')
    
    # Получение параметров
    package = config.get('package', '')
    repo_url = config.get('repository', 'https://pypi.org/pypi')
    
    if not package:
        print("Ошибка: Не указано имя пакета в конфигурации")
        return
    
    print(f"Прямые зависимости пакета '{package}':")
    dependencies = get_package_dependencies(package, repo_url)
    
    if dependencies:
        for dep in dependencies:
            print(f" - {dep}")
    else:
        print("Зависимости не найдены или пакет не существует")

if __name__ == "__main__":
    main()
