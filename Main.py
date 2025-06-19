import sys
import os
import sqlite3


from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QFrame, QPushButton, QLineEdit, QComboBox, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "decor.db")
ICON_PATH = os.path.join(BASE_DIR, "Наш декор.ico")
LOGO_PATH = os.path.join(BASE_DIR, "Наш декор.png")

class ProductItemWidget(QFrame):
    def __init__(self, product, cost):
        super().__init__()
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #000;
            }
            QLabel#header {
                font-family: Gabriola;
                font-size: 20px;
                font-weight: bold;
                color: #000000;
            }
            QLabel#sub {
                font-family: Gabriola;
                font-size: 16px;
                color: #000000;
            }
            QLabel#cost {
                font-family: Gabriola;
                font-size: 20px;
                font-weight: bold;
                color: #000000;
            }
            QLabel {
                border: none;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Левая часть с информацией о продукте
        left = QVBoxLayout()
        header_layout = QHBoxLayout()
        
        header = QLabel(f"{product['product_type']} | {product['name']}")
        header.setObjectName("header")
        header_layout.addWidget(header)
        
        # Правая часть с ценой (теперь на одном уровне с заголовком)
        cost_lbl = QLabel(f"{cost:.2f} р")
        cost_lbl.setObjectName("cost")
        cost_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(cost_lbl)
        
        left.addLayout(header_layout)

        # Добавляем остальную информацию о продукте
        for text in (
            f"Артикул: {product['sku']}",
            f"Мин. цена: {product['min_partner_price']:.2f} р",
            f"Ширина: {product['roll_width']:.2f} м"
        ):
            lbl = QLabel(text)
            lbl.setObjectName("sub")
            left.addWidget(lbl)

        layout.addLayout(left)

class ProductForm(QWidget):
    def __init__(self, parent, product=None):
        super().__init__()
        self.parent = parent
        self.product = product
        self.original_sku = product['sku'] if product else None 

        self.setWindowTitle("Редактировать продукт" if product else "Добавить продукт")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: Gabriola;
                color: #000000;
            }
            QLabel {
                font-size: 16px;
                color: #000000;
            }
            QLineEdit, QComboBox {
                font-family: Gabriola;
                font-size: 16px;
                padding: 4px;
                border: 1px solid #666;
                border-radius: 4px;
                color: #000000;
                background-color: white;
            }
            QPushButton {
                font-family: Gabriola;
                font-size: 16px;
                background-color: #2D6033;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #244a25;
            }
        """)

        layout = QVBoxLayout(self)

        self.sku_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["Обои", "Фрески", "Панно"])
        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.width_input = QLineEdit()

        layout.addWidget(QLabel("Артикул:"))
        layout.addWidget(self.sku_input)
        layout.addWidget(QLabel("Тип продукта:"))
        layout.addWidget(self.type_input)
        layout.addWidget(QLabel("Наименование:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Мин. цена для партнера:"))
        layout.addWidget(self.price_input)
        layout.addWidget(QLabel("Ширина рулона (м):"))
        layout.addWidget(self.width_input)

        btn_layout = QHBoxLayout()
        back_btn = QPushButton("Назад")
        save_btn = QPushButton("Сохранить")
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        save_btn.clicked.connect(self.save)
        back_btn.clicked.connect(self.close)

        if product:
            self.populate_fields()

    def populate_fields(self):
        self.sku_input.setText(str(self.product['sku']))
        self.type_input.setCurrentText(self.product['product_type'])
        self.name_input.setText(self.product['name'])
        self.price_input.setText(str(self.product['min_partner_price']))
        self.width_input.setText(str(self.product['roll_width']))

    def save(self):
        try:
            sku = self.sku_input.text().strip()
            prod_type = self.type_input.currentText()
            name = self.name_input.text().strip()
            min_price = float(self.price_input.text())
            roll_width = float(self.width_input.text())

            if min_price < 0 or roll_width < 0:
                raise ValueError("Цена и ширина не могут быть отрицательными")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            if sku != self.original_sku:
                cursor.execute("SELECT COUNT(*) FROM products WHERE sku=?", (sku,))
                if cursor.fetchone()[0] > 0:
                    raise ValueError("Артикул должен быть уникальным!")

            if self.product:
                cursor.execute("""
                    UPDATE products SET product_type=?, name=?, min_partner_price=?, roll_width=?, sku=?
                    WHERE sku=?
                """, (prod_type, name, min_price, roll_width, sku, self.original_sku))
            else:
                cursor.execute("""
                    INSERT INTO products (product_type, name, sku, min_partner_price, roll_width)
                    VALUES (?, ?, ?, ?, ?)
                """, (prod_type, name, sku, min_price, roll_width))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успешно", "Продукт сохранён.")
            self.parent.load_and_show_products()
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Неверные данные: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

class ProductApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Каталог продукции")
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.setFixedSize(1000, 600)
        self.setStyleSheet("QWidget { background-color: #FFFFFF; font-family: Gabriola; color: #000000; }")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)

        logo = QLabel()
        pixmap = QPixmap(LOGO_PATH)
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(logo)

        title = QLabel("Каталог продукции")
        title.setFont(QFont("Gabriola", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setSpacing(8)
        self.list_widget.setStyleSheet("QListWidget { border: none; background: #FFFFFF; }")
        self.list_widget.itemClicked.connect(self.open_edit_form)
        main_layout.addWidget(self.list_widget)

        self.load_and_show_products()

    def load_and_show_products(self):
        self.list_widget.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT product_type, name, sku, min_partner_price, roll_width FROM products")
        for prod_type, name, sku, min_price, roll_width in cursor.fetchall():
            cost = self.calculate_product_cost(cursor, name)
            product = {
                "product_type": prod_type,
                "name": name,
                "sku": sku,
                "min_partner_price": min_price,
                "roll_width": roll_width
            }

            item = QListWidgetItem(self.list_widget)
            widget = ProductItemWidget(product, cost)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, product)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

        conn.close()

    def calculate_product_cost(self, cursor, product_name):
        cursor.execute("""
            SELECT pm.required_quantity, m.price_per_unit
            FROM product_materials pm
            JOIN materials m ON pm.material_name = m.name
            WHERE pm.product_name = ?
        """, (product_name,))
        total = sum(qty * price for qty, price in cursor.fetchall() if qty and price)
        return round(total, 2)

    def open_edit_form(self, item):
        product = item.data(Qt.ItemDataRole.UserRole)
        self.form = ProductForm(self, product)
        self.form.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductApp()
    window.show()
    sys.exit(app.exec())
