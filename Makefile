.PHONY: help venv install build-linux build-windows clean

# 虚拟环境目录
VENV := .venv

# 可执行文件路径（Linux / WSL）
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYINSTALLER := $(VENV)/bin/pyinstaller

help:
	@echo "Available targets:"
	@echo "  venv          - Create virtual environment"
	@echo "  install       - Install dependencies"
	@echo "  build-linux   - Build Linux executable"
	@echo "  build-windows - Build Windows executable (Windows only)"
	@echo "  clean         - Clean build artifacts"

# 创建虚拟环境
venv:
	python3 -m venv $(VENV)

# 安装依赖
install: venv
	$(PIP) install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple/
	$(PIP) install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
	$(PIP) install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple/

# Linux / WSL 构建
build-linux:
	$(PYINSTALLER) \
		--onefile \
		--add-data "templates:templates" \
		--name webhook-linux \
		main.py

# Windows 构建（仅在 Windows / Git Bash / GitHub Actions Windows runner）
build-windows:
	pyinstaller \
		--onefile \
		--add-data "templates;templates" \
		--name webhook-windows \
		main.py

# 清理
clean:
	rm -rf build dist *.spec $(VENV)
