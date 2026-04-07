.PHONY: help install install-dev test test-verbose uninstall clean lint format

help:
	@echo "SnipBox - Terminator Snippet Manager - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install the plugin using the shell script"
	@echo "  make install-dev      Install for development (editable mode)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run test suite"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo ""
	@echo "Cleanup:"
	@echo "  make uninstall        Remove the installed plugin"
	@echo "  make clean            Remove build artifacts and cache"
	@echo ""
	@echo "Code quality:"
	@echo "  make lint             Check code style with pylint"
	@echo "  make format           Auto-format code with autopep8"

install:
	@echo "Installing Terminator Snippets Plugin..."
	bash install.sh

install-dev:
	@echo "Installing for development..."
	pip install -e .

test:
	@echo "Running test suite..."
	python3 test_snipbox.py

test-verbose:
	@echo "Running tests with verbose output..."
	python3 -m pytest test_snipbox.py -v 2>/dev/null || python3 test_snipbox.py

uninstall:
	@echo "Removing SnipBox plugin..."
	rm -f ~/.config/terminator/plugins/snipbox.py
	@echo "Removed plugin file"
	@echo "Please manually remove 'SnipBoxPlugin' from enabled_plugins in ~/.config/terminator/config"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -f .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete"

lint:
	@echo "Checking code style..."
	@which pylint > /dev/null || (echo "pylint not installed. Install with: pip install pylint"; exit 1)
	pylint snipbox.py --disable=C0111,R0913 || true

format:
	@echo "Auto-formatting code..."
	@which autopep8 > /dev/null || (echo "autopep8 not installed. Install with: pip install autopep8"; exit 1)
	autopep8 --in-place --aggressive snipbox.py
	@echo "Formatting complete"
