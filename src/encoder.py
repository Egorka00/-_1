"""
Кодировщик для УВМ (Вариант 6)
"""

from typing import List
from .parser import Command


class Encoder:
    """Кодировщик промежуточного представления в бинарный формат"""
    
    def encode(self, commands: List[Command]) -> bytes:
        """
        Кодирование списка команд
        
        Args:
            commands: список команд в промежуточном представлении
            
        Returns:
            Байтовая последовательность
        """
        binary_data = bytearray()
        
        for cmd in commands:
            cmd_bytes = self._encode_command(cmd)
            binary_data.extend(cmd_bytes)
        
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
            raise ValueError(f"Неизвестная команда: {cmd.mnemonic}")
    
    def _encode_load(self, cmd: Command) -> bytes:
        """Кодирование LOAD: A=6, B=константа"""
        constant = cmd.args[0]
        
        # Объединение: (B << 3) | A
        value = (constant << 3) | 6
        
        # 5 байт, little-endian
        return value.to_bytes(5, 'little')
    
    def _encode_read(self, cmd: Command) -> bytes:
        """Кодирование READ: A=3, B=смещение"""
        offset = cmd.args[0]
        
        # Объединение: (B << 3) | A
        value = (offset << 3) | 3
        
        # 2 байта, little-endian
        return value.to_bytes(2, 'little')
    
    def _encode_store(self, cmd: Command) -> bytes:
        """Кодирование STORE: A=2, B=адрес"""
        address = cmd.args[0]
        
        # Объединение: (B << 3) | A
        value = (address << 3) | 2
        
        # 3 байта, little-endian
        return value.to_bytes(3, 'little')
    
    def _encode_bitrev(self, cmd: Command) -> bytes:
        """Кодирование BITREV: A=1, B=адрес"""
        address = cmd.args[0]
        
        # Объединение: (B << 3) | A
        value = (address << 3) | 1
        
        # 3 байта, little-endian
        return value.to_bytes(3, 'little')
    
    def test_encoding(self):
        """Тестирование кодирования согласно спецификации"""
        print("Тестирование кодирования команд УВМ (Вариант 6)")
        print("=" * 50)
        
        test_cases = [
            ('LOAD', [63], bytes([0xFE, 0x01, 0x00, 0x00, 0x00])),
            ('READ', [102], bytes([0x33, 0x03])),
            ('STORE', [120], bytes([0xC2, 0x03, 0x00])),
            ('BITREV', [88], bytes([0xC1, 0x02, 0x00])),
        ]
        
        all_pass = True
        
        for mnemonic, args, expected in test_cases:
            # Создаем mock-команду
            cmd = Command(
                opcode={'LOAD': 6, 'READ': 3, 'STORE': 2, 'BITREV': 1}[mnemonic],
                mnemonic=mnemonic,
                args=args,
                size=len(expected),
                line_num=0,
                source=f"{mnemonic} {args[0]}"
            )
            
            result = self._encode_command(cmd)
            
            if result == expected:
                print(f"✓ {mnemonic:8} {args}: OK")
            else:
                print(f"✗ {mnemonic:8} {args}: FAIL")
                print(f"  Ожидалось: {expected.hex(' ', 1)}")
                print(f"  Получено:  {result.hex(' ', 1)}")
                all_pass = False
        
        print("=" * 50)
        if all_pass:
            print("✅ Все тесты пройдены успешно!")
        else:
            print("❌ Некоторые тесты не пройдены")
        
        return all_pass


if __name__ == '__main__':
    encoder = Encoder()
    encoder.test_encoding()
