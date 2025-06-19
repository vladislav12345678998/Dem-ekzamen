import pandas as pd
import sqlite3
import openpyxl



conn = sqlite3.connect('decor.db')

def import_from_excel(file, table, rename_columns):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.replace('\xa0', ' ', regex=True)
    df = df.rename(columns=rename_columns)
    print(f"Импорт из {file} → таблица {table}")
    df.to_sql(table, conn, if_exists='append', index=False)

import_from_excel(
    "Material_type_import.xlsx",
    "material_types",
    {
        "Тип материала": "name",
        "Процент брака материала": "defect_percent"
    }
)

import_from_excel(
    "Materials_import.xlsx",
    "materials",
    {
        "Наименование материала": "name",
        "Тип материала": "material_type",
        "Цена единицы материала": "price_per_unit",
        "Минимальное количество": "min_quantity",
        "Количество в упаковке": "pack_quantity",
        "Единица измерения": "unit"
    }
)

import_from_excel(
    "Product_materials_import.xlsx",
    "product_materials",
    {
        "Продукция": "product_name",
        "Наименование материала": "material_name",
        "Необходимое количество материала": "required_quantity"
    }
)

import_from_excel(
    "Product_type_import.xlsx",
    "product_types",
    {
        "Тип продукции": "name",
        "Коэффициент типа продукции": "coefficient"
    }
)

import_from_excel(
    "Products_import.xlsx",
    "products",
    {
        "Тип продукции": "product_type",
        "Наименование продукции": "name",
        "Артикул": "sku",
        "Минимальная стоимость для партнера": "min_partner_price",
        "Ширина рулона, м": "roll_width"
    }
)

# Закрытие соединения
conn.close()
print("Все данные импортированы.")


