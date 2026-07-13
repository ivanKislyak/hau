# Hau
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-MVP-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Hau** is a desktop app for tracking utility meter values, configuring tariffs, and calculating utility payments.

## Features
- Add and edit properties
- Store utility meter values
- Configure flat and tiered tariffs
- Use remaining-units logic for tiered tariffs
- Calculate utility payments automatically
- Choose interface language on first launch
- Configure preferred currency
- Edit user settings later
- Store data locally in SQLite

## Screenshots
### First launch
![First launch](assets/screenshots/first-launch.png)

### Main screen
![Main screen](assets/screenshots/main-screen.png)

### Value editor
![Value editor](assets/screenshots/value-editor.png)

### Tariff editor
![Tariff editor](assets/screenshots/tariff-editor.png)

## Tech Stack
- Python
- Tkinter
- CustomTkinter
- SQLite
- Pillow
- JSON localization
- locale formatting

## Installation
```bash
git clone https://github.com/ivanKislyak/hau.git
cd hau
pip install -r requirements.txt
python main.py