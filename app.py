import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Bakery Inventory Manager")

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return {"products": [], "sales_log": []}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {"owner": {"password": "owner123", "role": "Owner"}, "employee": {"password": "employee123", "role": "Employee"}}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None

users_db = load_users()

#Login Page
if not st.session_state.logged_in:
    st.title("Bakery Inventory Manager")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            if username in users_db and users_db[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.role = users_db[username]["role"]
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.info("Sign In: User:owner Pass:owner123 or User:employee Pass:employee123")
    
    with tab2:
        st.subheader("Register")
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        role = st.radio("Role:", ["Owner", "Employee"], key="reg_role")
        
        if st.button("Register"):
            if new_user and new_pass:
                if new_user in users_db:
                    st.error("Username taken")
                else:
                    users_db[new_user] = {"password": new_pass, "role": role}
                    save_users(users_db)
                    st.success("Account created!")
            else:
                st.error("Fill all fields")

# Main App
else:
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.title("Bakery Inventory Manager")
    st.write(f"User: {st.session_state.user} | {st.session_state.role}")
    st.markdown("---")
    
    if st.session_state.role == "Owner":
        st.subheader("Owner Dashboard")
        choice = st.radio("Action:", ["View Products", "Add Product", "Update Product", "Delete Product", "Chatbot"], horizontal=True)
        
        if choice == "Add Product":
            name = st.text_input("Product name", key="add_name")
            price = st.number_input("Price", min_value=0.01, step=0.01, key="add_price")
            stock = st.number_input("Stock", min_value=1, step=1, key="add_stock")
            
            if st.button("Add"):
                if name.strip():
                    data = load_data()
                    if any(p["name"].lower() == name.lower() for p in data["products"]):
                        st.error("Product already exists")
                    else:
                        new_id = max([p["id"] for p in data["products"]], default=0) + 1
                        data["products"].append({"id": new_id, "name": name, "price": price, "stock": stock})
                        save_data(data)
                        st.success("Product added!")
                else:
                    st.error("Name cannot be empty")
        
        elif choice == "View Products":
            data = load_data()
            if data["products"]:
                for p in data["products"]:
                    st.write(f"ID {p['id']}: {p['name']} - ${p['price']} | Stock: {p['stock']}")
            else:
                st.info("No products")
        
        elif choice == "Update Product":
            data = load_data()
            if data["products"]:
                pid = st.selectbox("Select product", [p["id"] for p in data["products"]], format_func=lambda x: f"ID {x}: {next(p['name'] for p in data['products'] if p['id'] == x)}", key="upd_id")
                product = next(p for p in data["products"] if p["id"] == pid)
                
                new_name = st.text_input("Name", value=product["name"], key="upd_name")
                new_price = st.number_input("Price", value=product["price"], step=0.01, key="upd_price")
                new_stock = st.number_input("Stock", value=product["stock"], step=1, key="upd_stock")
                
                if st.button("Update"):
                    product["name"] = new_name
                    product["price"] = new_price
                    product["stock"] = new_stock
                    save_data(data)
                    st.success("Updated!")
            else:
                st.info("No products")
        
        elif choice == "Delete Product":
            data = load_data()
            if data["products"]:
                pid = st.selectbox("Select product", [p["id"] for p in data["products"]], format_func=lambda x: f"ID {x}: {next(p['name'] for p in data['products'] if p['id'] == x)}", key="del_id")
                
                if st.button("Delete"):
                    data["products"] = [p for p in data["products"] if p["id"] != pid]
                    save_data(data)
                    st.success("Deleted!")
            else:
                st.info("No products")
        
        elif choice == "Chatbot":
            q = st.text_input("Ask about inventory:", key="owner_bot")
            if q:
                data = load_data()
                q = q.lower()
                if "low stock" in q:
                    low = [p for p in data["products"] if p["stock"] < 5]
                    st.write("Low stock:" if low else "All well-stocked!")
                    for p in low:
                        st.write(f"- {p['name']}: {p['stock']} units")
                elif "how many" in q:
                    st.write(f"Total products: {len(data['products'])}")
                elif "total value" in q:
                    value = sum(p["price"] * p["stock"] for p in data["products"])
                    st.write(f"Inventory value: ${value:.2f}")
                elif "sales" in q:
                    if data["sales_log"]:
                        st.write("Recent sales:")
                        for s in data["sales_log"][-5:]:
                            st.write(f"- {s['product']} x{s['qty']} by {s['employee']}")
                    else:
                        st.write("No sales yet")
                else:
                    st.write("Try: low stock, how many, total value, sales")
    
    else:
        st.subheader("Employee Dashboard")
        choice = st.radio("Action:", ["View Catalog", "Log Sale", "Low Stock", "Chatbot"], horizontal=True)
        
        if choice == "View Catalog":
            data = load_data()
            if data["products"]:
                for p in data["products"]:
                    st.write(f"{p['name']} - ${p['price']} | Stock: {p['stock']}")
            else:
                st.info("No products")
        
        elif choice == "Log Sale":
            data = load_data()
            if data["products"]:
                pid = st.selectbox("Select product", [p["id"] for p in data["products"]], format_func=lambda x: next(p['name'] for p in data["products"] if p['id'] == x), key="sale_id")
                qty = st.number_input("Quantity", min_value=1, step=1, key="sale_qty")
                
                if st.button("Log Sale"):
                    product = next(p for p in data["products"] if p["id"] == pid)
                    if product["stock"] >= qty:
                        product["stock"] -= qty
                        data["sales_log"].append({"product": product["name"], "qty": qty, "employee": st.session_state.user, "date": datetime.now().isoformat()})
                        save_data(data)
                        st.success(f"Sold {qty} x {product['name']}")
                    else:
                        st.error("Not enough stock!")
            else:
                st.info("No products")
        
        elif choice == "Low Stock":
            data = load_data()
            low = [p for p in data["products"] if p["stock"] < 5]
            if low:
                st.warning("Items below 5 units:")
                for p in low:
                    st.write(f"{p['name']} - {p['stock']} units")
            else:
                st.info("No low stock items")
        
        elif choice == "Chatbot":
            q = st.text_input("Ask about inventory:", key="emp_bot")
            if q:
                data = load_data()
                q = q.lower()
                if "low stock" in q:
                    low = [p for p in data["products"] if p["stock"] < 5]
                    st.write("Low stock:" if low else "All well-stocked!")
                    for p in low:
                        st.write(f"- {p['name']}: {p['stock']} units")
                elif "how many" in q:
                    st.write(f"Total products: {len(data['products'])}")
                elif "total value" in q:
                    value = sum(p["price"] * p["stock"] for p in data["products"])
                    st.write(f"Inventory value: ${value:.2f}")
                elif "sales" in q:
                    if data["sales_log"]:
                        st.write("Recent sales:")
                        for s in data["sales_log"][-5:]:
                            st.write(f"- {s['product']} x{s['qty']} by {s['employee']}")
                    else:
                        st.write("No sales yet")
                else:
                    st.write("Try: low stock, how many, total value, sales")