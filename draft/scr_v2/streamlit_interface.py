import streamlit as st
import pandas as pd
from supabase_api import *
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

st.set_page_config(layout="wide")

def set_page_width(page_width=5):
    _, col, _ = st.columns([1, page_width, 1])
    return col

with set_page_width():

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

        # ==============================================================================================
        # Date filter
        st.subheader("Select Transactions by Date")
        col1, col2 = st.columns(2)
        first_day_of_this_month = date(year=datetime.today().year, month=datetime.today().month, day=1)
        with col1:
            start_date = st.date_input(label="Start Date", value=first_day_of_this_month)
        with col2:
            end_date = st.date_input(label="End Date", value=first_day_of_this_month+relativedelta(months=1)-timedelta(days=1))

        # ==============================================================================================
        # Filter dataframe by date range
        mask = (merge_df['date'].dt.date >= start_date) & (merge_df['date'].dt.date <= end_date)
        transaction_df = merge_df[mask]

        # Display transaction history
        with st.expander("Transaction History"):
            st.dataframe(transaction_df.sort_values(by='date', ascending=False))

        st.dataframe(transaction_df.groupby("date")["amount"].sum().reset_index())

        # ==============================================================================================
        # Create line chart with Plotly Express
        fig = px.line(
            data_frame=transaction_df.groupby("date")["amount"].sum().reset_index(),
            x='date',
            y='amount',
            title='Daily Spending Trend',
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

        # ==============================================================================================
        col1, col2 = st.columns(2)

        with col1:
            # Create pie chart
            fig = px.pie(
                data_frame=transaction_df,
                values='amount',
                names='category_type',
                title='Income VS Expense',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_traces(textinfo='label+percent+value', textposition='auto')
            st.plotly_chart(fig)

        # ==============================================================================================#
        with col2:
            # Create pie chart
            fig = px.pie(
                data_frame=transaction_df,
                values='amount',
                names='category_name',
                title='Spending in each category',
                color_discrete_sequence=px.colors.qualitative.D3
            )
            fig.update_traces(textinfo='label+percent+value', textposition='auto')

            # Display in Streamlit
            st.plotly_chart(fig)


    else:
        st.error("Please provide a valid user_id to view the dashboard.")