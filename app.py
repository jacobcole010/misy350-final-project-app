import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Jacob's Bakery Inventory Manager")

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
    st.session_state.data = load_data()

if not st.session_state.logged_in:
    st.title("Jacob's Bakery Inventory Manager")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        user = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", key="login_btn"):
            users_db = load_users()
            if user in users_db and users_db[user]["password"] == pwd:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.role = users_db[user]["role"]
                st.session_state.data = load_data()
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.info("Login: owner/owner123 or employee/employee123")
    
    with tab2:
        st.subheader("Register")
        user = st.text_input("Username", key="reg_user")
        pwd = st.text_input("Password", type="password", key="reg_pass")
        role = st.radio("Role:", ["Owner", "Employee"], key="reg_role")
        
        if st.button("Register", key="reg_btn"):
            users_db = load_users()
            if not user or not pwd:
                st.error("Fill all fields")
            elif user in users_db:
                st.error("Username taken")
            else:
                users_db[user] = {"password": pwd, "role": role}
                save_users(users_db)
                st.success("Account created!")

else:
    st.title("Jacob's Bakery Inventory Manager")
    st.write(f"User: {st.session_state.user} | {st.session_state.role}")
    
    data = st.session_state.data
    
    # Sidebar
    st.sidebar.title("Menu")
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.rerun()
    
    if st.session_state.role == "Owner":
        action = st.sidebar.radio("Action:", ["View", "Add", "Update", "Delete", "Chat"], key="owner_menu")
        
        if action == "Add":
            st.subheader("Add Product")
            name = st.text_input("Product name", key="add_name")
            price = st.number_input("Price", min_value=0.01, step=0.01, key="add_price")
            stock = st.number_input("Stock", min_value=1, step=1, key="add_stock")
            
            if st.button("Add", key="add_btn"):
                if name.strip() and price > 0 and stock > 0:
                    if any(p["name"].lower() == name.lower() for p in data["products"]):
                        st.error("Already exists")
                    else:
                        new_id = max([p["id"] for p in data["products"]], default=0) + 1
                        data["products"].append({"id": new_id, "name": name.strip(), "price": price, "stock": stock})
                        save_data(data)
                        st.session_state.data = data
                        st.success("Added!")
                else:
                    st.error("Invalid input")
        
        elif action == "View":
            st.subheader("View Products")
            if data["products"]:
                for p in data["products"]:
                    st.write(f"ID {p['id']}: {p['name']} - ${p['price']} | {p['stock']} units")
            else:
                st.info("No products")
        
        elif action == "Update":
            st.subheader("Update Product")
            if data["products"]:
                pid = st.selectbox("Select", [p["id"] for p in data["products"]], format_func=lambda x: f"ID {x}: {next(p['name'] for p in data['products'] if p['id'] == x)}", key="upd_select")
                p = next(prod for prod in data["products"] if prod["id"] == pid)
                
                name = st.text_input("Name", value=p["name"], key="upd_name")
                price = st.number_input("Price", value=p["price"], step=0.01, key="upd_price")
                stock = st.number_input("Stock", value=p["stock"], step=1, key="upd_stock")
                
                if st.button("Update", key="upd_btn"):
                    if name.strip() and price > 0 and stock > 0:
                        p["name"] = name.strip()
                        p["price"] = price
                        p["stock"] = stock
                        save_data(data)
                        st.session_state.data = data
                        st.success("Updated!")
                    else:
                        st.error("Invalid input")
            else:
                st.info("No products")
        
        elif action == "Delete":
            st.subheader("Delete Product")
            if data["products"]:
                pid = st.selectbox("Select", [p["id"] for p in data["products"]], format_func=lambda x: f"ID {x}: {next(p['name'] for p in data['products'] if p['id'] == x)}", key="del_select")
                p = next(prod for prod in data["products"] if prod["id"] == pid)
                
                st.warning(f"Delete '{p['name']}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes", key="del_yes"):
                        data["products"] = [prod for prod in data["products"] if prod["id"] != pid]
                        save_data(data)
                        st.session_state.data = data
                        st.success("Deleted!")
                with col2:
                    st.button("No", key="del_no")
            else:
                st.info("No products")
        
        elif action == "Chat":
            st.subheader("Inventory Chat")
            q = st.text_input("Ask:", key="owner_chat")
            if q:
                q = q.lower()
                if "low stock" in q:
                    low = [p for p in data["products"] if p["stock"] < 5]
                    if low:
                        st.write("Low: " + ", ".join([f"{p['name']} ({p['stock']})" for p in low]))
                    else:
                        st.write("All good!")
                elif "how many" in q:
                    st.write(f"Products: {len(data['products'])}")
                elif "total value" in q:
                    total = sum(p["price"] * p["stock"] for p in data["products"])
                    st.write(f"Value: ${total:.2f}")
                elif "sales" in q:
                    if data["sales_log"]:
                        recent = [f"{s['product']}x{s['qty']}" for s in data["sales_log"][-3:]]
                        st.write("Recent: " + ", ".join(recent))
                    else:
                        st.write("No sales")
                else:
                    st.write("Try: low stock, how many, total value, sales")
    
    else:
        action = st.sidebar.radio("Action:", ["View", "Log Sale", "Low Stock", "Chat"], key="emp_menu")
        
        if action == "View":
            st.subheader("View Catalog")
            if data["products"]:
                for p in data["products"]:
                    st.write(f"{p['name']} - ${p['price']} | {p['stock']} units")
            else:
                st.info("No products")
        
        elif action == "Log Sale":
            st.subheader("Log Sale")
            if data["products"]:
                pid = st.selectbox("Select", [p["id"] for p in data["products"]], format_func=lambda x: next(p['name'] for p in data["products"] if p['id'] == x), key="sale_select")
                qty = st.number_input("Qty", min_value=1, step=1, key="sale_qty")
                
                if st.button("Log", key="sale_btn"):
                    p = next(prod for prod in data["products"] if prod["id"] == pid)
                    if p["stock"] >= qty:
                        p["stock"] -= qty
                        data["sales_log"].append({"product": p["name"], "qty": qty, "employee": st.session_state.user, "date": datetime.now().isoformat()})
                        save_data(data)
                        st.session_state.data = data
                        st.success(f"Sold {qty}x")
                    else:
                        st.error("Not enough stock!")
            else:
                st.info("No products")
        
        elif action == "Low Stock":
            st.subheader("Low Stock Alert")
            low = [p for p in data["products"] if p["stock"] < 5]
            if low:
                st.warning("Low stock:")
                for p in low:
                    st.write(f"{p['name']} - {p['stock']} units")
            else:
                st.info("All good!")
        
        elif action == "Chat":
            st.subheader("Inventory Chat")
            q = st.text_input("Ask:", key="emp_chat")
            if q:
                q = q.lower()
                if "low stock" in q:
                    low = [p for p in data["products"] if p["stock"] < 5]
                    if low:
                        st.write("Low: " + ", ".join([f"{p['name']} ({p['stock']})" for p in low]))
                    else:
                        st.write("All good!")
                elif "how many" in q:
                    st.write(f"Products: {len(data['products'])}")
                elif "total value" in q:
                    total = sum(p["price"] * p["stock"] for p in data["products"])
                    st.write(f"Value: ${total:.2f}")
                elif "sales" in q:
                    if data["sales_log"]:
                        recent = [f"{s['product']}x{s['qty']}" for s in data["sales_log"][-3:]]
                        st.write("Recent: " + ", ".join(recent))
                    else:
                        st.write("No sales")
                else:
                    st.write("Try: low stock, how many, total value, sales")