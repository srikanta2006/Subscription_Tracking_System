import streamlit as st
import pandas as pd
from src.services.user_service import UserService
from src.services.subscription_service import SubscriptionService
from src.services.payment_service import PaymentService

# Initialize services
user_service = UserService()
subscription_service = SubscriptionService()
payment_service = PaymentService()

st.set_page_config(page_title="Subscription Tracker", layout="wide")
st.title("📊 Subscription Tracker")

# Sidebar navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/942/942748.png", width=60)
st.sidebar.markdown("### Welcome 👋\nManage users, subscriptions & payments seamlessly.")

menu = {
    "🏠 Dashboard": ["Overview"],
    "👤 Users": ["Add User", "List Users", "Delete User"],
    "📦 Subscriptions": ["Add Subscription", "View Subscriptions"],
    "💳 Payments": ["Add Payment", "View Payments"],
    "💰 Insights": ["Total Spend"],
}
section = st.sidebar.selectbox("Select Section", list(menu.keys()))
choice = st.sidebar.radio("Choose Action", menu[section])

# ------------------- Dashboard -------------------
if choice == "Overview":
    st.header("📊 Dashboard Overview")

    # Fetch data
    users = user_service.user_dao.get_all_users()
    subs = subscription_service.subscription_dao.get_all_subscriptions()
    payments = payment_service.payment_dao.get_all_payments()

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Users", len(users))
    with col2:
        st.metric("📦 Subscriptions", len(subs))
    with col3:
        st.metric("💳 Payments", len(payments))
    with col4:
        completed_payments = [float(p["amount"]) for p in payments if p["status"] == "Completed"]
        st.metric("💰 Total Revenue", f"₹ {sum(completed_payments):.2f}")

    st.divider()

    # Subscriptions by user
    st.subheader("📦 Subscriptions by User")
    if subs:
        sub_df = pd.DataFrame(subs)
        sub_count = sub_df.groupby("user_id").size().reset_index(name="count")
        st.bar_chart(sub_count.set_index("user_id"))
    else:
        st.info("No subscriptions yet.")

    # Revenue distribution
    st.subheader("💰 Revenue by Subscription")
    if payments and subs:
        pay_data = []
        for s in subs:
            sub_payments = payment_service.payment_dao.get_payments_by_subscription(s["id"])
            for p in sub_payments:
                if p["status"] == "Completed":
                    pay_data.append({"subscription": s["name"], "amount": float(p["amount"])})

        if pay_data:
            df = pd.DataFrame(pay_data)
            st.bar_chart(df.groupby("subscription")["amount"].sum())
        else:
            st.info("No completed payments yet.")
    else:
        st.info("No payment data available.")

    # Recent payments
    st.subheader("🕒 Recent Payments")
    if payments:
        # Corrected line
        df = pd.DataFrame(payments).sort_values("payment_date", ascending=False).head(5)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No payments recorded yet.")

# ------------------- Other Pages -------------------
elif choice == "Add User":
    st.header("➕ Add User")
    with st.form("add_user_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        submit = st.form_submit_button("Add User")
    if submit:
        if not name or not email:
            st.error("Name and Email are required!")
        elif not user_service.is_valid_email(email):
            st.error("Invalid email format")
        elif user_service.user_dao.get_user_by_email(email):
            st.error("Email already exists")
        else:
            success = user_service.user_dao.create_user(name, email)
            if success:
                st.success(f"✅ User '{name}' added successfully!")
            else:
                st.error("❌ Failed to add user")

elif choice == "List Users":
    st.header("👥 Registered Users")
    users = user_service.user_dao.get_all_users()
    if users:
        df = pd.DataFrame(users)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users found.")

elif choice == "Delete User":
    st.header("❌ Delete User")
    user_id = st.number_input("User ID to Delete", min_value=1, step=1)
    if st.button("Delete User"):
        user = user_service.user_dao.get_user_by_id(user_id)
        if not user:
            st.error("User does not exist.")
        elif subscription_service.subscription_dao.get_subscriptions_by_user(user_id):
            st.warning("⚠️ User still has subscriptions. Cannot delete.")
        else:
            success = user_service.user_dao.delete_user(user_id)
            if success:
                st.success(f"✅ User ID {user_id} deleted successfully.")
            else:
                st.error("❌ Failed to delete user.")

elif choice == "Add Subscription":
    st.header("➕ Add Subscription for User")
    col1, col2 = st.columns(2)
    with col1:
        user_id = st.number_input("User ID", min_value=1, step=1)
        default_subs = subscription_service.default_dao.get_all_default_subscriptions()
        sub_options = [f"{s['name']} ({s['plan_type']} - {s['cost']})" for s in default_subs]
        sub_choice = st.selectbox("Choose a Subscription", sub_options + ["Custom Subscription"])
    with col2:
        if sub_choice == "Custom Subscription":
            sub_name = st.text_input("Subscription Name")
            plan_type = st.selectbox("Plan Type", ["monthly", "yearly"])
            cost = st.number_input("Cost", min_value=0.0, step=0.01)
        else:
            idx = sub_options.index(sub_choice)
            sub_name = default_subs[idx]["name"]
            plan_type = default_subs[idx]["plan_type"]
            cost = default_subs[idx]["cost"]

        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

    if st.button("Add Subscription"):
        subscription_service.subscription_dao.add_subscription(
            user_id=user_id,
            name=sub_name,
            plan_type=plan_type,
            cost=cost,
            start_date=str(start_date),
            end_date=str(end_date),
            status="Active"
        )
        st.success(f"✅ Subscription '{sub_name}' added for User ID {user_id}")

elif choice == "View Subscriptions":
    st.header("📜 Subscriptions")
    user_id = st.number_input("Enter User ID", min_value=1, step=1)
    if st.button("View Subscriptions"):
        subs = subscription_service.subscription_dao.get_subscriptions_by_user(user_id)
        if subs:
            df = pd.DataFrame(subs)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No subscriptions found for this user.")

elif choice == "Add Payment":
    st.header("💳 Add Payment")
    col1, col2 = st.columns(2)
    with col1:
        subscription_id = st.number_input("Subscription ID", min_value=1, step=1)
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
    with col2:
        method = st.selectbox("Payment Method", ["UPI", "Card", "PayPal", "Other"])
        status = st.selectbox("Status", ["Completed", "Pending", "Failed"])

    if st.button("Add Payment"):
        result = payment_service.payment_dao.insert_payment(
            subscription_id, amount, method, status
        )
        if result:
            st.success(f"✅ Payment of {amount} added for Subscription ID {subscription_id}")
        else:
            st.error("❌ Failed to add payment.")

elif choice == "View Payments":
    st.header("📑 Payments")
    subscription_id = st.number_input("Enter Subscription ID", min_value=1, step=1)
    if st.button("View Payments"):
        payments = payment_service.payment_dao.get_payments_by_subscription(subscription_id)
        if payments:
            df = pd.DataFrame(payments)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No payments found for this subscription.")

elif choice == "Total Spend":
    st.header("💰 Total Spend Analysis")
    user_id = st.number_input("Enter User ID", min_value=1, step=1)
    if st.button("Calculate"):
        user = user_service.user_dao.get_user_by_id(user_id)
        if not user:
            st.error("User does not exist.")
        else:
            subs = subscription_service.subscription_dao.get_subscriptions_by_user(user_id)
            if not subs:
                st.info("User has no subscriptions.")
            else:
                sub_ids = [s["id"] for s in subs]
                total = payment_service.payment_dao.get_total_spend_for_subscriptions(sub_ids)
                st.metric(label=f"Total Spend for {user['name']}", value=f"₹ {total:.2f}")

                payments = []
                for s in subs:
                    p = payment_service.payment_dao.get_payments_by_subscription(s["id"])
                    if p:
                        for pay in p:
                            payments.append({"subscription": s["name"], "amount": float(pay["amount"])})
                if payments:
                    df = pd.DataFrame(payments)
                    st.bar_chart(df.set_index("subscription"))
