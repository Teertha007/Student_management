# Student Management System (PyQt6 + SQLite)

A simple desktop app to manage student records (add, search, edit, delete) using PyQt6 for the UI and SQLite for storage. The database is local and created automatically on first run.

## Features
- Add new students with name, course, and mobile
- Search students by exact name
- Edit and delete existing records
- Auto-rearrange IDs after deletion to keep them sequential
- Lightweight: single-file app with local SQLite database

## Requirements
- Python 3.11 or newer (per pyproject)
- Windows, macOS, or Linux

## Installation
You can use either pip or uv.

Option A — pip
1) Create and activate a virtual environment
- Windows:
```
python -m venv .venv
.venv\Scripts\activate
```
- macOS/Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```
2) Install dependencies
```
pip install -U pip
pip install PyQt6
```

Option B — uv (recommended if you have uv installed)
```
uv venv
uv sync
```

## Run
From the project root:
```
python main.py
```
Or with uv:
```
uv run python main.py
```

On first launch, a SQLite database file database.db will be created in the project directory. Sample toolbar icons are included in icons/.

## Project structure
```
student management/
├─ main.py            # PyQt6 application
├─ database.db        # Auto-created SQLite database (can be deleted/regenerated)
├─ icons/
│  ├─ add.png
│  └─ search.png
├─ pyproject.toml     # Project metadata and dependency declaration
├─ uv.lock            # uv lockfile (optional)
└─ README.md
```

## Notes
- The app keeps student IDs sequential by compacting IDs after a deletion.
- The database ships with the repo for convenience. If you don’t want to track local data, add database.db to .gitignore before committing.

## Troubleshooting
- Qt platform plugin errors (e.g., "could not find the Qt platform plugin"):
  - Reinstall PyQt6: `pip install --force-reinstall --no-cache-dir PyQt6`
  - Ensure you’re running inside the virtual environment that has PyQt6 installed.
- If fonts or icons don’t render, verify the icons/ folder exists next to main.py.

## Contributing
- Open an issue for bugs or feature requests.
- For small fixes, please submit a PR with a brief description and screenshots if UI-related.

## Author
- Teerthanker Sarker

## License
This project is licensed under the MIT License. See the LICENSE file for details.
