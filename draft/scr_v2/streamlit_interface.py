import streamlit as st
import pandas as pd
from supabase_api import *
import plotly.express as px

# Get query parameters
query_params = st.query_params

if query_params:
  user_id = query_params.get("user_id", "")
  user_info = get_user_info(user_id)
else:
  user_id = None

if user_id:
  st.set_page_config(layout="wide")
  st.title("Report")

  st.subheader(f"Welcome, {user_info['username']}!!!")

  transactions_data = get_transactions_table_by_user(user_id)
  categories_data = get_categories_table_by_user(user_id)

  transactions_df = pd.DataFrame(transactions_data)
  categories_df = pd.DataFrame(categories_data)

  transactions_df = transactions_df[["created_at", "updated_at", "date", "category_id", "description",  "currency", "amount"]]
  merge_df = transactions_df.merge(categories_df, how='inner', on='category_id')
  merge_df = merge_df[["created_at", "updated_at", "date", "category_type", "category_name", "description", "currency", "amount"]]
  merge_df['date'] = pd.to_datetime(merge_df['date'])

  # Configure column widths
  with st.expander("Expense History"):
    st.dataframe(merge_df)

  category_type_sum_df = merge_df.groupby(['category_type'])['amount'].sum().reset_index()
  category_name_sum_df = merge_df.groupby(['category_name'])['amount'].sum().reset_index()

  st.dataframe(category_type_sum_df)

  a,b,c = st.columns(3)
  a.metric(label="Expense", value=f"${category_type_sum_df[category_type_sum_df["category_type"] == "Expense"]["amount"].values[0]}", width=200)
  b.metric(label="Income", value=f"${category_type_sum_df[category_type_sum_df["category_type"] == "Income"]["amount"].values[0]}", width=200)
  c.metric(label="Total Spending", value=f"${merge_df["amount"].sum()}", width=200)


  col1, col2 = st.columns(2)
  with col1:
    fig = px.pie(category_type_sum_df,
                 values='amount',
                 names='category_type',
                 title='Distribution of Category Type')
    st.plotly_chart(fig)

  with col2:
    fig = px.pie(category_name_sum_df,
                 values='amount',
                 names='category_name',
                 title='Distribution of Category Name')
    st.plotly_chart(fig)


import numpy as np
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

# Custom Metric Cards with centered text inside borders
st.subheader("Key Financial Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div style="border: 2px solid #ccc; border-radius: 5px; padding: 10px; height: 100px; display: flex; justify-content: center; align-items: center; text-align: center;">
            <div>
                <h4 style="margin: 0;">Total Spending</h4>
                <p style="margin: 0; font-size: 18px;">${:,.2f}</p>
            </div>
        </div>
        """.format(filtered_transactions['amount'].sum()),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style="border: 2px solid #ccc; border-radius: 5px; padding: 10px; height: 100px; display: flex; justify-content: center; align-items: center; text-align: center;">
            <div>
                <h4 style="margin: 0;">Avg Monthly Spending</h4>
                <p style="margin: 0; font-size: 18px;">${:,.2f}</p>
            </div>
        </div>
        """.format(filtered_transactions.groupby('month')['amount'].sum().mean()),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div style="border: 2px solid #ccc; border-radius: 5px; padding: 10px; height: 100px; display: flex; justify-content: center; align-items: center; text-align: center;">
            <div>
                <h4 style="margin: 0;">Highest Expense</h4>
                <p style="margin: 0; font-size: 18px;">${:,.2f}</p>
            </div>
        </div>
        """.format(filtered_transactions['amount'].max()),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <div style="border: 2px solid #ccc; border-radius: 5px; padding: 10px; height: 100px; display: flex; justify-content: center; align-items: center; text-align: center;">
            <div>
                <h4 style="margin: 0;">Transaction Count</h4>
                <p style="margin: 0; font-size: 18px;">{}</p>
            </div>
        </div>
        """.format(len(filtered_transactions)),
        unsafe_allow_html=True
    )