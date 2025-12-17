"""
Кодировщик промежуточного представления в бинарный формат УВМ (Вариант 6)
Этап 2: Формирование машинного кода
"""

from typing import List, Tuple
from src.parser import Command


class Encoder:
    """Кодировщик команд в бинарный формат УВМ"""
    
    def __init__(self):
        self.commands_encoded = 0
        self.total_bytes = 0
    
    def encode(self, commands: List[Command]) -> bytes:
        """Кодирование списка команд в байты"""
        
        binary_data = bytearray()
        self.commands_encoded = 0
        
        for cmd in commands:
            cmd_bytes = self._encode_command(cmd)
            binary_data.extend(cmd_bytes)
            self.commands_encoded += 1
        
        self.total_bytes = len(binary_data)
        return bytes(binary_data)
    
    def _encode_command(self, cmd: Command) -> bytes:
        """Кодирование одной команды"""
        
        if cmd.mnemonic == 'LOAD':
            return self._encode_load(cmd)
        elif cmd.mnemonic == 'READ':
            return self._encode_read(cmd)
        elif cmd.mnemonic == 'STORE':
            return self._encode_store(cmd)
        elif cmd.mnemonic == 'BITREV':
            return self._encode_bitrev(cmd)
        else:
            raise ValueError(f"Неизвестная команда для кодирования: {cmd.mnemonic}")
    
    def _encode_load(self, cmd: Command) -> bytes:
        """
        Кодирование команды LOAD
        Формат: A=6 (биты 0-2), B=константа (биты 3-33)
        Размер: 5 байт (40 бит)
        """
        constant = cmd.args[0]
        
        # Объединяем: (B << 3) | A
        # A=6 (0b110)
        value = (constant << 3) | 6
        
        # Преобразуем в 5 байт (little-endian)
        result = bytearray(5)
        for i in range(5):
            result[i] = (value >> (8 * i)) & 0xFF
        
        return bytes(result)
    
    def _encode_read(self, cmd: Command) -> bytes:
        """
        Кодирование команды READ
        Формат: A=3 (биты 0-2), B=смещение (биты 3-10)
        Размер: 2 байта (16 бит)
        """
        offset = cmd.args[0]
        
        # Объединяем: (B << 3) | A
        # A=3 (0b011)
        value = (offset << 3) | 3
        
        # 2 байта, little-endian
        return bytes([value & 0xFF, (value >> 8) & 0xFF])
    
    def _encode_store(self, cmd: Command) -> bytes:
        """
        Кодирование команды STORE
        Формат: A=2 (биты 0-2), B=адрес (биты 3-22)
        Размер: 3 байта (24 бит)
        """
        address = cmd.args[0]
        
        # Объединяем: (B << 3) | A
        # A=2 (0b010)
        value = (address << 3) | 2
        
        # 3 байта, little-endian
        result = bytearray(3)
        for i in range(3):
            result[i] = (value >> (8 * i)) & 0xFF
        
        return bytes(result)
    
    def _encode_bitrev(self, cmd: Command) -> bytes:
        """
        Кодирование команды BITREV
        Формат: A=1 (биты 0-2), B=адрес (биты 3-22)
        Размер: 3 байта (24 бит)
        """
        address = cmd.args[0]
        
        # Объединяем: (B << 3) | A
        # A=1 (0b001)
        value = (address << 3) | 1
        
        # 3 байта, little-endian
        result = bytearray(3)
        for i in range(3):
            result[i] = (value >> (8 * i)) & 0xFF
        
        return bytes(result)
    
    def get_stats(self) -> Tuple[int, int]:
        """Получить статистику кодирования"""
        return self.commands_encoded, self.total_bytes
    
    def run_tests(self) -> None:
        """Запуск тестов кодирования (соответствует спецификации УВМ)"""
        
        print("=" * 60)
        print("ТЕСТИРОВАНИЕ КОДИРОВАНИЯ (по спецификации УВМ)")
        print("=" * 60)
        
        from src.parser import Command
        
        test_cases = [
            {
                'name': 'LOAD 63',
                'cmd': Command(opcode=6, mnemonic='LOAD', args=[63], 
                             size=5, line_num=1, raw_line='LOAD 63'),
                'expected': bytes([0xFE, 0x01, 0x00, 0x00, 0x00])
            },
            {
                'name': 'READ 102',
                'cmd': Command(opcode=3, mnemonic='READ', args=[102], 
                             size=2, line_num=1, raw_line='READ 102'),
                'expected': bytes([0x33, 0x03])
            },
            {
                'name': 'STORE 120',
                'cmd': Command(opcode=2, mnemonic='STORE', args=[120], 
                             size=3, line_num=1, raw_line='STORE 120'),
                'expected': bytes([0xC2, 0x03, 0x00])
            },
            {
                'name': 'BITREV 88',
                'cmd': Command(opcode=1, mnemonic='BITREV', args=[88], 
                             size=3, line_num=1, raw_line='BITREV 88'),
                'expected': bytes([0xC1, 0x02, 0x00])
            },
        ]
        
        all_passed = True
        
        for test in test_cases:
            try:
                result = self._encode_command(test['cmd'])
                hex_result = ' '.join(f'0x{b:02X}' for b in result)
                hex_expected = ' '.join(f'0x{b:02X}' for b in test['expected'])
                
                if result == test['expected']:
                    print(f"✓ {test['name']:15} -> {hex_result}")
                else:
                    print(f"✗ {test['name']:15}")
                    print(f"  Ожидалось: {hex_expected}")
                    print(f"  Получено:  {hex_result}")
                    all_passed = False
                    
            except Exception as e:
                print(f"✗ {test['name']:15} - Ошибка: {e}")
                all_passed = False
        
        if all_passed:
            print("\n✅ Все тесты пройдены успешно!")
        else:
            print("\n❌ Некоторые тесты не пройдены")
        
        print("=" * 60)
        return all_passed


# Для запуска тестов напрямую
if __name__ == "__main__":
    encoder = Encoder()
    encoder.run_tests()
