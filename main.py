# Import necessary PyQt6 widgets and modules
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, \
    QLineEdit, QGridLayout, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox
from PyQt6.QtGui import QAction
import sys
import sqlite3


class MainWindow(QMainWindow):

    def __init__(self):
        """Initialize the main window with menu bar and table widget."""
        super().__init__()
        self.setWindowTitle("Student Management System")

        # Create menu bar with File and Help menus
        file_menu = self.menuBar().addMenu("&File")
        help_menu = self.menuBar().addMenu("&Help")

        # Add "Add Student" action to File menu
        add_student_action = QAction("&Add Student", self)
        add_student_action.triggered.connect(self.insert)  # Connect to insert method
        file_menu.addAction(add_student_action)

        # Add "About" action to Help menu (placeholder for future implementation)
        about_action = QAction("&About", self)
        help_menu.addAction(about_action)

        # Create and configure the main table widget
        self.table = QTableWidget(0, 3)  # Start with 0 rows, 3 columns initially
        self.table.setColumnCount(4)     # Set to 4 columns for Id, Name, Course, Mobile
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)  # Hide row numbers
        self.setCentralWidget(self.table)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")

        # Clear existing table data
        self.table.setRowCount(0)

        # Populate table with database results
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()

    def insert(self):

        dialog = InsertDialog()
        dialog.exec()  # Show dialog modally


class InsertDialog(QDialog):

    def __init__(self):
        """Initialize the dialog with input fields and submit button."""
        super().__init__()
        self.setWindowTitle("Add Student")
        self.setFixedWidth(300)   # Fixed dialog dimensions
        self.setFixedHeight(300)

        # Create vertical layout for dialog components
        layout = QVBoxLayout()

        # Student name input field
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.student_name)

        # Course selection dropdown
        self.course_name = QComboBox()
        courses = ["Computer Science", "Mathematics", "Physics", "Chemistry"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Mobile number input field
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Enter Mobile Number")
        layout.addWidget(self.mobile)

        # Submit button to save the student data
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)  # Connect to add_student method
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):

        # Get data from input fields
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        # Insert new student into database
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the main window table to show the new student
        main_window.load_data()


# Application entry point
if __name__ == "__main__":
    # Create the PyQt6 application instance
    app = QApplication(sys.argv)

    # Create and show the main window
    main_window = MainWindow()
    main_window.show()

    # Load initial data from database
    main_window.load_data()

    # Start the application event loop
    sys.exit(app.exec())
