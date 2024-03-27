import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QMenu, QAction, QScrollArea, QSizePolicy, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor
import requests

class AIThread(QThread):
    ai_response_received = pyqtSignal(str, bool)  # bool to indicate if it's code

    def __init__(self, question):
        super().__init__()
        self.question = question

    def run(self):
        try:
            response = requests.post("https://floatgptai.replit.app/chat", json={'prompt': self.question})
            response.raise_for_status()
            is_code = 'def' in response.json()['response']  # Simple check for code
            self.ai_response_received.emit(response.json()['response'], is_code)
        except Exception as e:
            self.ai_response_received.emit(f"Error: {str(e)}", False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.symbols = ['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']
        self.i = 0
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_animation)

    def initUI(self):
        self.setWindowTitle('FloatGPT desktop')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #333; color: #FFF;")  # Dark theme

        layout = QVBoxLayout()

        self.response_edit = QTextEdit()
        self.response_edit.setReadOnly(True)  # Make it read-only
        self.response_edit.setFont(QFont('Roboto', 15))
        self.response_edit.setStyleSheet("background-color: #222; color: #FFF; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.response_edit)

        self.ask_button = QPushButton()
        self.ask_button.setIcon(QIcon('./styling/images.png'))  # Set path to your up arrow icon
        self.ask_button.setIconSize(QSize(60, 60))  # Adjust as needed
        self.ask_button.setStyleSheet("QPushButton { background-color: #555; border-radius: 15px; }"
                                      "QPushButton:hover { background-color: #666; }"
                                      "QPushButton:pressed { background-color: #777; }")
        self.ask_button.setFixedSize(60, 60)  # Set fixed size for round shape
        self.ask_button.clicked.connect(self.ask_ai)
        layout.addWidget(self.ask_button, 0, Qt.AlignRight)  # Align the button to the right

        self.question_edit = QLineEdit()
        self.question_edit.setFont(QFont('Arial', 12))
        self.question_edit.setStyleSheet("background-color: #222; color: #FFF; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.question_edit)

        self.response_label = QLabel()
        self.response_label.setWordWrap(True)
        self.response_label.setFont(QFont('Arial', 12))
        self.response_label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.response_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.response_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.response_label.customContextMenuRequested.connect(self.show_context_menu)

    def ask_ai(self):
        question = self.question_edit.text()
        self.ai_thread = AIThread(question)
        self.ai_thread.ai_response_received.connect(self.display_ai_response)
        self.ai_thread.start()
        self.ask_button.setEnabled(False)
        self.start_loading_animation()

    def start_loading_animation(self):
        self.loading_timer.start(100)  # Update every 100 ms

    def update_loading_animation(self):
        self.response_edit.setText('%s' % self.symbols[self.i])
        self.i = (self.i + 1) % len(self.symbols)

    def display_ai_response(self, response, is_code):
        self.ask_button.setEnabled(True)
        self.loading_timer.stop()  # Stop the loading animation
        if is_code:
            self.response_edit.append("Code Snippet:\n" + response)
        else:
            self.start_typewriter_effect(response)
    

    def start_typewriter_effect(self, text, speed_ms=3):
        self.text_to_display = text
        self.current_display_index = 0
        self.typewriter_timer = QTimer()
        self.typewriter_timer.timeout.connect(self.update_typewriter_display)
        self.typewriter_timer.start(speed_ms)

    def update_typewriter_display(self):
        if self.current_display_index < len(self.text_to_display):
            self.response_edit.clear()  # Clear the QTextEdit
            self.response_edit.append(self.text_to_display[:self.current_display_index])  # Use append instead of setText
            self.current_display_index += 1
        else:
            self.typewriter_timer.stop()

    def show_context_menu(self, position):
        context_menu = QMenu()
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_response)
        context_menu.addAction(copy_action)
        context_menu.exec_(self.response_label.mapToGlobal(position))

    def copy_response(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.response_label.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
(app.exec_())