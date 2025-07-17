import streamlit as st
import pandas as pd
from supabase_api import *
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

# Get query parameters
query_params = st.query_params

if query_params:
    user_id = query_params.get("user_id", "")
    user_info = get_user_info(user_id)
else:
    user_id = None

if user_id:
    st.title("Financial Dashboard")
    st.subheader(f"Welcome, {user_info['username']}!!!")

    # Fetch data
    transactions_data = get_transactions_table_by_user(user_id)
    categories_data = get_categories_table_by_user(user_id)

    transactions_df = pd.DataFrame(transactions_data)
    categories_df = pd.DataFrame(categories_data)

    # Process data
    transactions_df = transactions_df[["created_at", "updated_at", "date", "category_id", "description", "currency", "amount"]]
    merge_df = transactions_df.merge(categories_df, how='inner', on='category_id')
    merge_df = merge_df[["created_at", "updated_at", "date", "category_type", "category_name", "description", "currency", "amount"]]
    merge_df['date'] = pd.to_datetime(merge_df['date'])

    # Date filter
    st.subheader("Select Transactions by Date")
    col1, col2 = st.columns(2)
    first_day_of_this_month = date(year=datetime.today().year, month=datetime.today().month, day=1)
    with col1:
        start_date = st.date_input(label="Start Date", value=first_day_of_this_month)
    with col2:
        end_date = st.date_input(label="End Date", value=first_day_of_this_month+relativedelta(months=1)-timedelta(days=1))

    # Filter dataframe by date range
    mask = (merge_df['date'].dt.date >= start_date) & (merge_df['date'].dt.date <= end_date)
    transaction_df = merge_df[mask]

    # Display transaction history
    with st.expander("Transaction History"):
        st.dataframe(transaction_df.sort_values(by='date', ascending=False))

    st.dataframe(transaction_df.groupby("date")["amount"].sum().reset_index())

    # Create line chart with Plotly Express
    fig = px.line(
        data_frame=transaction_df.groupby("date")["amount"].sum().reset_index(),
        x='date',
        y='amount',
        title='Daily Transaction Amounts',
        labels={'date': 'Date', 'amount': 'Amount ($)'},
        template='plotly'  # Use a clean theme
    )

    # Customize line chart
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Amount ($)",
        hovermode="x unified"  # Unified hover tooltip for better UX
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Please provide a valid user_id to view the dashboard.")

# if user_id:
#     # st.set_page_config(layout="wide")
#     st.title("Financial Dashboard")

#     st.subheader(f"Welcome, {user_info['username']}!!!")

#     # Fetch data
#     transactions_data = get_transactions_table_by_user(user_id)
#     categories_data = get_categories_table_by_user(user_id)

#     transactions_df = pd.DataFrame(transactions_data)
#     categories_df = pd.DataFrame(categories_data)

#     # Process data
#     transactions_df = transactions_df[["created_at", "updated_at", "date", "category_id", "description", "currency", "amount"]]
#     merge_df = transactions_df.merge(categories_df, how='inner', on='category_id')
#     merge_df = merge_df[["created_at", "updated_at", "date", "category_type", "category_name", "description", "currency", "amount"]]
#     merge_df['date'] = pd.to_datetime(merge_df['date'])

#     # Date filter
#     st.subheader("Filter Transactions by Date")
#     col1, col2 = st.columns(2)
#     with col1:
#         start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
#     with col2:
#         end_date = st.date_input("End Date", value=datetime.now())
    
#     # Filter dataframe by date range
#     mask = (merge_df['date'].dt.date >= start_date) & (merge_df['date'].dt.date <= end_date)
#     filtered_df = merge_df[mask]

#     # Display transaction history
#     with st.expander("Transaction History"):
#         st.dataframe(filtered_df.sort_values(by='date', ascending=False))

#     # Calculate metrics
#     category_type_sum_df = filtered_df.groupby(['category_type'])['amount'].sum().reset_index()
#     category_name_sum_df = filtered_df.groupby(['category_name'])['amount'].sum().reset_index()
#     avg_transaction_df = filtered_df.groupby(['category_name'])['amount'].mean().reset_index().rename(columns={'amount': 'avg_amount'})

#     # Metrics layout
#     st.subheader("Key Metrics")
#     col1, col2, col3, col4 = st.columns(4)
#     expense = category_type_sum_df[category_type_sum_df["category_type"] == "Expense"]["amount"].sum() if "Expense" in category_type_sum_df["category_type"].values else 0
#     income = category_type_sum_df[category_type_sum_df["category_type"] == "Income"]["amount"].sum() if "Income" in category_type_sum_df["category_type"].values else 0
#     net_balance = income - expense

#     with col1:
#         st.metric(label="Total Income", value=f"${income:,.2f}")
#     with col2:
#         st.metric(label="Total Expense", value=f"${expense:,.2f}")
#     with col3:
#         st.metric(label="Net Balance", value=f"${net_balance:,.2f}", delta=f"{net_balance:,.2f}")
#     with col4:
#         st.metric(label="Total Transactions", value=len(filtered_df))

#     # Visualizations
#     st.subheader("Spending Insights")

#     # Monthly spending trend
#     monthly_trend = filtered_df.groupby([filtered_df['date'].dt.to_period('M'), 'category_type'])['amount'].sum().reset_index()
#     monthly_trend['date'] = monthly_trend['date'].dt.to_timestamp()
#     fig_trend = px.line(monthly_trend, x='date', y='amount', color='category_type', title="Monthly Spending Trend")
#     st.plotly_chart(fig_trend, use_container_width=True)

#     # Top expense categories
#     expense_cats = category_name_sum_df[category_name_sum_df['amount'] > 0].sort_values(by='amount', ascending=False).head(5)
#     fig_cats = px.bar(expense_cats, x='category_name', y='amount', title="Top Expense Categories")
#     st.plotly_chart(fig_cats, use_container_width=True)

#     # Average transaction amount per category
#     fig_avg = px.bar(avg_transaction_df, x='category_name', y='avg_amount', title="Average Transaction Amount per Category")
#     st.plotly_chart(fig_avg, use_container_width=True)

# else:
#     st.error("Please provide a valid user_id to view the dashboard.")