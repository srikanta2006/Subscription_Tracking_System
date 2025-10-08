# app.py
import streamlit as st
import pandas as pd
from datetime import date

# Import your actual services
from src.services.user_service import UserService
from src.services.subscription_service import SubscriptionService
from src.services.payment_service import PaymentService

# --- Page Configuration ---
st.set_page_config(page_title="Subscription Tracker", layout="wide", page_icon="💳")

# --- Custom CSS for a Polished UI ---
st.markdown("""
<style>
    /* General body styling */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Main containers for a card-like effect */
    div[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 25px;
        background-color: #1a1c2e;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease-in-out;
    }
    div[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"]:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* Style for metric cards */
    div[data-testid="stMetric"] {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        background: linear-gradient(145deg, #232733, #1a1c2e);
    }

    /* Primary button style */
    .stButton > button {
        border-radius: 20px;
        border: 1px solid #7792E3;
        background-color: transparent;
        color: #7792E3;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #7792E3;
        color: white;
        border-color: #7792E3;
    }
    .stButton > button:focus {
        box-shadow: 0 0 0 2px rgba(119, 146, 227, 0.5) !important;
    }
    
    /* Custom divider */
    hr {
        margin-top: 20px !important;
        margin-bottom: 20px !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Service Initialization ---
user_service = UserService()
subscription_service = SubscriptionService()
payment_service = PaymentService()


# --- Caching ---
@st.cache_data(ttl=300) # Cache data for 5 minutes
def load_data():
    """Fetches all data from the services and caches the result."""
    users = user_service.user_dao.get_all_users()
    subscriptions = subscription_service.subscription_dao.get_all_subscriptions()
    payments = payment_service.payment_dao.get_all_payments()
    return users, subscriptions, payments


# --- Main App ---
st.title("💳 Subscription Tracker Dashboard")
st.markdown("An elegant solution to manage users, subscriptions, and payments seamlessly.")

try:
    users, subscriptions, payments = load_data()
except Exception as e:
    st.error(f"🔌 Failed to connect to the database. Please check your services and secrets.toml file. Error: {e}")
    st.stop()

# Create mappings for user-friendly selectboxes
user_map = {user['name']: user['id'] for user in users}
subscription_map = {}
if users and subscriptions:
    user_id_to_name = {u['id']: u['name'] for u in users}
    subscription_map = {f"{sub['name']} (User: {user_id_to_name.get(sub['user_id'], 'N/A')})": sub['id'] for sub in subscriptions}


# --- Main Navigation Tabs ---
dash_tab, user_tab, sub_tab, payment_tab, insight_tab = st.tabs([
    "🏠 Dashboard", "👤 User Management", "📦 Subscription Hub", "💸 Payment Center", "💡 Analytics"
])


# --- Dashboard Tab ---
with dash_tab:
    st.header("🚀 At a Glance")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("👥 Total Users", len(users))
    with col2: st.metric("📦 Active Subscriptions", len(subscriptions))
    with col3: st.metric("💳 Payments Recorded", len(payments))
    with col4:
        completed_payments = sum(float(p["amount"]) for p in payments if p["status"] == "Completed")
        st.metric("💰 Total Revenue", f"₹ {completed_payments:,.2f}")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("📈 Subscriptions per User")
            if subscriptions:
                sub_df = pd.DataFrame(subscriptions)
                user_names_map = {u['id']: u['name'] for u in users}
                sub_df['user_name'] = sub_df['user_id'].map(user_names_map)
                st.bar_chart(sub_df['user_name'].value_counts(), color="#7792E3")
            else:
                st.info("No subscription data available.")
    with col2:
        with st.container(border=True):
            st.subheader("🕒 Recent Payments")
            if payments:
                df = pd.DataFrame(payments).sort_values("payment_date", ascending=False).head(5)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No payments recorded yet.")


# --- User Management Tab ---
with user_tab:
    with st.container(border=True):
        add_user_tab, list_user_tab, delete_user_tab = st.tabs(["➕ Add User", "👥 List Users", "❌ Delete User"])
        
        with add_user_tab:
            st.subheader("Create a New User Profile")
            with st.form("add_user_form"):
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                if st.form_submit_button("✅ Create User"):
                    if not name or not email: st.error("Name and Email are required.")
                    elif not user_service.is_valid_email(email): st.error("Invalid email format.")
                    elif user_service.user_dao.get_user_by_email(email): st.error("Email already exists.")
                    else:
                        if user_service.user_dao.create_user(name, email):
                            st.success(f"User '{name}' added successfully!")
                            st.cache_data.clear()
                            st.rerun()
                        else: st.error("Failed to add user.")

        with list_user_tab:
            st.subheader("Registered User Accounts")
            st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)

        with delete_user_tab:
            st.subheader("Remove a User")
            if not users:
                st.warning("No users available to delete.")
            else:
                user_to_delete = st.selectbox("Select User to Remove", options=user_map.keys())
                if st.button("🗑️ Delete User", type="primary"):
                    user_id = user_map[user_to_delete]
                    if subscription_service.subscription_dao.get_subscriptions_by_user(user_id):
                        st.warning("⚠️ User still has active subscriptions. Please remove them first.")
                    else:
                        if user_service.user_dao.delete_user(user_id):
                            st.success(f"User '{user_to_delete}' deleted successfully.")
                            st.cache_data.clear()
                            st.rerun()
                        else: st.error("Failed to delete user.")

# --- Subscription Management Tab ---
with sub_tab:
    with st.container(border=True):
        add_sub_tab, view_sub_tab = st.tabs(["➕ Add Subscription", "📜 View Subscriptions"])

        with add_sub_tab:
            st.subheader("Add Subscription for a User")
            if not users:
                st.warning("Please add a user before adding subscriptions.")
            else:
                with st.form("add_subscription_form"):
                    user_name = st.selectbox("Select User", options=user_map.keys())
                    sub_name = st.text_input("Subscription Name (e.g., Netflix, Spotify)")
                    col1, col2 = st.columns(2)
                    with col1:
                        plan_type = st.selectbox("Plan Type", ["monthly", "yearly"])
                        start_date = st.date_input("Start Date")
                    with col2:
                        cost = st.number_input("Cost (₹)", min_value=0.0, format="%.2f")
                        end_date = st.date_input("End Date")

                    if st.form_submit_button("✅ Add Subscription"):
                        user_id = user_map[user_name]
                        success = subscription_service.subscription_dao.add_subscription(
                            user_id=user_id, name=sub_name, plan_type=plan_type, cost=cost,
                            start_date=str(start_date), end_date=str(end_date), status="Active"
                        )
                        if success:
                            st.success(f"Subscription '{sub_name}' added for {user_name}.")
                            st.cache_data.clear()
                            st.rerun()
                        else: st.error("Failed to add subscription.")
        
        with view_sub_tab:
            st.subheader("View Subscriptions by User")
            if not users:
                st.warning("No users available.")
            else:
                user_to_view = st.selectbox("Select a User", options=user_map.keys())
                user_id = user_map[user_to_view]
                user_subs = subscription_service.subscription_dao.get_subscriptions_by_user(user_id)
                if user_subs:
                    st.dataframe(pd.DataFrame(user_subs), use_container_width=True, hide_index=True)
                else:
                    st.info(f"{user_to_view} has no subscriptions.")

# --- Payment Management Tab ---
with payment_tab:
    with st.container(border=True):
        add_pay_tab, view_pay_tab = st.tabs(["💸 Add Payment", "📑 View Payments"])

        with add_pay_tab:
            st.subheader("Record a New Payment")
            if not subscriptions:
                st.warning("Please add a subscription before recording a payment.")
            else:
                with st.form("add_payment_form"):
                    sub_choice = st.selectbox("Select Subscription", options=subscription_map.keys())
                    col1, col2 = st.columns(2)
                    with col1:
                        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
                        method = st.selectbox("Payment Method", ["UPI", "Card", "PayPal", "Other"])
                    with col2:
                        status = st.selectbox("Status", ["Completed", "Pending", "Failed"])
                        
                    if st.form_submit_button("✅ Record Payment"):
                        sub_id = subscription_map[sub_choice]
                        if payment_service.payment_dao.insert_payment(sub_id, amount, method, status):
                            st.success(f"Payment of ₹{amount} recorded for the selected subscription.")
                            st.cache_data.clear()
                            st.rerun()
                        else: st.error("Failed to add payment.")

        with view_pay_tab:
            st.subheader("View Payments for a Subscription")
            if not subscriptions:
                st.warning("No subscriptions available.")
            else:
                sub_to_view = st.selectbox("Select Subscription", options=subscription_map.keys())
                sub_id = subscription_map[sub_to_view]
                sub_payments = payment_service.payment_dao.get_payments_by_subscription(sub_id)
                if sub_payments:
                    st.dataframe(pd.DataFrame(sub_payments), use_container_width=True, hide_index=True)
                else:
                    st.info(f"No payments found for the selected subscription.")

# --- Analytics Tab ---
with insight_tab:
    with st.container(border=True):
        st.header("💡 User Spending Analysis")
        if not users:
            st.warning("No users available for analysis.")
        else:
            user_to_analyze = st.selectbox("Select a User to Analyze", options=user_map.keys())
            user_id = user_map[user_to_analyze]
            user_subs = subscription_service.subscription_dao.get_subscriptions_by_user(user_id)
            if not user_subs:
                st.info(f"{user_to_analyze} has no subscriptions to analyze.")
            else:
                payments_data = []
                for sub in user_subs:
                    for payment in payment_service.payment_dao.get_payments_by_subscription(sub["id"]):
                        if payment['status'] == 'Completed':
                            payments_data.append({"subscription": sub["name"], "amount": float(payment["amount"])})
                
                if not payments_data:
                    st.info(f"No completed payments found for {user_to_analyze}.")
                else:
                    df = pd.DataFrame(payments_data)
                    total_spend = df['amount'].sum()
                    st.metric(label=f"Total Spend for {user_to_analyze}", value=f"₹ {total_spend:,.2f}")
                    st.bar_chart(df.groupby('subscription')['amount'].sum(), color="#FF4B4B")