import streamlit as st

st.set_page_config(page_title=" Jacob's Snack Shop")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.cart = []

users = {"jacob": ("password", "Customer"), "admin": ("admin123", "Owner")}

st.title("Jacob'sSnack Shop")

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in users and users[username][0] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.role = users[username][1]
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        st.subheader("Register")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        role = st.radio("I am a:", ["Customer", "Owner"])
        
        if st.button("Register"):
            if new_user and new_pass:
                users[new_user] = (new_pass, role)
                st.success("Account created! Please login.")
            else:
                st.error("Fill all fields")

else:
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.cart = []
            st.rerun()
    
    st.write(f"**Logged in as: {st.session_state.user} ({st.session_state.role})**")
    st.divider()
    
    if st.session_state.role == "Customer":
        st.subheader("Browse Snacks")
        
        snacks = {
            "Chips": 2.99,
            "Pretzels": 3.49,
            "Popcorn": 4.99,
            "Cookies": 3.99,
            "Trail Mix": 5.99,
            "Candy": 2.49,
            "Soda": 1.99,
            "Iced Tea": 2.49,
            "Juice": 3.49,
            "Water Bottle": 1.49
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Snacks:**")
            for snack in ["Chips", "Pretzels", "Popcorn", "Cookies", "Trail Mix", "Candy"]:
                if st.button(f"Add {snack} (${snacks[snack]})"):
                    st.session_state.cart.append({"item": snack, "price": snacks[snack]})
                    st.success(f"Added {snack} to cart!")
        
        with col2:
            st.write("**Drinks:**")
            for drink in ["Soda", "Iced Tea", "Juice", "Water Bottle"]:
                if st.button(f"Add {drink} (${snacks[drink]})"):
                    st.session_state.cart.append({"item": drink, "price": snacks[drink]})
                    st.success(f"Added {drink} to cart!")
        
        st.divider()
        
        if st.session_state.cart:
            st.subheader("Your Cart")
            total = 0
            for idx, item in enumerate(st.session_state.cart):
                st.write(f"{item['item']} - ${item['price']}")
                total += item['price']
            
            st.write(f"**Total: ${total:.2f}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear Cart"):
                    st.session_state.cart = []
                    st.rerun()
            
            with col2:
                if st.button("Place Order"):
                    st.success(f"Order placed! Total: ${total:.2f}")
                    st.session_state.cart = []
                    st.rerun()
        else:
            st.info("Cart is empty. Add items to get started!")
    
    else:
        st.subheader("Inventory")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Snacks:**")
            st.write("Chips: 50 units")
            st.write("Pretzels: 30 units")
            st.write("Popcorn: 20 units")
            st.write("Cookies: 40 units")
            st.write("Trail Mix: 25 units")
            st.write("Candy: 60 units")
        
        with col2:
            st.write("**Drinks:**")
            st.write("Soda: 80 units")
            st.write("Iced Tea: 45 units")
            st.write("Juice: 35 units")
            st.write("Water Bottle: 100 units")