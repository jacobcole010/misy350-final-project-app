import streamlit as st
from datetime import datetime

from ai_assistant import AIChatAssistant
from data_layer import DataManager
from services import AuthService, InventoryService


st.set_page_config(page_title="Jacob's Bakery Inventory Manager", layout="wide")


def setup_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.name = ""
        st.session_state.messages = []


def show_test_accounts():
    st.subheader("Accounts")
    st.info("Owner\n\nUsername: owner\n\nPassword: owner123")
    st.info("Employee\n\nUsername: employee\n\nPassword: employee123")
    st.info("Manager\n\nUsername: manager\n\nPassword: manager123")


def show_login(auth_service):
    st.title("Jacob's Bakery Inventory Manager")
    st.write("Manage bakery products, inventory, and sales.")

    left, right = st.columns([2, 1])

    with left:
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                login = st.form_submit_button("Login")

            if login:
                user = auth_service.validate_login(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user.username
                    st.session_state.role = user.role
                    st.session_state.name = user.name
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tab2:
            with st.form("register_form"):
                username = st.text_input("New username", key="register_username")
                name = st.text_input("Your name", key="register_name")
                password = st.text_input("New password", type="password", key="register_password")
                role = st.selectbox("Role", ["Employee", "Owner"], key="register_role")
                register = st.form_submit_button("Register")

            if register:
                success, message = auth_service.register_user(username, password, role, name)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    with right:
        show_test_accounts()


def show_sidebar():
    if st.session_state.role == "Owner":
        st.sidebar.title("Owner/Manager Console")
    else:
        st.sidebar.title("Employee Workspace")

    st.sidebar.write(f"{st.session_state.name}")
    st.sidebar.write(f"Role: {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.name = ""
        st.session_state.messages = []
        st.rerun()

    if st.session_state.role == "Owner":
        return st.sidebar.radio("Go to", ["Owner Dashboard", "Manage Products", "Log Sale", "Sales Log", "AI Assistant"])

    return st.sidebar.radio("Go to", ["My Shift Dashboard", "Product Lookup", "Log Sale", "Low Stock", "AI Assistant"])


def show_owner_dashboard(inventory_service):
    st.title("Owner/Manager Dashboard")
    st.caption("Business performance, inventory value, and management alerts.")
    summary = inventory_service.get_summary()
    sales = inventory_service.get_sales()
    products = inventory_service.get_products()
    average_sale = summary["sales_total"] / len(sales) if sales else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Products Managed", summary["products"])
    col2.metric("Low-Stock Items", summary["low_stock"])
    col3.metric("Inventory Value", f"${summary['inventory_value']:.2f}")
    col4.metric("Average Sale", f"${average_sale:.2f}")

    st.divider()

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Inventory Control")
        st.table(inventory_service.get_product_rows())

        st.subheader("Category Value")
        category_rows = []
        categories = sorted(set(product.category for product in products))
        for category in categories:
            category_products = [product for product in products if product.category == category]
            category_rows.append(
                {
                    "Category": category,
                    "Products": len(category_products),
                    "Units": sum(product.stock for product in category_products),
                    "Value": f"${sum(product.get_value() for product in category_products):.2f}",
                }
            )

        if category_rows:
            st.table(category_rows)
        else:
            st.info("No category data available.")

    with right:
        st.subheader("Management Alerts")
        low_items = inventory_service.get_low_stock_items()
        if low_items:
            for item in low_items:
                st.warning(f"{item.name}: {item.stock} left, order {5 - item.stock} or more")
        else:
            st.success("No low-stock items.")

        st.subheader("Sales Overview")
        st.metric("Total Sales Logged", f"${summary['sales_total']:.2f}")
        recent_sales = inventory_service.get_recent_sales()
        if recent_sales:
            for sale in recent_sales:
                st.write(f"{sale.date}: {sale.product_name}, {sale.quantity} sold by {sale.employee}")
        else:
            st.info("No sales yet.")


def show_employee_dashboard(inventory_service):
    st.title("My Shift Dashboard")
    st.caption("Quick selling tools, product availability, and items that need attention.")

    products = inventory_service.get_products()
    low_items = inventory_service.get_low_stock_items()
    sales = inventory_service.get_sales()
    today = datetime.now().strftime("%Y-%m-%d")
    my_sales = [sale for sale in sales if sale.employee == st.session_state.username]
    todays_sales = [sale for sale in my_sales if sale.date == today]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Products Available", len(products))
    col2.metric("Items to Watch", len(low_items))
    col3.metric("My Sales Logged", len(my_sales))
    col4.metric("My Sales Today", len(todays_sales))

    st.divider()

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Product Lookup")
        product_rows = []
        for product in products:
            status = "Restock soon" if product.is_low_stock() else "Ready to sell"
            product_rows.append(
                {
                    "Name": product.name,
                    "Category": product.category,
                    "Price": f"${product.price:.2f}",
                    "Stock": product.stock,
                    "Status": status,
                }
            )
        st.table(product_rows)

    with right:
        st.subheader("Shift Priorities")
        if low_items:
            for item in low_items:
                st.warning(f"Tell a manager: {item.name} has {item.stock} left")
        else:
            st.success("No low-stock items right now.")

        st.subheader("My Recent Sales")
        if my_sales:
            for sale in my_sales[-3:]:
                st.write(f"{sale.date}: {sale.quantity} {sale.product_name}")
        else:
            st.info("You have not logged any sales yet.")


def show_product_management(inventory_service):
    st.title("Product Management")

    tab1, tab2, tab3 = st.tabs(["Add", "Update", "Delete"])

    with tab1:
        with st.form("add_product"):
            name = st.text_input("Product name", key="add_product_name")
            category = st.text_input("Category", key="add_product_category")
            price = st.number_input("Price", min_value=0.01, step=0.25, key="add_product_price")
            stock = st.number_input("Stock", min_value=0, step=1, key="add_product_stock")
            submitted = st.form_submit_button("Add Product")

        if submitted:
            success, message = inventory_service.add_product(name, category, price, stock)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    products = inventory_service.get_products()
    if not products:
        st.info("No products yet.")
        return

    choices = {f"{p.name} (ID {p.item_id})": p.item_id for p in products}

    with tab2:
        selected = st.selectbox("Choose product", choices.keys(), key="update_choice")
        product = inventory_service.find_product(choices[selected])

        with st.form("update_product"):
            name = st.text_input("Product name", value=product.name, key="update_product_name")
            category = st.text_input("Category", value=product.category, key="update_product_category")
            price = st.number_input("Price", min_value=0.01, value=float(product.price), step=0.25, key="update_product_price")
            stock = st.number_input("Stock", min_value=0, value=int(product.stock), step=1, key="update_product_stock")
            submitted = st.form_submit_button("Update Product")

        if submitted:
            success, message = inventory_service.update_product(product.item_id, name, category, price, stock)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with tab3:
        selected = st.selectbox("Choose product", choices.keys(), key="delete_choice")
        product = inventory_service.find_product(choices[selected])
        st.warning(f"Delete {product.name}?")

        if st.button("Delete Product"):
            success, message = inventory_service.delete_product(product.item_id)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def show_catalog(inventory_service):
    st.title("Product Lookup")
    st.caption("Employee view: prices, stock levels, and product status.")

    rows = []
    for product in inventory_service.get_products():
        rows.append(
            {
                "Name": product.name,
                "Category": product.category,
                "Price": f"${product.price:.2f}",
                "Stock": product.stock,
                "Status": "Restock soon" if product.is_low_stock() else "Ready to sell",
            }
        )

    st.table(rows)


def show_log_sale(inventory_service):
    st.title("Log Sale")
    products = inventory_service.get_products()

    if not products:
        st.info("No products available.")
        return

    choices = {f"{p.name} - {p.stock} in stock": p.item_id for p in products}

    with st.form("log_sale"):
        selected = st.selectbox("Product", choices.keys(), key="sale_product_choice")
        quantity = st.number_input("Quantity", min_value=1, step=1, key="sale_quantity")
        submitted = st.form_submit_button("Log Sale")

    if submitted:
        success, message = inventory_service.log_sale(choices[selected], quantity, st.session_state.username)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)


def show_sales_log(inventory_service):
    st.title("Sales Log")
    sales = inventory_service.get_sales_rows()
    if sales:
        st.table(sales)
    else:
        st.info("No sales have been logged yet.")


def show_low_stock(inventory_service):
    st.title("Low Stock")
    low_items = inventory_service.get_low_stock_rows()
    if low_items:
        st.table(low_items)
    else:
        st.success("All products are stocked above the alert level.")


def show_ai_assistant(ai_assistant):
    st.title("AI Inventory Assistant")
    st.write("Ask about restocking, sales, inventory value, or product ideas.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Ask a question")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        answer = ai_assistant.generate_response(question, st.session_state.role)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)


def show_app(inventory_service, ai_assistant):
    page = show_sidebar()

    if page == "Owner Dashboard":
        show_owner_dashboard(inventory_service)
    elif page == "My Shift Dashboard":
        show_employee_dashboard(inventory_service)
    elif page == "Manage Products":
        show_product_management(inventory_service)
    elif page == "Product Lookup":
        show_catalog(inventory_service)
    elif page == "Log Sale":
        show_log_sale(inventory_service)
    elif page == "Sales Log":
        show_sales_log(inventory_service)
    elif page == "Low Stock":
        show_low_stock(inventory_service)
    elif page == "AI Assistant":
        show_ai_assistant(ai_assistant)


def main():
    setup_session()
    data_manager = DataManager()
    auth_service = AuthService(data_manager)
    inventory_service = InventoryService(data_manager)
    ai_assistant = AIChatAssistant(inventory_service)

    if st.session_state.logged_in:
        show_app(inventory_service, ai_assistant)
    else:
        show_login(auth_service)


main()
