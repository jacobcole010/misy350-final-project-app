import json
from pathlib import Path


APP_FOLDER = Path(__file__).parent
DATA_FILE = APP_FOLDER / "data.json"
USERS_FILE = APP_FOLDER / "users.json"


DATA = {
    "products": [
        {"id": 1, "name": "Blueberry Muffin", "category": "Muffins", "price": 3.50, "stock": 18},
        {"id": 2, "name": "Cinnamon Toast", "category": "Breakfast", "price": 4.00, "stock": 10},
        {"id": 3, "name": "Chocolate Brownie", "category": "Brownies", "price": 3.25, "stock": 4},
        {"id": 4, "name": "Vanilla Cupcake", "category": "Cupcakes", "price": 3.75, "stock": 8},
        {"id": 5, "name": "Sugar Cookie", "category": "Cookies", "price": 2.50, "stock": 2},
    ],
    "sales_log": [
        {"product": "Blueberry Muffin", "qty": 6, "employee": "employee", "date": "2026-04-08", "total": 21.00},
        {"product": "Cinnamon Toast", "qty": 3, "employee": "manager", "date": "2026-04-08", "total": 12.00},
        {"product": "Sugar Cookie", "qty": 5, "employee": "employee", "date": "2026-04-09", "total": 12.50},
    ],
}


USERS = {
    "owner": {"password": "owner123", "role": "Owner", "name": "Owner Demo"},
    "manager": {"password": "manager123", "role": "Owner", "name": "Bakery Manager"},
    "employee": {"password": "employee123", "role": "Employee", "name": "Employee Demo"},
}


def load_json_data(file_path, starter_data):
    if not file_path.exists():
        save_json_data(file_path, starter_data)
        return starter_data

    with open(file_path, "r") as file:
        return json.load(file)


def save_json_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)


class DataManager:
    def __init__(self):
        self.data_file = DATA_FILE
        self.users_file = USERS_FILE
        self.create_files_if_missing()

    def create_files_if_missing(self):
        if not self.data_file.exists():
            save_json_data(self.data_file, DATA)
        if not self.users_file.exists():
            save_json_data(self.users_file, USERS)

    def load_inventory_data(self):
        data = load_json_data(self.data_file, DATA)
        data.setdefault("products", [])
        data.setdefault("sales_log", [])
        return data

    def save_inventory_data(self, data):
        save_json_data(self.data_file, data)

    def load_users(self):
        users = load_json_data(self.users_file, USERS)
        for username in USERS:
            if username not in users:
                users[username] = USERS[username]
        return users

    def save_users(self, users):
        save_json_data(self.users_file, users)
