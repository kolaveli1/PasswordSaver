import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox,
    QHBoxLayout, QInputDialog, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QLineEdit
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from database import add_category, add_password, get_categories, get_passwords_by_category, delete_password, update_password
from encryption import decrypt_password, encrypt_password
from cryptography.fernet import InvalidToken


def load_styles():
    try:
        with open("src/styles.qss", "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


class PasswordManager(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Manager")
        self.setGeometry(100, 100, 1400, 600)
        self.setStyleSheet(load_styles())

        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        self.add_category_btn = QPushButton("➕ Tilføj Kategori")
        self.add_category_btn.clicked.connect(self.add_category)
        left_panel.addWidget(self.add_category_btn)

        self.category_list = QListWidget()
        self.category_list.setFixedWidth(250)
        self.category_list.itemClicked.connect(self.load_passwords)
        left_panel.addWidget(self.category_list)

        main_layout.addLayout(left_panel)

        mid_panel = QVBoxLayout()
        mid_panel.setSpacing(10)

        self.add_password_btn = QPushButton("➕ Tilføj Password")
        self.add_password_btn.clicked.connect(self.add_password)
        mid_panel.addWidget(self.add_password_btn)

        self.password_table = QTableWidget()
        self.password_table.setColumnCount(4)
        self.password_table.setHorizontalHeaderLabels(["Website", "Brugernavn", "Password", ""])
        self.password_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.password_table.verticalHeader().setVisible(False)
        self.password_table.verticalHeader().setDefaultSectionSize(50)
        self.password_table.setColumnWidth(0, 300)
        self.password_table.setColumnWidth(1, 300)
        self.password_table.setColumnWidth(2, 400)
        self.password_table.setColumnWidth(3, 50)

        self.password_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.password_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        mid_panel.addWidget(self.password_table)
        main_layout.addLayout(mid_panel)
        self.setLayout(main_layout)
        self.load_categories()

    def load_categories(self):
        self.category_list.clear()
        categories = get_categories()
        for category in categories:
            self.category_list.addItem(category[1])

    def load_passwords(self, item):
        self.selected_category = item.text()
        passwords = get_passwords_by_category(self.selected_category)

        self.password_table.setRowCount(len(passwords))

        for row, (site, user, encrypted_pw) in enumerate(passwords):
            site_item = QTableWidgetItem(site)
            site_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.password_table.setItem(row, 0, site_item)

            self.password_table.setCellWidget(row, 1, self.create_icon_row(user, ["edit", "copy"], row, "username"))

            password_widget = self.create_icon_row("********", ["edit", "copy", "eye"], row, encrypted_pw)
            password_widget.layout().itemAt(0).widget().setProperty("encrypted_pw", encrypted_pw)
            self.password_table.setCellWidget(row, 2, password_widget)

            delete_btn = self.create_icon_button("public/trashcan.png", lambda _, r=row, site=site, user=user: self.delete_password(r, site, user))
            self.password_table.setCellWidget(row, 3, delete_btn)

    def create_icon_row(self, text, icons, row, field):
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        label = QLabel(text)
        label.setStyleSheet("background-color: transparent; color: #d8dee9;")
        layout.addWidget(label)
        layout.addStretch()

        for icon in icons:
            if icon == "edit":
                btn = self.create_icon_button("public/edit.png", lambda _, r=row, f=field: self.edit_field(r, f))
            elif icon == "copy":
                btn = self.create_icon_button("public/copy.png", lambda _, r=row, f=field: self.copy_to_clipboard(r, f))
            elif icon == "eye":
                btn = self.create_icon_button("public/eye.png", lambda _, r=row, f=field: self.toggle_password_visibility(r, f))
            layout.addWidget(btn)

        widget.setLayout(layout)
        return widget

    def create_icon_button(self, icon_path, callback):
        btn = QPushButton()
        btn.setIcon(QIcon(icon_path))
        btn.setFixedSize(24, 24)
        btn.setStyleSheet("border: none; padding: 0; background-color: transparent;")
        btn.clicked.connect(callback)
        return btn

    def delete_password(self, row, site, username):
        reply = QMessageBox.question(self, "Bekræft sletning", "Er du sikker på, at du vil slette dette password?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            delete_password(site, username)
            self.load_passwords(self.category_list.currentItem())

    def copy_to_clipboard(self, row, field):
        if field == "username":
            text = self.password_table.cellWidget(row, 1).layout().itemAt(0).widget().text()
        else:
            label = self.password_table.cellWidget(row, 2).layout().itemAt(0).widget()
            encrypted_pw = label.property("encrypted_pw")
            if encrypted_pw:
                text = decrypt_password(encrypted_pw)
            else:
                QMessageBox.warning(self, "Fejl", "Kunne ikke dekryptere passwordet!")
                return
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def edit_field(self, row, field):
        current_value = self.password_table.cellWidget(row, 1).layout().itemAt(0).widget().text()
        if field != "username":
            current_value = decrypt_password(self.password_table.cellWidget(row, 2).layout().itemAt(0).widget().property("encrypted_pw"))
            new_value, ok = QInputDialog.getText(self, "Rediger", "Indtast nyt password:", text=current_value)
        else:
            new_value, ok = QInputDialog.getText(self, "Rediger", f"Indtast nyt {field}:", text=current_value)

        if ok and new_value:
            if field == "password":
                self.password_table.cellWidget(row, 2).layout().itemAt(0).widget().setProperty("encrypted_pw", encrypt_password(new_value))
                self.password_table.cellWidget(row, 2).layout().itemAt(0).widget().setText("********")
            else:
                self.password_table.cellWidget(row, 1).layout().itemAt(0).widget().setText(new_value)

            site_item = self.password_table.item(row, 0)
            site = site_item.text()
            update_password(site, current_value, new_value)

    def toggle_password_visibility(self, row, encrypted_pw):
        label = self.password_table.cellWidget(row, 2).layout().itemAt(0).widget()
        if label.text() == "********":
            decrypted_pw = decrypt_password(encrypted_pw)
            if decrypted_pw:
                label.setText(decrypted_pw)
            else:
                QMessageBox.warning(self, "Fejl", "Kunne ikke dekryptere password!")
        else:
            label.setText("********")

    def add_category(self):
        text, ok = QInputDialog.getText(self, "Tilføj Kategori", "Indtast kategori navn:")
        if ok and text:
            add_category(text)
            self.load_categories()

    def add_password(self):
        if not hasattr(self, "selected_category") or not self.selected_category:
            QMessageBox.warning(self, "Fejl", "Vælg en kategori først!")
            return

        website, ok1 = QInputDialog.getText(self, "Tilføj Password", "Indtast website:")
        username, ok2 = QInputDialog.getText(self, "Tilføj Password", "Indtast brugernavn:")
        password, ok3 = QInputDialog.getText(self, "Tilføj Password", "Indtast adgangskode:", echo=QLineEdit.EchoMode.Password)

        if not (ok1 and ok2 and ok3):
            return

        add_password(self.selected_category, website, username, password)
        self.load_passwords(self.category_list.currentItem())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordManager()
    window.show()
    sys.exit(app.exec())