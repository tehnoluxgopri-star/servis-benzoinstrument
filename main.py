import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView
)

class BenzoinstrumentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сервіс бензоінструмент — Система обліку")
        self.resize(1100, 650)
        
        self.init_db()
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # === Поля вводу нових замовлень ===
        form_layout = QHBoxLayout()
        
        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("ПІБ Клієнта")
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон")
        
        self.device_input = QLineEdit()
        self.device_input.setPlaceholderText("Найменування товару")
        
        self.sn_input = QLineEdit()
        self.sn_input.setPlaceholderText("Серійний номер")
        
        self.issue_input = QLineEdit()
        self.issue_input.setPlaceholderText("Несправність")

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Примітки")

        add_btn = QPushButton("Прийняти в ремонт")
        add_btn.setStyleSheet("background-color: #17B978; color: white; font-weight: bold;")
        add_btn.clicked.connect(self.add_order)

        form_layout.addWidget(self.client_input)
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(self.device_input)
        form_layout.addWidget(self.sn_input)
        form_layout.addWidget(self.issue_input)
        form_layout.addWidget(self.notes_input)
        form_layout.addWidget(add_btn)

        main_layout.addLayout(form_layout)

        # === Таблиця замовлень ===
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "№", "Клієнт", "Телефон", "Товар", "Серійний №", 
            "Несправність", "Дата отримання", "Дата видачі", "Статус", "Примітки"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        # === Панель управління та квитанцій ===
        action_layout = QHBoxLayout()
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Прийнято", "В роботі", "Готово до видачі", "Видано"])
        
        update_btn = QPushButton("Змінити статус")
        update_btn.clicked.connect(self.update_status)

        receipt_in_btn = QPushButton("Квитанція отримання")
        receipt_in_btn.clicked.connect(self.print_receipt_in)

        receipt_out_btn = QPushButton("Квитанція видачі")
        receipt_out_btn.clicked.connect(self.print_receipt_out)

        action_layout.addWidget(QLabel("Статус:"))
        action_layout.addWidget(self.status_combo)
        action_layout.addWidget(update_btn)
        action_layout.addSpacing(20)
        action_layout.addWidget(receipt_in_btn)
        action_layout.addWidget(receipt_out_btn)
        action_layout.addStretch()

        main_layout.addLayout(action_layout)

        self.load_data()

    def init_db(self):
        """Ініціалізація бази даних SQLite"""
        self.conn = sqlite3.connect("service_benzoinstrument.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client TEXT,
                phone TEXT,
                device TEXT,
                serial_number TEXT,
                issue TEXT,
                date_in TEXT,
                date_out TEXT,
                status TEXT,
                notes TEXT
            )
        ''')
        self.conn.commit()

    def add_order(self):
        """Додавання нового замовлення"""
        client = self.client_input.text().strip()
        phone = self.phone_input.text().strip()
        device = self.device_input.text().strip()
        sn = self.sn_input.text().strip()
        issue = self.issue_input.text().strip()
        notes = self.notes_input.text().strip()
        date_in = datetime.now().strftime("%Y-%m-%d %H:%M")

        if not client or not phone or not device:
            QMessageBox.warning(self, "Помилка", "Заповніть обов'язкові поля: Клієнт, Телефон, Товар!")
            return

        self.cursor.execute('''
            INSERT INTO orders (client, phone, device, serial_number, issue, date_in, date_out, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, '', 'Прийнято', ?)
        ''', (client, phone, device, sn, issue, date_in, notes))
        self.conn.commit()

        self.client_input.clear()
        self.phone_input.clear()
        self.device_input.clear()
        self.sn_input.clear()
        self.issue_input.clear()
        self.notes_input.clear()

        self.load_data()

    def load_data(self):
        """Завантаження списку замовлень у таблицю"""
        self.cursor.execute("SELECT * FROM orders ORDER BY id DESC")
        rows = self.cursor.fetchall()

        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(data if data else "")))

    def update_status(self):
        """Оновлення статусу та дати видачі"""
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Увага", "Оберіть замовлення зі списку!")
            return

        order_id = self.table.item(row, 0).text()
        new_status = self.status_combo.currentText()
        date_out = datetime.now().strftime("%Y-%m-%d %H:%M") if new_status == "Видано" else ""

        self.cursor.execute("UPDATE orders SET status = ?, date_out = ? WHERE id = ?", (new_status, date_out, order_id))
        self.conn.commit()
        self.load_data()

    def print_receipt_in(self):
        """Формування квитанції прийому"""
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Увага", "Оберіть замовлення для створення квитанції!")
            return

        info = [self.table.item(row, col).text() for col in range(10)]
        text = (
            "==================================================\n"
            f"СЕРВІС БЕНЗОІНСТРУМЕНТ — КВИТАНЦІЯ ПРИЙОМУ №{info[0]}\n"
            "==================================================\n"
            f"Дата отримання: {info[6]}\n"
            f"Клієнт: {info[1]}\n"
            f"Телефон: {info[2]}\n"
            f"Товар: {info[3]}\n"
            f"Серійний №: {info[4]}\n"
            f"Заявлена несправність: {info[5]}\n"
            f"Примітки: {info[9]}\n"
            "--
