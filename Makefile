.PHONY: test run clean

# Переменные
PYTHON = python3
SRC_DIR = src
TEST_DIR = tests
EXAMPLES_DIR = examples

# Основные цели
test:
	cd $(TEST_DIR) && $(PYTHON) -m pytest test_assembler.py -v

run:
	$(PYTHON) $(SRC_DIR)/assembler.py $(EXAMPLES_DIR)/test.asm output.bin --test

test-encoder:
	$(PYTHON) -c "from src.encoder import Encoder; e = Encoder(); e.test_encoding()"

clean:
	rm -f output.bin
	rm -rf __pycache__ */__pycache__ */*.pyc
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Для быстрого тестирования
quick: clean test run

# Показать help
help:
	@echo "Доступные команды:"
	@echo "  make test      - запустить все тесты"
	@echo "  make run       - запустить ассемблер с примером"
	@echo "  make test-encoder - протестировать только кодировщик"
	@echo "  make clean     - очистить проект"
	@echo "  make quick     - очистить, запустить тесты и пример"
	@echo "  make help      - показать эту справку"
