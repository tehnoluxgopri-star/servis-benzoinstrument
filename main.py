warning(self, "Помилка", "Заповніть обов'язкові поля: Клієнт, Телефон, Товар!")
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
    lines = [
        "==================================================",
        f"СЕРВІС БЕНЗОІНСТРУМЕНТ — КВИТАНЦІЯ ПРИЙОМУ №{info[0]}",
        "==================================================",
        f"Дата отримання: {info[6]}",
        f"Клієнт: {info[1]}",
        f"Телефон: {info[2]}",
        f"Товар: {info[3]}",
        f"Серійний №: {info[4]}",
        f"Заявлена несправність: {info[5]}",
        f"Примітки: {info[9]}",
        "--------------------------------------------------",
        "Прийняв майстер: _______________   Підпис клієнта: _______________"
    ]
    text = "\n".join(lines)
    QMessageBox.information(self, "Квитанція отримання", text)

def print_receipt_out(self):
    """Формування квитанції видачі"""
    row = self.table.currentRow()
    if row == -1:
        QMessageBox.warning(self, "Увага", "Оберіть замовлення!")
        return

    info = [self.table.item(row, col).text() for col in range(10)]
    date_val = info[7] if info[7] else datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [
        "==================================================",
        f"СЕРВІС БЕНЗОІНСТРУМЕНТ — КВИТАНЦІЯ ВИДАЧІ №{info[0]}",
        "==================================================",
        f"Дата видачі: {date_val}",
        f"Клієнт: {info[1]}",
        f"Товар: {info[3]} (С/Н: {info[4]})",
        f"Статус: {info[8]}",
        f"Примітки: {info[9]}",
        "--------------------------------------------------",
        "Претензій до якості виконаних робіт не маю.",
        "Підпис клієнта: _______________"
    ]
    text = "\n".join(lines)
    QMessageBox.information(self, "Квитанція видачі", text)

def closeEvent(self, event):
    self.conn.close()
if name == "main": app = QApplication(sys.argv) win = BenzoinstrumentApp() win.show() sys.exit(app.exec())
