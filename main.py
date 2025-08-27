from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, \
    QLineEdit, QGridLayout, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox,\
    QToolBar,QStatusBar,QMessageBox
from PyQt6.QtGui import QAction,QIcon
from PyQt6.QtCore import Qt
import sys
import os
import sqlite3

# Try to import MySQL connector, fall back to SQLite if not available or connection fails
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("MySQL connector not available, using SQLite instead")

class DatabaseConnection:
    USE_SQLITE = True  # Force SQLite by default for now

    def __init__(self,host="localhost", user="root", password="2580teertha",
                  database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    @staticmethod
    def connect(host: str = "localhost", user: str = "root", password: str = "2580teertha", database: str = "school"):
        """Get a database connection (MySQL preferred, SQLite fallback)."""
        if DatabaseConnection.USE_SQLITE:
            return sqlite3.connect("database.db")

        if not MYSQL_AVAILABLE:
            print("MySQL not available, falling back to SQLite")
            DatabaseConnection.USE_SQLITE = True
            return sqlite3.connect("database.db")

        try:
            host = os.getenv("DB_HOST", host)
            user = os.getenv("DB_USER", user)
            password = os.getenv("DB_PASSWORD", password)
            database = os.getenv("DB_NAME", database)

            # Test the connection with timeout
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                connection_timeout=3,
                autocommit=True
            )
            return conn
        except mysql.connector.Error as err:
            print(f"MySQL connection failed: {err}")
            print(f"Attempted connection: host={host}, user={user}, database={database}")
            print("Falling back to SQLite database...")
            DatabaseConnection.USE_SQLITE = True
            return sqlite3.connect("database.db")
        except Exception as e:
            print(f"Unexpected error connecting to MySQL: {e}")
            print("Falling back to SQLite database...")
            DatabaseConnection.USE_SQLITE = True
            return sqlite3.connect("database.db")

    @staticmethod
    def ensure_database(host: str = "localhost", user: str = "root", password: str = "2580teertha", database: str = "school"):
        """Ensure the target database exists (MySQL only, SQLite auto-creates)."""
        if DatabaseConnection.USE_SQLITE:
            return  # SQLite auto-creates the file

        if not MYSQL_AVAILABLE:
            return

        try:
            host = os.getenv("DB_HOST", host)
            user = os.getenv("DB_USER", user)
            password = os.getenv("DB_PASSWORD", password)
            database = os.getenv("DB_NAME", database)

            # Connect to server without selecting a database (with timeout)
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                connection_timeout=3
            )
            cur = conn.cursor()
            try:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                conn.commit()
            finally:
                cur.close()
                conn.close()
        except Exception as e:
            print(f"Could not create MySQL database: {e}")
            print("Will use SQLite instead")
            DatabaseConnection.USE_SQLITE = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(600, 800)

        # Initialize database with error handling
        try:
            print("Initializing database...")
            self.init_database()
            db_type = "SQLite" if DatabaseConnection.USE_SQLITE else "MySQL"
            print(f"Database initialized successfully using {db_type}")
        except Exception as e:
            print(f"Database initialization failed: {e}")
            print("The application will continue with SQLite...")
            DatabaseConnection.USE_SQLITE = True
            try:
                self.init_database()
                print("SQLite fallback successful")
            except Exception as e2:
                print(f"Even SQLite failed: {e2}")
                sys.exit(1)

        file_menu = self.menuBar().addMenu("&File")
        help_menu = self.menuBar().addMenu("&Help")
        edit_menu = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"),"&Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu.addAction(add_student_action)

        about_action = QAction("&About", self)
        help_menu.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"),"&Search", self)
        edit_menu.addAction(search_action)
        search_action.triggered.connect(self.search_student)

        self.table = QTableWidget(0, 3)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        self.table.cellClicked.connect(self.cell_clicked)

    def init_database(self):
        """Initialize the database and create table if it doesn't exist."""
        # Ensure DB exists (MySQL only)
        DatabaseConnection.ensure_database()

        connection = DatabaseConnection.connect()
        cursor = connection.cursor()

        if DatabaseConnection.USE_SQLITE:
            # SQLite syntax
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    course TEXT NOT NULL,
                    mobile TEXT NOT NULL
                )
            ''')
        else:
            # MySQL syntax
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INT NOT NULL AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    course VARCHAR(100) NOT NULL,
                    mobile VARCHAR(20) NOT NULL,
                    PRIMARY KEY (id)
                ) ENGINE=InnoDB
            ''')
        connection.commit()
        cursor.close()
        connection.close()

    def rearrange_ids(self):
        """Reassign IDs to be sequential by re-inserting rows."""
        connection = DatabaseConnection.connect()
        cursor = connection.cursor()

        # Read current data ordered by id
        cursor.execute("SELECT name, course, mobile FROM students ORDER BY id")
        rows = cursor.fetchall()

        if DatabaseConnection.USE_SQLITE:
            # SQLite approach
            cursor.execute("DELETE FROM students")
            # Reset the auto-increment counter
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")
            # Re-insert students with sequential IDs
            for i, (name, course, mobile) in enumerate(rows, 1):
                cursor.execute("INSERT INTO students (id, name, course, mobile) VALUES (?, ?, ?, ?)",
                             (i, name, course, mobile))
        else:
            # MySQL approach
            cursor.execute("TRUNCATE TABLE students")
            # Re-insert without id so AUTO_INCREMENT assigns sequential ids
            if rows:
                cursor.executemany(
                    "INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                    rows,
                )
        connection.commit()
        cursor.close()
        connection.close()

    def cell_clicked(self):
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_student)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_student)

        childern = self.findChildren(QPushButton)
        if childern:
            for child in childern:
                self.statusBar().removeWidget(child)
        self.statusBar().addWidget(edit_button)
        self.statusBar().addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, course, mobile FROM students ORDER BY id")
        rows = cursor.fetchall()

        self.table.setRowCount(0)

        for row_number, row_data in enumerate(rows):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        cursor.close()
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search_student(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit_student(self):
        dialog = EditDialog()
        dialog.exec()

    def delete_student(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = "Student Management System v1.0\n" \
                  "This application is developed by Teethanker Sarker\n" \
                  "It is a simple student management system built with PyQt6 and MySQL."
        self.setText(content)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

class InsertDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Computer Science", "Mathematics", "Physics", "Chemistry"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Enter Mobile Number")
        layout.addWidget(self.mobile)

        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        connection = DatabaseConnection.connect()
        cursor = connection.cursor()

        if DatabaseConnection.USE_SQLITE:
            cursor.execute(
                "INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                (name, course, mobile),
            )
        else:
            cursor.execute(
                "INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                (name, course, mobile),
            )
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_data()
        self.close()

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.student_name)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()

        connection = DatabaseConnection.connect()
        cursor = connection.cursor()

        if DatabaseConnection.USE_SQLITE:
            cursor.execute("SELECT id, name, course, mobile FROM students WHERE name = ?", (name,))
        else:
            cursor.execute("SELECT id, name, course, mobile FROM students WHERE name = %s", (name,))
        rows = cursor.fetchall()

        # Highlight matching rows in the table
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        # Optional: print first match to console for debugging
        if rows:
            print(rows[0])

        cursor.close()
        connection.close()

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        self.student_id = main_window.table.item(index, 0).text()

        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Update Student Name")
        layout.addWidget(self.student_name)

        course_item = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Computer Science", "Mathematics", "Physics", "Chemistry"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_item)
        layout.addWidget(self.course_name)

        mobile_number = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile_number)
        self.mobile.setPlaceholderText("Enter Mobile Number")
        layout.addWidget(self.mobile)

        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection.connect()
        cursor = connection.cursor()

        if DatabaseConnection.USE_SQLITE:
            cursor.execute(
                "UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                (
                    self.student_name.text(),
                    self.course_name.itemText(self.course_name.currentIndex()),
                    self.mobile.text(),
                    self.student_id,
                ),
            )
        else:
            cursor.execute(
                "UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                (
                    self.student_name.text(),
                    self.course_name.itemText(self.course_name.currentIndex()),
                    self.mobile.text(),
                    self.student_id,
                ),
            )
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete this student?")
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)
        self.setLayout(layout)

        yes_button.clicked.connect(self.delete_student)
        no_button.clicked.connect(self.close)

    def delete_student(self):
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection.connect()
        cursor = connection.cursor()

        if DatabaseConnection.USE_SQLITE:
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        else:
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()

        # Rearrange IDs after deletion to remove gaps
        main_window.rearrange_ids()
        main_window.load_data()
        self.close()

        confirmation = QMessageBox()
        confirmation.setWindowTitle("Success")
        confirmation.setText("Student Record Deleted Successfully")
        confirmation.exec()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
