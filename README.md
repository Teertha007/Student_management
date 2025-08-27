# Student Management System (PyQt6 + MySQL)

A simple desktop app to manage student records (add, search, edit, delete) using PyQt6 for the UI and MySQL for storage. The MySQL database and table are created automatically on first run.

## Features
- Add new students with name, course, and mobile
- Search students by exact name
- Edit and delete existing records
- Auto-rearrange IDs after deletion to keep them sequential
- Single-file app with a MySQL backend

## Requirements
- Python 3.11 or newer (per pyproject)
- MySQL Server 8.0+ available locally or remotely
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
pip install PyQt6 mysql-connector-python
```

Option B — uv (recommended if you have uv installed)
```
uv venv
uv sync
```

## Configure database connection
By default, the app connects to a local MySQL server using:
- host: localhost
- user: root
- password: 2580teertha
- database: school

Override these with environment variables before running:
- DB_HOST
- DB_USER
- DB_PASSWORD
- DB_NAME

Examples (Windows PowerShell):
```
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_PASSWORD = "your_password"
$env:DB_NAME = "school"
```
macOS/Linux bash:
```
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=school
```

On first launch, the app will ensure the target database exists and create the `students` table if it isn't present.

## Run
From the project root:
```
python main.py
```
Or with uv:
```
uv run python main.py
```

## Project structure
```
student management/
├─ main.py            # PyQt6 application (uses MySQL)
├─ icons/
│  ├─ add.png
│  └─ search.png
├─ pyproject.toml     # Project metadata and dependency declaration
├─ uv.lock            # uv lockfile (optional)
└─ README.md
```

Note: The previous SQLite file (database.db) is no longer used. You can delete it safely.

## Notes
- The app keeps student IDs sequential by compacting IDs after a deletion. In MySQL this is done by re-inserting rows to reassign AUTO_INCREMENT ids.
- If your MySQL user doesn't have permission for TRUNCATE, you can adjust the `rearrange_ids` method to avoid TRUNCATE.

## Troubleshooting
- MySQL connection errors:
  - Verify host/user/password/db are correct (use env vars).
  - Ensure MySQL Server is running and accessible.
  - Ensure the user has rights to create databases and tables on the server.
- Qt platform plugin errors (e.g., "could not find the Qt platform plugin"):
  - Reinstall PyQt6: `pip install --force-reinstall --no-cache-dir PyQt6`
  - Ensure you’re running inside the virtual environment that has PyQt6 installed.
- If icons don’t render, verify the icons/ folder exists next to main.py.

## Contributing
- Open an issue for bugs or feature requests.
- For small fixes, please submit a PR with a brief description and screenshots if UI-related.

## Author
- Teerthanker Sarker

## License
This project is licensed under the MIT License. See the LICENSE file for details.
