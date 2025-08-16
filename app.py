"""
streamlit run app.py

TODO:
- backup backslash
"""
import streamlit as st
import pandas as pd
from utils import render_books_tab, data_loader
st.set_page_config(page_title="ספרייה קהילתית", page_icon="📚", layout="wide")
with st.spinner("Loading...", show_time=True):
    books_df, loans_df = data_loader()

render_books_tab(books_df, loans_df)
