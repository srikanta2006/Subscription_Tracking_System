import streamlit as st
from src.services.user_service import user_service
from src.services.subscription_service import subscription_service
from src.services.payment_service import payment_service

st.title("Subscription Tracker")

# ---- Sidebar Menu ----
menu = [
    "Add User",
    "List Users",
    "Add Subscription for a User",
    "View Subscriptions for a User",
    "Add Payment for a Subscription",
    "View Payments for a Subscription",
    "Delete User",
    "Total Spend of the User",
]

choice = st.sidebar.selectbox("Select Action", menu)

# -------------------- Add User --------------------
if choice == "Add User":
    st.header("Add User")
    with st.form("add_user"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        if st.form_submit_button("Add User"):
            try:
                user_service.add_user(name, email)
                st.success(f"User '{name}' added successfully!")
            except Exception as e:
                st.error(f"Failed to add user: {e}")

# -------------------- List Users --------------------
elif choice == "List Users":
    st.header("All Users")
    users = user_service.list_users()
    if users:
        for u in users:
            st.write(f"{u['user_id']}: {u['name']} — Email: {u['email']}")
    else:
        st.info("No users found.")

# -------------------- Add Subscription --------------------
elif choice == "Add Subscription for a User":
    st.header("Add Subscription")
    users = user_service.list_users()
    if not users:
        st.warning("Add users first.")
    else:
        with st.form("add_subscription"):
            user_ids = [u["user_id"] for u in users]
            user_id = st.selectbox("Select User", user_ids)
            name = st.text_input("Subscription Name")
            amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            status = st.selectbox("Status", ["Active", "Expired", "Pending"])
            if st.form_submit_button("Add Subscription"):
                try:
                    subscription_service.add_subscription_for_user(
                        user_id, name, amount, str(start_date), str(end_date), status
                    )
                    st.success("Subscription added successfully!")
                except Exception as e:
                    st.error(f"Failed: {e}")

# -------------------- View Subscriptions --------------------
elif choice == "View Subscriptions for a User":
    st.header("View Subscriptions")
    users = user_service.list_users()
    if not users:
        st.warning("Add users first.")
    else:
        user_ids = [u["user_id"] for u in users]
        user_id = st.selectbox("Select User", user_ids)
        subs = subscription_service.view_subscriptions_for_user(user_id)
        if subs:
            for sub in subs:
                st.write(
                    f"{sub['sub_id']}: {sub['name']} — ₹{sub['amount']} — "
                    f"Start: {sub['start_date']} — End: {sub['end_date']} — Status: {sub['status']}"
                )
        else:
            st.info("No subscriptions for this user.")

# -------------------- Add Payment --------------------
elif choice == "Add Payment for a Subscription":
    st.header("Add Payment")
    subs = subscription_service.list_subscriptions()
    if not subs:
        st.warning("Add subscriptions first.")
    else:
        with st.form("add_payment"):
            sub_ids = [s["sub_id"] for s in subs]
            sub_id = st.selectbox("Select Subscription", sub_ids)
            amount = st.number_input("Payment Amount (₹)", min_value=0.0, format="%.2f")
            date = st.date_input("Payment Date")
            if st.form_submit_button("Add Payment"):
                try:
                    payment_service.add_payment_for_subscription(
                        sub_id, float(amount), str(date)
                    )
                    st.success("Payment added successfully!")
                except Exception as e:
                    st.error(f"Failed: {e}")

# -------------------- View Payments --------------------
elif choice == "View Payments for a Subscription":
    st.header("View Payments")
    subs = subscription_service.list_subscriptions()
    if not subs:
        st.warning("Add subscriptions first.")
    else:
        sub_ids = [s["sub_id"] for s in subs]
        sub_id = st.selectbox("Select Subscription", sub_ids)
        payments = payment_service.view_payments_for_subscription(sub_id)
        if payments:
            for p in payments:
                st.write(f"{p['payment_id']}: ₹{p['amount']} — Date: {p['date']}")
        else:
            st.info("No payments for this subscription.")

# -------------------- Delete User --------------------
elif choice == "Delete User":
    st.header("Delete User")
    users = user_service.list_users()
    if not users:
        st.warning("No users to delete.")
    else:
        user_ids = [u["user_id"] for u in users]
        user_id = st.selectbox("Select User to Delete", user_ids)
        if st.button("Delete User"):
            try:
                user_service.delete_user(user_id)
                st.success(f"User {user_id} deleted successfully!")
            except Exception as e:
                st.error(f"Failed: {e}")

# -------------------- Total Spend --------------------
elif choice == "Total Spend of the User":
    st.header("Total Spend")
    users = user_service.list_users()
    if not users:
        st.warning("Add users first.")
    else:
        user_ids = [u["user_id"] for u in users]
        user_id = st.selectbox("Select User", user_ids)
        total = subscription_service.calculate_total_spend(user_id)
        st.write(f"Total spend for User {user_id}: ₹{total}")
