# Configuration
REPO_URL = https://github.com/AuriFeen/RepairSch.git
APP_DIR = RepairSch_Source
VENV = $(APP_DIR)/venv
PIP = $(VENV)/bin/pip

.PHONY: install clean

install:
	@echo "--- Fetching Project... ---"
	@if [ ! -d "$(APP_DIR)" ]; then git clone $(REPO_URL) $(APP_DIR); fi
	@echo "--- Setting up Virtual Environment... ---"
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@echo "--- Installing Dependencies... ---"
	@# Use the requirements file directly from the repo
	@$(PIP) install -r $(APP_DIR)/requirements.txt
	@echo "--- Finalizing Desktop Integration... ---"
	@chmod +x $(APP_DIR)/launcher.sh
	@echo "[Desktop Entry]" > $(APP_DIR)/RepairSch.desktop
	@echo "Name=RepairSch" >> $(APP_DIR)/RepairSch.desktop
	@echo "Exec=$(shell pwd)/$(APP_DIR)/launcher.sh" >> $(APP_DIR)/RepairSch.desktop
	@echo "Path=$(shell pwd)/$(APP_DIR)" >> $(APP_DIR)/RepairSch.desktop
	@echo "Type=Application" >> $(APP_DIR)/RepairSch.desktop
	@echo "Terminal=true" >> $(APP_DIR)/RepairSch.desktop
	@mkdir -p ~/.local/share/applications
	@cp $(APP_DIR)/RepairSch.desktop ~/.local/share/applications/
	@echo "Installation Complete! You can now run from your Applications menu."

clean:
	rm -rf $(APP_DIR)
