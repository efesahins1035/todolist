import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QListWidget, 
                             QListWidgetItem, QMessageBox, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.todos = []
        self.load_todos()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Todo Uygulaması')
        self.setGeometry(100, 100, 600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        title_label = QLabel('Todo Uygulaması')
        title_font = QFont('Arial', 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        input_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText('Yeni görev ekle...')
        self.todo_input.returnPressed.connect(self.add_todo)
        input_layout.addWidget(self.todo_input)
        
        add_button = QPushButton('Ekle')
        add_button.clicked.connect(self.add_todo)
        input_layout.addWidget(add_button)
        
        main_layout.addLayout(input_layout)
        
        self.todo_list = QListWidget()
        self.todo_list.itemDoubleClicked.connect(self.toggle_todo)
        main_layout.addWidget(self.todo_list)
        
        button_layout = QHBoxLayout()
        
        delete_button = QPushButton('Sil')
        delete_button.clicked.connect(self.delete_todo)
        button_layout.addWidget(delete_button)
        
        clear_button = QPushButton('Tümünü Temizle')
        clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_button)
        
        main_layout.addLayout(button_layout)
        
        self.refresh_list()
        
    def add_todo(self):
        text = self.todo_input.text().strip()
        if text:
            todo = {
                'text': text,
                'completed': False
            }
            self.todos.append(todo)
            self.save_todos()
            self.refresh_list()
            self.todo_input.clear()
        
    def toggle_todo(self, item):
        index = self.todo_list.row(item)
        self.todos[index]['completed'] = not self.todos[index]['completed']
        self.save_todos()
        self.refresh_list()
        
    def delete_todo(self):
        current_item = self.todo_list.currentItem()
        if current_item:
            index = self.todo_list.row(current_item)
            del self.todos[index]
            self.save_todos()
            self.refresh_list()
        
    def clear_all(self):
        if self.todos:
            reply = QMessageBox.question(self, 'Onay', 
                                        'Tüm görevleri silmek istediğinize emin misiniz?',
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.todos = []
                self.save_todos()
                self.refresh_list()
        
    def refresh_list(self):
        self.todo_list.clear()
        for todo in self.todos:
            item = QListWidgetItem(todo['text'])
            if todo['completed']:
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
                item.setForeground(Qt.gray)
            self.todo_list.addItem(item)
        
    def save_todos(self):
        try:
            with open('todos.json', 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, 'Hata', f'Kayıt hatası: {str(e)}')
        
    def load_todos(self):
        try:
            with open('todos.json', 'r', encoding='utf-8') as f:
                self.todos = json.load(f)
        except FileNotFoundError:
            self.todos = []
        except Exception as e:
            self.todos = []
            QMessageBox.warning(self, 'Hata', f'Yükleme hatası: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
