from datetime import datetime

from models import InventoryItem, Sale, User


class AuthService:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def find_user_by_username(self, username):
        username = username.strip().lower()
        users = self.data_manager.load_users()

        if username not in users:
            return None

        user_data = users[username]
        return User(username, user_data["password"], user_data["role"], user_data["name"], user_data.get("user_id", username))

    def validate_login(self, username, password):
        user = self.find_user_by_username(username)

        if user and user.password == password:
            return user

        return None

    def register_user(self, username, password, role, name):
        username = username.strip().lower()
        name = name.strip()

        if username == "" or password == "":
            return False, "Username and password are required."

        if len(password) < 6:
            return False, "Password must be at least 6 characters."

        users = self.data_manager.load_users()

        if username in users:
            return False, "That username is already taken."

        if name == "":
            name = username.title()

        prefix = "OWN" if role == "Owner" else "EMP"
        user_number = len(users) + 1
        users[username] = {"password": password, "role": role, "name": name, "user_id": f"{prefix}{user_number:03d}"}
        self.data_manager.save_users(users)
        return True, "Account created. You can log in now."


class InventoryService:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def get_data(self):
        return self.data_manager.load_inventory_data()

    def save_data(self, data):
        self.data_manager.save_inventory_data(data)

    def get_products(self):
        data = self.get_data()
        products = []

        for product in data["products"]:
            products.append(
                InventoryItem(
                    product["id"],
                    product["name"],
                    product.get("category", "Bakery"),
                    float(product["price"]),
                    int(product["stock"]),
                )
            )

        return products

    def find_product(self, item_id):
        for product in self.get_products():
            if product.item_id == item_id:
                return product
        return None

    def add_product(self, name, category, price, stock, changed_by="", changed_by_id=""):
        name = name.strip()
        category = category.strip()

        if name == "":
            return False, "Product name is required."

        if category == "":
            category = "Bakery"

        if price <= 0:
            return False, "Price must be greater than zero."

        if stock < 0:
            return False, "Stock cannot be negative."

        data = self.get_data()

        for product in data["products"]:
            if product["name"].lower() == name.lower():
                return False, "That product already exists."

        new_id = max([product["id"] for product in data["products"]], default=0) + 1
        data["products"].append(
            {
                "id": new_id,
                "name": name,
                "category": category,
                "price": float(price),
                "stock": int(stock),
                "last_updated_by": changed_by,
                "last_updated_by_id": changed_by_id,
                "last_updated_date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        self.add_change_log(data, "Added product", name, changed_by, changed_by_id)
        self.save_data(data)
        return True, "Product added."

    def update_product(self, item_id, name, category, price, stock, changed_by="", changed_by_id=""):
        name = name.strip()
        category = category.strip()

        if name == "":
            return False, "Product name is required."

        if category == "":
            category = "Bakery"

        if price <= 0:
            return False, "Price must be greater than zero."

        if stock < 0:
            return False, "Stock cannot be negative."

        data = self.get_data()

        for product in data["products"]:
            if product["id"] == item_id:
                product["name"] = name
                product["category"] = category
                product["price"] = float(price)
                product["stock"] = int(stock)
                product["last_updated_by"] = changed_by
                product["last_updated_by_id"] = changed_by_id
                product["last_updated_date"] = datetime.now().strftime("%Y-%m-%d")
                self.add_change_log(data, "Updated product", name, changed_by, changed_by_id)
                self.save_data(data)
                return True, "Product updated."

        return False, "Product not found."

    def delete_product(self, item_id, changed_by="", changed_by_id=""):
        data = self.get_data()

        for product in data["products"]:
            if product["id"] == item_id:
                data["products"].remove(product)
                self.add_change_log(data, "Deleted product", product["name"], changed_by, changed_by_id)
                self.save_data(data)
                return True, "Product deleted."

        return False, "Product not found."

    def log_sale(self, item_id, quantity, employee, employee_id=""):
        data = self.get_data()
        quantity = int(quantity)

        for product in data["products"]:
            if product["id"] == item_id:
                if product["stock"] < quantity:
                    return False, "Not enough stock."

                product["stock"] -= quantity
                total = round(product["price"] * quantity, 2)
                data["sales_log"].append(
                    {
                        "product": product["name"],
                        "qty": quantity,
                        "employee": employee,
                        "employee_id": employee_id,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "total": total,
                    }
                )
                self.save_data(data)
                return True, "Sale logged."

        return False, "Product not found."

    def get_sales(self):
        data = self.get_data()
        sales = []

        for sale in data["sales_log"]:
            sales.append(
                Sale(
                    sale["product"],
                    sale["qty"],
                    sale["employee"],
                    sale["date"],
                    sale.get("total", 0),
                    sale.get("employee_id", ""),
                )
            )

        return sales

    def add_change_log(self, data, action, product_name, changed_by, changed_by_id):
        data.setdefault("change_log", [])
        data["change_log"].append(
            {
                "action": action,
                "product": product_name,
                "changed_by": changed_by,
                "changed_by_id": changed_by_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%I:%M %p"),
            }
        )

    def get_change_rows(self):
        data = self.get_data()
        rows = []

        for change in data.get("change_log", []):
            rows.append(
                {
                    "Action": change.get("action", ""),
                    "Product": change.get("product", ""),
                    "Changed By": change.get("changed_by", ""),
                    "Employee ID": change.get("changed_by_id", ""),
                    "Date": change.get("date", ""),
                    "Time": change.get("time", ""),
                }
            )

        return rows

    def get_recent_sales(self):
        return self.get_sales()[-3:]

    def get_low_stock_items(self):
        low_items = []

        for product in self.get_products():
            if product.is_low_stock():
                low_items.append(product)

        return low_items

    def get_summary(self):
        products = self.get_products()
        sales = self.get_sales()

        return {
            "products": len(products),
            "low_stock": len(self.get_low_stock_items()),
            "inventory_value": sum(product.get_value() for product in products),
            "sales_total": sum(sale.total for sale in sales),
        }

    def get_product_rows(self):
        rows = []
        data = self.get_data()

        for product_data in data["products"]:
            product = InventoryItem(
                product_data["id"],
                product_data["name"],
                product_data.get("category", "Bakery"),
                float(product_data["price"]),
                int(product_data["stock"]),
            )
            rows.append(
                {
                    "ID": product.item_id,
                    "Name": product.name,
                    "Category": product.category,
                    "Price": f"${product.price:.2f}",
                    "Stock": product.stock,
                    "Value": f"${product.get_value():.2f}",
                    "Updated By": product_data.get("last_updated_by", ""),
                    "Employee ID": product_data.get("last_updated_by_id", ""),
                }
            )

        return rows

    def get_sales_rows(self):
        rows = []

        for sale in self.get_sales():
            rows.append(
                {
                    "Product": sale.product_name,
                    "Quantity": sale.quantity,
                    "Employee": sale.employee,
                    "Employee ID": sale.employee_id,
                    "Date": sale.date,
                    "Total": f"${sale.total:.2f}",
                }
            )

        return rows

    def get_low_stock_rows(self):
        rows = []

        for product in self.get_low_stock_items():
            rows.append(
                {
                    "ID": product.item_id,
                    "Name": product.name,
                    "Category": product.category,
                    "Stock": product.stock,
                    "Restock Needed": 5 - product.stock,
                }
            )

        return rows

    def get_ai_context(self):
        product_lines = []
        sale_lines = []

        for product in self.get_products():
            product_lines.append(f"{product.name}: {product.stock} in stock, ${product.price:.2f}, {product.category}")

        for sale in self.get_sales():
            sale_lines.append(f"{sale.date}: {sale.quantity} {sale.product_name} sold by {sale.employee}")

        return "\n".join(product_lines) + "\n\nSales:\n" + "\n".join(sale_lines)
