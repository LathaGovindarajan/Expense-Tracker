import streamlit as st
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------- MongoDB Setup -----------------
client = MongoClient('mongodb://localhost:27017')
db = client['expense_db']

users_col = db['user']
categories_col = db['category']
expenses_col = db['expenses']

# ----------------- Sidebar Filters -----------------
st.sidebar.title("🔍 Filters")

# Get all users
users = list(users_col.find({}, {"_id": 1, "username": 1}))
user_map = {user["username"]: user["_id"] for user in users}
selected_user = st.sidebar.selectbox("User", list(user_map.keys()))

# Get categories
categories = list(categories_col.find({}, {"_id": 1, "category": 1}))
cat_map = {cat["category"]: cat["_id"] for cat in categories}
selected_categories = st.sidebar.multiselect("Categories", list(cat_map.keys()), default=list(cat_map.keys()))

# Date range filter
date_range = st.sidebar.date_input("Date Range", value=[datetime(2024, 1, 1), datetime.today()])
start_date, end_date = date_range[0], date_range[1]

# ----------------- Fetch & Prepare Data -----------------
user_id = user_map[selected_user]
category_ids = [cat_map[c] for c in selected_categories]

query = {
    "user": user_id,
    "category": {"$in": category_ids},
    "date": {"$gte": datetime.combine(start_date, datetime.min.time()),
             "$lte": datetime.combine(end_date, datetime.max.time())}
}
expenses = list(expenses_col.find(query))

if not expenses:
    st.title("💸 Expense Tracker Dashboard")
    st.warning("No expense data found for the selected filters.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(expenses)
df["amount"] = df["amount"].astype(float)
df["date"] = pd.to_datetime(df["date"])
df["category"] = df["category"].apply(lambda cid: categories_col.find_one({"_id": cid})["category"])
df["month"] = df["date"].dt.to_period("M").astype(str)

# ----------------- Dashboard -----------------
st.title("💸 Expense Tracker Dashboard")

total_spent = df["amount"].sum()
user_info = users_col.find_one({"_id": user_id})
goal = user_info.get("spending_goal", 0)

# Summary Metrics
col1, col2 = st.columns(2)
col1.metric("Total Spending", f"₹ {total_spent:,.2f}")
col2.metric("Spending Goal", f"₹ {goal:,.2f}", delta=f"₹ {total_spent - goal:,.2f}")

# ----------------- Visualization 1: Spending by Category -----------------
st.subheader("📊 Category-wise Spending")

cat_df = df.groupby("category")["amount"].sum().sort_values(ascending=False).reset_index()

col1, col2 = st.columns(2)

with col1:
    st.write("Bar Chart")
    fig, ax = plt.subplots()
    sns.barplot(data=cat_df, x="amount", y="category", palette="viridis", ax=ax)
    ax.set_xlabel("Amount Spent (₹)")
    ax.set_ylabel("Category")
    st.pyplot(fig)

with col2:
    st.write("Pie Chart")
    fig2, ax2 = plt.subplots()
    ax2.pie(cat_df["amount"], labels=cat_df["category"], autopct='%1.1f%%', startangle=140)
    ax2.axis('equal')
    st.pyplot(fig2)

# ----------------- Visualization 2: Monthly Trend -----------------
st.subheader("📈 Monthly Spending Trend")

monthly = df.groupby("month")["amount"].sum().reset_index()

fig3, ax3 = plt.subplots()
sns.lineplot(data=monthly, x="month", y="amount", marker="o", ax=ax3)
ax3.set_ylabel("Total Spent (₹)")
ax3.set_title("Monthly Expense Trend")
plt.xticks(rotation=45)
st.pyplot(fig3)

# ----------------- Visualization 3: Budget Goals per Category -----------------
st.subheader("🎯 Category Budget Goals")

goal_data = []
for cat in selected_categories:
    cat_obj = categories_col.find_one({"_id": cat_map[cat]})
    goal_data.append({
        "category": cat_obj["category"],
        "goal": cat_obj.get("goal", 0.0),
        "spent": df[df["category"] == cat_obj["category"]]["amount"].sum()
    })

goal_df = pd.DataFrame(goal_data)

fig4, ax4 = plt.subplots()
goal_df.plot(kind="bar", x="category", y=["goal", "spent"], ax=ax4, color=["green", "red"])
ax4.set_ylabel("₹ Amount")
ax4.set_title("Category-wise Budget vs Actual Spending")
st.pyplot(fig4)

# ----------------- Optional: Show Raw Data -----------------
with st.expander("🧾 Show Raw Data"):
    st.dataframe(df[["date", "category", "amount", "description"]].sort_values(by="date", ascending=False))
