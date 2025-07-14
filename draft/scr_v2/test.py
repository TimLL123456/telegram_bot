import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from plotly import graph_objects as go

# Sample data generation
np.random.seed(42)
dates = pd.date_range(start="2024-01-01", end="2025-07-14", freq="D")
sample_transactions = pd.DataFrame({
    'transaction_id': range(1, 151),
    'user_id': 1,
    'date': np.random.choice(dates, 150),
    'category_id': np.random.choice([1, 2, 3, 4, 5], 150),
    'description': ['Grocery', 'Utility', 'Entertainment', 'Travel', 'Dining'] * 30,
    'amount': np.random.uniform(5, 1000, 150),
    'currency': ['USD'] * 150,
    'is_deleted': False,
    'created_at': pd.Timestamp.now(),
    'updated_at': pd.Timestamp.now()
})

sample_categories = pd.DataFrame({
    'category_id': [1, 2, 3, 4, 5],
    'category_type': ['Food', 'Bills', 'Leisure', 'Travel', 'Food'],
    'category_name': ['Grocery', 'Utility', 'Entertainment', 'Travel', 'Dining'],
    'created_at': pd.Timestamp.now(),
    'updated_at': pd.Timestamp.now()
})

sample_users = pd.DataFrame({
    'user_id': [1],
    'username': ['johndoe'],
    'default_currency': ['USD'],
    'created_at': pd.Timestamp.now(),
    'updated_at': pd.Timestamp.now()
})

# Filter transactions for the user and exclude deleted ones
user_transactions = sample_transactions[sample_transactions['user_id'] == 1]

# Merge with categories to get category names
user_transactions = user_transactions.merge(sample_categories[['category_id', 'category_name']], on='category_id', how='left')

# Convert 'date' to datetime and create 'month' column
user_transactions['date'] = pd.to_datetime(user_transactions['date'])
user_transactions['month'] = user_transactions['date'].dt.to_period('M').dt.to_timestamp()

# Streamlit app
st.title("Detailed Personal Expense Report")

# Date range filter
min_date = user_transactions['date'].min().date()
max_date = user_transactions['date'].max().date()
date_range = st.date_input("Select Date Range", [min_date, max_date])
filtered_transactions = user_transactions[
    (user_transactions['date'] >= pd.to_datetime(date_range[0])) & 
    (user_transactions['date'] <= pd.to_datetime(date_range[1]))
]

# Category filter
categories_list = filtered_transactions['category_name'].unique()
selected_categories = st.multiselect("Select Categories", categories_list, default=categories_list)
filtered_transactions = filtered_transactions[filtered_transactions['category_name'].isin(selected_categories)]

# Metric Cards with centering
st.subheader("Key Financial Metrics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<p style='text-align: center;'>", unsafe_allow_html=True)
    st.metric(label="Total Spending", value=f"${filtered_transactions['amount'].sum():,.2f}")
    st.markdown("</p>", unsafe_allow_html=True)
with col2:
    st.markdown("<p style='text-align: center;'>", unsafe_allow_html=True)
    st.metric(label="Avg Monthly Spending", value=f"${filtered_transactions.groupby('month')['amount'].sum().mean():,.2f}")
    st.markdown("</p>", unsafe_allow_html=True)
with col3:
    st.markdown("<p style='text-align: center;'>", unsafe_allow_html=True)
    st.metric(label="Highest Expense", value=f"${filtered_transactions['amount'].max():,.2f}")
    st.markdown("</p>", unsafe_allow_html=True)
with col4:
    st.markdown("<p style='text-align: center;'>", unsafe_allow_html=True)
    st.metric(label="Transaction Count", value=f"{len(filtered_transactions)}")
    st.markdown("</p>", unsafe_allow_html=True)

# Expense Trends Over Time
st.subheader("Expense Trends Over Time")
monthly_expenses = filtered_transactions.groupby('month')['amount'].sum().reset_index()
fig1 = px.line(monthly_expenses, x='month', y='amount', title='Monthly Expense Trends', labels={'amount': 'Total Amount'})
st.plotly_chart(fig1)

# Cumulative Spending Trend
st.subheader("Cumulative Spending Trend")
cumulative_expenses = monthly_expenses.sort_values('month').copy()
cumulative_expenses['cumulative_amount'] = cumulative_expenses['amount'].cumsum()
fig5 = px.line(cumulative_expenses, x='month', y='cumulative_amount', title='Cumulative Expenses Over Time', labels={'cumulative_amount': 'Cumulative Amount'})
st.plotly_chart(fig5)

# Category-Wise Spending Breakdown
st.subheader("Category-Wise Spending")
category_expenses = filtered_transactions.groupby('category_name')['amount'].sum().reset_index()
fig2 = px.pie(category_expenses, values='amount', names='category_name', title='Expenses by Category')
st.plotly_chart(fig2)

# Category Spending Trends
st.subheader("Category Spending Trends")
category_trends = filtered_transactions.groupby(['month', 'category_name'])['amount'].sum().reset_index()
fig6 = px.line(category_trends, x='month', y='amount', color='category_name', title='Spending Trends by Category', labels={'amount': 'Total Amount'})
st.plotly_chart(fig6)

# Top 10 Expenses
st.subheader("Top 10 Expenses")
top_expenses = filtered_transactions.nlargest(10, 'amount')
fig3 = px.bar(top_expenses, x='description', y='amount', title='Top 10 Expenses', labels={'amount': 'Amount'}, color='category_name')
st.plotly_chart(fig3)

# Monthly Expense Comparison
st.subheader("Monthly Expense Comparison")
fig4 = px.bar(monthly_expenses, x='month', y='amount', title='Monthly Expense Comparison', labels={'amount': 'Total Amount'}, color_discrete_sequence=['#1f77b4'])
st.plotly_chart(fig4)

# Average Monthly Spending
st.subheader("Average Monthly Spending")
avg_monthly = monthly_expenses['amount'].mean()
fig7 = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_monthly,
    title={'text': "Average Monthly Expense"},
    gauge={'axis': {'range': [0, monthly_expenses['amount'].max() * 1.2]},
           'bar': {'color': "#20c997"}}))
st.plotly_chart(fig7)

# Detailed Expense Breakdown
st.subheader("Detailed Expense Breakdown")
st.dataframe(filtered_transactions[['date', 'category_name', 'description', 'amount', 'currency']])
csv = filtered_transactions[['date', 'category_name', 'description', 'amount', 'currency']].to_csv(index=False)
st.download_button(label="Download CSV", data=csv, file_name="expense_breakdown.csv", mime="text/csv")

# Spending by Currency (if applicable)
st.subheader("Spending by Currency")
currency_expenses = filtered_transactions.groupby('currency')['amount'].sum().reset_index()
fig8 = px.bar(currency_expenses, x='currency', y='amount', title='Spending by Currency', labels={'amount': 'Total Amount'})
st.plotly_chart(fig8)