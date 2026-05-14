class User:
    def __init__(self, username, password, role, name, user_id=""):
        self.username = username
        self.password = password
        self.role = role
        self.name = name
        self.user_id = user_id or username

    def is_owner(self):
        return self.role == "Owner"


class InventoryItem:
    def __init__(self, item_id, name, category, price, stock):
        self.item_id = item_id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock

    def is_low_stock(self):
        return self.stock < 5

    def get_value(self):
        return self.price * self.stock


class Sale:
    def __init__(self, product_name, quantity, employee, date, total, employee_id=""):
        self.product_name = product_name
        self.quantity = quantity
        self.employee = employee
        self.date = date
        self.total = total
        self.employee_id = employee_id
