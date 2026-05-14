import json
from pathlib import Path


APP_FOLDER = Path(__file__).parent
DATA_FILE = APP_FOLDER / "data.json"
USERS_FILE = APP_FOLDER / "users.json"


DATA = {
    "products": [
        {
            "id": 1,
            "name": "Blueberry Muffin",
            "category": "Muffins",
            "price": 3.50,
            "stock": 18,
            "last_updated_by": "owner",
            "last_updated_by_id": "OWN001",
            "last_updated_date": "2026-04-08",
        },
        {
            "id": 2,
            "name": "Cinnamon Toast",
            "category": "Breakfast",
            "price": 4.00,
            "stock": 10,
            "last_updated_by": "owner",
            "last_updated_by_id": "OWN001",
            "last_updated_date": "2026-04-08",
        },
        {
            "id": 3,
            "name": "Chocolate Brownie",
            "category": "Brownies",
            "price": 3.25,
            "stock": 4,
            "last_updated_by": "owner",
            "last_updated_by_id": "OWN001",
            "last_updated_date": "2026-04-08",
        },
        {
            "id": 4,
            "name": "Vanilla Cupcake",
            "category": "Cupcakes",
            "price": 3.75,
            "stock": 8,
            "last_updated_by": "owner",
            "last_updated_by_id": "OWN001",
            "last_updated_date": "2026-04-08",
        },
        {
            "id": 5,
            "name": "Sugar Cookie",
            "category": "Cookies",
            "price": 2.50,
            "stock": 2,
            "last_updated_by": "owner",
            "last_updated_by_id": "OWN001",
            "last_updated_date": "2026-04-08",
        },
    ],
    "sales_log": [
        {
            "product": "Blueberry Muffin",
            "qty": 6,
            "employee": "employee",
            "employee_id": "EMP001",
            "date": "2026-04-08",
            "total": 21.00,
        },
        {
            "product": "Cinnamon Toast",
            "qty": 3,
            "employee": "manager",
            "employee_id": "MGR001",
            "date": "2026-04-08",
            "total": 12.00,
        },
        {
            "product": "Sugar Cookie",
            "qty": 5,
            "employee": "employee",
            "employee_id": "EMP001",
            "date": "2026-04-09",
            "total": 12.50,
        },
    ],
    "change_log": [],
}


USERS = {
    "owner": {"password": "owner123", "role": "Owner", "name": "Owner Demo", "user_id": "OWN001"},
    "manager": {"password": "manager123", "role": "Owner", "name": "Bakery Manager", "user_id": "MGR001"},
    "employee": {"password": "employee123", "role": "Employee", "name": "Employee Demo", "user_id": "EMP001"},
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
        data.setdefault("change_log", [])
        return data

    def save_inventory_data(self, data):
        save_json_data(self.data_file, data)

    def load_users(self):
        users = load_json_data(self.users_file, USERS)
        changed = False
        for username in USERS:
            if username not in users:
                users[username] = USERS[username]
                changed = True

        next_employee_id = 1
        for username, user_data in users.items():
            if "user_id" not in user_data:
                prefix = "OWN" if user_data.get("role") == "Owner" else "EMP"
                user_data["user_id"] = f"{prefix}{next_employee_id:03d}"
                next_employee_id += 1
                changed = True
        if changed:
            self.save_users(users)
        return users

    def save_users(self, users):
        save_json_data(self.users_file, users)
