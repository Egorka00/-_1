import unittest
import tempfile
import os
from parser import ConfigParser
from compiler import XMLCompiler

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser()
    
    def test_simple_dict(self):
        text = """app {
    name = [[Test App]],
    version = 1.0
}"""
        result = self.parser.parse(text)
        self.assertIsNotNone(result)
        self.assertEqual(len(result["configs"]), 1)
    
    def test_constants(self):
        text = """var maxUsers 100;
config {
    limit = §maxUsers 50 +§
}"""
        result = self.parser.parse(text)
        self.assertIsNotNone(result)
        # Проверяем, что константа запомнилась
        self.assertIn("maxUsers", result["constants"])
    
    def test_array(self):
        text = """data {
    values = #( 1 2.5 3 )
}"""
        result = self.parser.parse(text)
        self.assertIsNotNone(result)
    
    def test_nested_dict(self):
        text = """server {
    settings = {
        port = 8080,
        host = [[localhost]]
    }
}"""
        result = self.parser.parse(text)
        self.assertIsNotNone(result)

class TestXMLCompiler(unittest.TestCase):
    def test_simple_to_xml(self):
        data = {
            "configs": [{
                "type": "dict",
                "name": "app",
                "pairs": [("name", "Test"), ("version", 1.0)]
            }]
        }
        xml = XMLCompiler.to_xml(data)
        self.assertIn("<app>", xml)
        self.assertIn("<name>Test</name>", xml)

class TestIntegration(unittest.TestCase):
    def test_file_processing(self):
        # Создаём временный файл с конфигурацией
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write("""app {
    name = [[Integration Test]]
}""")
            temp_file = f.name
        
        try:
            # Имитируем запуск CLI
            import subprocess
            result = subprocess.run(
                ['python', 'cli.py', '-i', temp_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("<app>", result.stdout)
        finally:
            os.unlink(temp_file)

if __name__ == '__main__':
    unittest.main()
