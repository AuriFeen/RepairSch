# Configuration
REPO_URL = https://github.com/AuriFeen/RepairSch.git
# Configuration - Pointing to the current directory
APP_DIR = .
VENV = $(APP_DIR)/venv
PIP = $(VENV)/bin/pip

.PHONY: install clean

install:
	@echo "--- Setting up Virtual Environment... ---"
	@python3 -m venv venv
	@./venv/bin/pip install --upgrade pip
	@echo "--- Installing Dependencies... ---"
	@if [ -f requirements.txt ]; then ./venv/bin/pip install -r requirements.txt; fi
	@echo "--- Finalizing Desktop Integration... ---"
	@chmod +x launcher.sh
	@# Update the .desktop file to reflect current path
	@echo "[Desktop Entry]" > RepairSch.desktop
	@echo "Name=RepairSch" >> RepairSch.desktop
	@echo "Exec=$(shell pwd)/launcher.sh" >> RepairSch.desktop
	@echo "Path=$(shell pwd)" >> RepairSch.desktop
	@echo "Type=Application" >> RepairSch.desktop
	@echo "Terminal=true" >> RepairSch.desktop
	@mkdir -p ~/.local/share/applications
	@cp RepairSch.desktop ~/.local/share/applications/
	@echo "Installation Complete!"

clean:
	rm -rf $(APP_DIR)
