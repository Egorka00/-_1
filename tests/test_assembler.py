"""
Тесты для ассемблера УВМ (Вариант 6)
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from assembler import Assembler
from parser import Parser
from encoder import Encoder


class TestParser(unittest.TestCase):
    """Тесты парсера"""
    
    def setUp(self):
        self.parser = Parser()
    
    def test_parse_load(self):
        """Тест парсинга команды LOAD"""
        source = "LOAD 63"
        commands = self.parser.parse(source)
        
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].mnemonic, 'LOAD')
        self.assertEqual(commands[0].args, [63])
        self.assertEqual(commands[0].size, 5)
    
    def test_parse_read(self):
        """Тест парсинга команды READ"""
        source = "READ 102"
        commands = self.parser.parse(source)
        
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].mnemonic, 'READ')
        self.assertEqual(commands[0].args, [102])
        self.assertEqual(commands[0].size, 2)
    
    def test_parse_store(self):
        """Тест парсинга команды STORE"""
        source = "STORE 120"
        commands = self.parser.parse(source)
        
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].mnemonic, 'STORE')
        self.assertEqual(commands[0].args, [120])
        self.assertEqual(commands[0].size, 3)
    
    def test_parse_bitrev(self):
        """Тест парсинга команды BITREV"""
        source = "BITREV 88"
        commands = self.parser.parse(source)
        
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].mnemonic, 'BITREV')
        self.assertEqual(commands[0].args, [88])
        self.assertEqual(commands[0].size, 3)
    
    def test_parse_multiple(self):
        """Тест парсинга нескольких команд"""
        source = """
        LOAD 100
        READ 50
        STORE 200
        BITREV 75
        """
        
        commands = self.parser.parse(source)
        self.assertEqual(len(commands), 4)
        self.assertEqual(commands[0].mnemonic, 'LOAD')
        self.assertEqual(commands[1].mnemonic, 'READ')
        self.assertEqual(commands[2].mnemonic, 'STORE')
        self.assertEqual(commands[3].mnemonic, 'BITREV')
    
    def test_parse_with_comments(self):
        """Тест парсинга с комментариями"""
        source = """
        LOAD 63    ; Загрузка константы
        READ 102   ; Чтение из памяти
        ; Комментарий на отдельной строке
        STORE 120  ; Запись в память
        """
        
        commands = self.parser.parse(source)
        self.assertEqual(len(commands), 3)
    
    def test_parse_with_labels(self):
        """Тест парсинга с метками"""
        source = """
        START:
            LOAD 100
        LOOP:
            READ 50
            BITREV 75
        """
        
        commands = self.parser.parse(source)
        self.assertEqual(len(commands), 3)
    
    def test_parse_invalid_mnemonic(self):
        """Тест обработки неверной мнемоники"""
        source = "INVALID 123"
        
        with self.assertRaises(ValueError):
            self.parser.parse(source)
    
    def test_parse_wrong_arg_count(self):
        """Тест обработки неверного количества аргументов"""
        source = "LOAD 1 2 3"
        
        with self.assertRaises(ValueError):
            self.parser.parse(source)


class TestEncoder(unittest.TestCase):
    """Тесты кодировщика"""
    
    def setUp(self):
        self.encoder = Encoder()
    
    def test_encode_load(self):
        """Тест кодирования LOAD 63"""
        from parser import Command
        
        cmd = Command(
            opcode=6,
            mnemonic='LOAD',
            args=[63],
            size=5,
            line_num=1,
            source='LOAD 63'
        )
        
        result = self.encoder._encode_command(cmd)
        expected = bytes([0xFE, 0x01, 0x00, 0x00, 0x00])
        
        self.assertEqual(result, expected)
    
    def test_encode_read(self):
        """Тест кодирования READ 102"""
        from parser import Command
        
        cmd = Command(
            opcode=3,
            mnemonic='READ',
            args=[102],
            size=2,
            line_num=1,
            source='READ 102'
        )
        
        result = self.encoder._encode_command(cmd)
        expected = bytes([0x33, 0x03])
        
        self.assertEqual(result, expected)
    
    def test_encode_store(self):
        """Тест кодирования STORE 120"""
        from parser import Command
        
        cmd = Command(
            opcode=2,
            mnemonic='STORE',
            args=[120],
            size=3,
            line_num=1,
            source='STORE 120'
        )
        
        result = self.encoder._encode_command(cmd)
        expected = bytes([0xC2, 0x03, 0x00])
        
        self.assertEqual(result, expected)
    
    def test_encode_bitrev(self):
        """Тест кодирования BITREV 88"""
        from parser import Command
        
        cmd = Command(
            opcode=1,
            mnemonic='BITREV',
            args=[88],
            size=3,
            line_num=1,
            source='BITREV 88'
        )
        
        result = self.encoder._encode_command(cmd)
        expected = bytes([0xC1, 0x02, 0x00])
        
        self.assertEqual(result, expected)
    
    def test_encode_multiple(self):
        """Тест кодирования нескольких команд"""
        from parser import Command
        
        commands = [
            Command(6, 'LOAD', [63], 5, 1, 'LOAD 63'),
            Command(3, 'READ', [102], 2, 2, 'READ 102'),
            Command(2, 'STORE', [120], 3, 3, 'STORE 120'),
            Command(1, 'BITREV', [88], 3, 4, 'BITREV 88'),
        ]
        
        result = self.encoder.encode(commands)
        expected = bytes([
            0xFE, 0x01, 0x00, 0x00, 0x00,  # LOAD 63
            0x33, 0x03,                     # READ 102
            0xC2, 0x03, 0x00,               # STORE 120
            0xC1, 0x02, 0x00                # BITREV 88
        ])
        
        self.assertEqual(result, expected)


class TestAssemblerIntegration(unittest.TestCase):
    """Интеграционные тесты ассемблера"""
    
    def setUp(self):
        self.assembler = Assembler()
    
    def test_full_assembly(self):
        """Тест полного цикла ассемблирования"""
        source_code = """LOAD 63
READ 102
STORE 120
BITREV 88"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False) as src:
            src.write(source_code)
            src_path = Path(src.name)
        
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as out:
            out_path = Path(out.name)
        
        try:
            # Ассемблирование
            _, binary = self.assembler.assemble(src_path, out_path)
            
            # Проверка результата
            expected = bytes([
                0xFE, 0x01, 0x00, 0x00, 0x00,
                0x33, 0x03,
                0xC2, 0x03, 0x00,
                0xC1, 0x02, 0x00
            ])
            
            self.assertEqual(binary, expected)
            
            # Проверка сохранения файла
            self.assertTrue(out_path.exists())
            self.assertEqual(out_path.stat().st_size, len(expected))
            
        finally:
            # Очистка
            os.unlink(src_path)
            os.unlink(out_path)
    
    def test_assembly_with_test_mode(self):
        """Тест ассемблирования в режиме тестирования"""
        source_code = "LOAD 63\nREAD 102"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False) as src:
            src.write(source_code)
            src_path = Path(src.name)
        
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as out:
            out_path = Path(out.name)
        
        try:
            # Запуск с тестовым режимом (проверяем, что не падает)
            self.assembler.assemble(src_path, out_path, test_mode=True)
            
            # Проверка создания файла
            self.assertTrue(out_path.exists())
            
        finally:
            os.unlink(src_path)
            os.unlink(out_path)


class TestSpecificationExamples(unittest.TestCase):
    """Тесты примеров из спецификации УВМ"""
    
    def test_specification_test_cases(self):
        """Проверка всех тестовых случаев из спецификации"""
        test_cases = [
            ('LOAD 63', bytes([0xFE, 0x01, 0x00, 0x00, 0x00])),
            ('READ 102', bytes([0x33, 0x03])),
            ('STORE 120', bytes([0xC2, 0x03, 0x00])),
            ('BITREV 88', bytes([0xC1, 0x02, 0x00])),
        ]
        
        assembler = Assembler()
        
        for source, expected in test_cases:
            with self.subTest(source=source):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False) as src:
                    src.write(source)
                    src_path = Path(src.name)
                
                with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as out:
                    out_path = Path(out.name)
                
                try:
                    _, binary = assembler.assemble(src_path, out_path)
                    self.assertEqual(binary, expected, 
                                   f"Неверное кодирование для: {source}")
                finally:
                    os.unlink(src_path)
                    os.unlink(out_path)


if __name__ == '__main__':
    unittest.main()
