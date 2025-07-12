import streamlit as st
import pandas as pd
from supabase_api import *
import matplotlib.pyplot as plt

st.title("Report")

user_id = st.text_input("Enter your user id:")

if user_id:
  transactions_data = get_transactions_table_by_user(user_id)
  categories_data = get_categories_table_by_user(user_id)

  transactions_df = pd.DataFrame(transactions_data)
  categories_df = pd.DataFrame(categories_data)

  transactions_df = transactions_df[["created_at", "updated_at", "date", "category_id", "description",  "currency", "amount"]]
  merge_df = transactions_df.merge(categories_df, how='inner', on='category_id')
  merge_df = merge_df[["created_at", "updated_at", "date", "category_type", "category_name", "description", "currency", "amount"]]
  merge_df['date'] = pd.to_datetime(merge_df['date'])

  # Configure column widths
  st.dataframe(merge_df)


  category_type_sum_df = merge_df.groupby(['category_type'])['amount'].sum().reset_index()
  category_name_sum_df = merge_df.groupby(['category_name'])['amount'].sum().reset_index()


  fig, ax = plt.subplots(figsize=(3, 2))  # width=10, height=5 inches
  bars = ax.bar(category_type_sum_df['category_type'], category_type_sum_df['amount'])
  ax.bar_label(bars, padding=3) 
  st.pyplot(fig, use_container_width=False)


  fig, ax = plt.subplots(figsize=(3, 2))  # width=10, height=5 inches
  bars = ax.bar(category_name_sum_df['category_name'], category_name_sum_df['amount'])
  ax.bar_label(bars, padding=3) 
  st.pyplot(fig, use_container_width=False)

