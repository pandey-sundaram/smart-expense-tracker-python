import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
from database import init_db, get_connection
from auth import signup, login
from ai import auto_category

st.set_page_config(page_title="Expense Tracker Pro", layout="wide")
init_db()

# ---- Custom Modern Styling ----
st.markdown("""
<style>
body {background: linear-gradient(to right, #0f2027, #203a43, #2c5364);}
.metric-card {
    background-color: #1e2a38;
    padding: 20px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:
    st.title("💰 Expense Tracker Pro")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(user, pwd):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        st.subheader("Signup")
        new_user = st.text_input("New Username")
        new_pwd = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if signup(new_user, new_pwd):
                st.success("Account created!")
            else:
                st.error("User already exists")

# ---------------- DASHBOARD ----------------
else:
    st.title(f"📊 Dashboard — {st.session_state.username}")

    conn = get_connection()
    df = pd.read_sql_query(
        f"SELECT * FROM expenses WHERE username='{st.session_state.username}'",
        conn
    )

    # Sidebar
    st.sidebar.header("Add Expense")
    description = st.sidebar.text_input("Description")
    amount = st.sidebar.number_input("Amount", min_value=0.0)

    if st.sidebar.button("Add"):
        category = auto_category(description)
        conn.execute("INSERT INTO expenses (username,date,category,amount) VALUES (?,?,?,?)",
                     (st.session_state.username,
                      datetime.now().strftime("%Y-%m-%d"),
                      category,
                      amount))
        conn.commit()
        st.rerun()

    # ---- Budget Section ----
    st.sidebar.header("Set Monthly Budget")
    budget = st.sidebar.number_input("Budget ₹", min_value=0.0)

    if st.sidebar.button("Save Budget"):
        conn.execute("INSERT OR REPLACE INTO budgets (username, monthly_budget) VALUES (?,?)",
                     (st.session_state.username, budget))
        conn.commit()
        st.success("Budget Saved")

    # ---- Metrics ----
    total_spent = df["amount"].sum() if not df.empty else 0
    col1, col2 = st.columns(2)
    col1.metric("Total Spending", f"₹ {round(total_spent,2)}")

    budget_df = pd.read_sql_query(
        f"SELECT monthly_budget FROM budgets WHERE username='{st.session_state.username}'",
        conn
    )

    if not budget_df.empty:
        monthly_budget = budget_df["monthly_budget"].iloc[0]
        col2.metric("Monthly Budget", f"₹ {monthly_budget}")
        if total_spent > monthly_budget:
            st.error("⚠ Budget Exceeded!")
        else:
            st.success("Within Budget")

    st.divider()

    # ---- Filtering ----
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        month_filter = st.selectbox("Filter by Month",
                                    df["date"].dt.month.unique())

        filtered = df[df["date"].dt.month == month_filter]

        # Pie Chart
        pie_data = filtered.groupby("category")["amount"].sum()
        st.subheader("Category Distribution")
        st.pyplot(pie_data.plot.pie(autopct="%1.1f%%").figure)

        # Prediction
        monthly = df.groupby(df["date"].dt.month)["amount"].sum()
        if len(monthly) > 1:
            X = np.array(monthly.index).reshape(-1,1)
            y = monthly.values
            model = LinearRegression()
            model.fit(X,y)
            next_month = np.array([[max(monthly.index)+1]])
            pred = model.predict(next_month)
            st.info(f"📈 Predicted Next Month: ₹ {round(pred[0],2)}")

        st.dataframe(filtered)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
