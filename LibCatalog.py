"""
streamlit run LibCatalog.py

"""
import streamlit as st
import pandas as pd
from utils import render_books_search_and_table, data_loader, center_header
st.set_page_config(page_title="קטלוג ספרייה קהילתית", page_icon="📚", layout="wide")
with st.spinner("Loading...", show_time=True):
    books_df, loans_df = data_loader()

center_header(level=1, text="ספריית שדי חמד 🌳")

render_books_search_and_table(books_df, loans_df)
st.markdown(
    "<div style='text-align: center;'><a href='mailto:hemmed.library@gmail.com'>תיבת פניות</a> 📥</div>",
    unsafe_allow_html=True
)