# Configuration
REPO_URL = https://github.com/AuriFeen/RepairSch.git
APP_DIR = RepairSch_Source
VENV = $(APP_DIR)/venv
PIP = $(VENV)/bin/pip

.PHONY: install clean

install:
	@echo "--- Checking/Fetching Repository... ---"
	@if [ ! -d "$(APP_DIR)" ]; then git clone $(REPO_URL) $(APP_DIR); fi
	@echo "--- Setting up virtual environment... ---"
	@if [ ! -d "$(VENV)" ]; then python3 -m venv $(VENV); fi
	@$(PIP) install --upgrade pip
	@echo "--- Installing dependencies... ---"
	@# Look for either requirements.txt OR requirement.txt
	@if [ -f "$(APP_DIR)/requirements.txt" ]; then \
		$(PIP) install -r $(APP_DIR)/requirements.txt; \
	elif [ -f "$(APP_DIR)/requirement.txt" ]; then \
		$(PIP) install -r $(APP_DIR)/requirement.txt; \
	else \
		echo "Error: No requirements file found!"; exit 1; \
	fi
	@echo "--- Finalizing Launcher... ---"
	@chmod +x launcher.sh
	@echo "[Desktop Entry]" > $(APP_DIR)/RepairSch.desktop
	@echo "Name=RepairSch" >> $(APP_DIR)/RepairSch.desktop
	@echo "Exec=$(shell pwd)/launcher.sh" >> $(APP_DIR)/RepairSch.desktop
	@echo "Path=$(shell pwd)" >> $(APP_DIR)/RepairSch.desktop
	@echo "Type=Application" >> $(APP_DIR)/RepairSch.desktop
	@echo "Terminal=true" >> $(APP_DIR)/RepairSch.desktop
	@mkdir -p ~/.local/share/applications
	@cp $(APP_DIR)/RepairSch.desktop ~/.local/share/applications/
	@echo "Installation Complete!"

clean:
	rm -rf $(APP_DIR)
