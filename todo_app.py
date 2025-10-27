import sys
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QListWidget,
                             QListWidgetItem, QMessageBox, QLabel, QDateEdit,
                             QSpinBox, QDialog, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate
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

        main_layout.addLayout(input_layout)

        # Tarih ve süre input'ları
        datetime_layout = QHBoxLayout()

        date_label = QLabel('Bitiş Tarihi:')
        datetime_layout.addWidget(date_label)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat('dd.MM.yyyy')
        datetime_layout.addWidget(self.date_input)

        duration_label = QLabel('Süre (dakika):')
        datetime_layout.addWidget(duration_label)

        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(0)
        self.duration_input.setMaximum(10000)
        self.duration_input.setValue(30)
        self.duration_input.setSuffix(' dk')
        datetime_layout.addWidget(self.duration_input)

        add_button = QPushButton('Ekle')
        add_button.clicked.connect(self.add_todo)
        datetime_layout.addWidget(add_button)

        main_layout.addLayout(datetime_layout)
        
        self.todo_list = QListWidget()
        self.todo_list.itemDoubleClicked.connect(self.toggle_todo)
        main_layout.addWidget(self.todo_list)
        
        button_layout = QHBoxLayout()

        edit_button = QPushButton('Düzenle')
        edit_button.clicked.connect(self.edit_todo)
        button_layout.addWidget(edit_button)

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
            due_date = self.date_input.date().toString('yyyy-MM-dd')
            duration = self.duration_input.value()

            todo = {
                'text': text,
                'completed': False,
                'due_date': due_date,
                'duration': duration
            }
            self.todos.append(todo)
            self.save_todos()
            self.refresh_list()
            self.todo_input.clear()
            self.date_input.setDate(QDate.currentDate())
            self.duration_input.setValue(30)
        
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
            # Geriye dönük uyumluluk için varsayılan değerler
            due_date = todo.get('due_date', '')
            duration = todo.get('duration', 0)

            # Görev metnini formatla
            text = todo['text']
            if due_date:
                # Tarihi formatla
                try:
                    date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d.%m.%Y')
                    text += f' | Bitiş: {formatted_date}'
                except:
                    pass

            if duration > 0:
                # Süreyi formatla
                if duration >= 60:
                    hours = duration // 60
                    minutes = duration % 60
                    if minutes > 0:
                        text += f' | Süre: {hours}sa {minutes}dk'
                    else:
                        text += f' | Süre: {hours}sa'
                else:
                    text += f' | Süre: {duration}dk'

            item = QListWidgetItem(text)
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

    def edit_todo(self):
        current_item = self.todo_list.currentItem()
        if current_item:
            index = self.todo_list.row(current_item)
            todo = self.todos[index]

            dialog = EditTodoDialog(todo, self)
            if dialog.exec_() == QDialog.Accepted:
                # Dialog'dan güncellenmiş değerleri al
                self.todos[index] = dialog.get_todo()
                self.save_todos()
                self.refresh_list()


class EditTodoDialog(QDialog):
    def __init__(self, todo, parent=None):
        super().__init__(parent)
        self.todo = todo.copy()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Görevi Düzenle')
        self.setModal(True)

        layout = QFormLayout()

        # Görev metni
        self.text_input = QLineEdit(self.todo['text'])
        layout.addRow('Görev:', self.text_input)

        # Tarih
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat('dd.MM.yyyy')

        due_date = self.todo.get('due_date', '')
        if due_date:
            try:
                date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                qdate = QDate(date_obj.year, date_obj.month, date_obj.day)
                self.date_input.setDate(qdate)
            except:
                self.date_input.setDate(QDate.currentDate())
        else:
            self.date_input.setDate(QDate.currentDate())

        layout.addRow('Bitiş Tarihi:', self.date_input)

        # Süre
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(0)
        self.duration_input.setMaximum(10000)
        self.duration_input.setValue(self.todo.get('duration', 30))
        self.duration_input.setSuffix(' dk')
        layout.addRow('Süre (dakika):', self.duration_input)

        # Butonlar
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_todo(self):
        return {
            'text': self.text_input.text().strip(),
            'completed': self.todo['completed'],
            'due_date': self.date_input.date().toString('yyyy-MM-dd'),
            'duration': self.duration_input.value()
        }


def main():
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
