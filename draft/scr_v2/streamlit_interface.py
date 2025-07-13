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

  a,b,c = st.columns(3)
  a.metric(label="Total Spending", value=f"${merge_df["amount"].sum()}", delta="1.2 °F", border=True, width=200)

  category_type_sum_df = merge_df.groupby(['category_type'])['amount'].sum().reset_index()
  category_name_sum_df = merge_df.groupby(['category_name'])['amount'].sum().reset_index()


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
