import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime

@st.cache_data(show_spinner=False, show_time=False)
def data_loader():
    loans_log_link = f"https://drive.google.com/uc?export=download&id={st.secrets["loans_log_id"]}"
    books_log_link = f"https://drive.google.com/uc?export=download&id={st.secrets["book_names_id"]}"
    loans_df = pd.read_csv(loans_log_link)
    books_df = pd.read_csv(books_log_link)
    loaned_book_ids = loans_df[loans_df['return_date'].isna()]['book_id'].unique()
    books_df["available"] = ~books_df['id'].isin(loaned_book_ids)
    books_df['available'] = np.where(books_df['available'], '✅ זמין', '❌ לא זמין')
    books_df = books_df.query('active == True').drop(columns=['active'])
    books_df['name'] = books_df['name'].str.strip()
    books_df['author'] = books_df['author'].str.strip()

    books_df['combination'] = books_df['name'] + " - " + books_df['author']
    return  books_df, loans_df

def calculate_metrics(books_df, loans_df):
    """Calculate metrics for the dashboard"""
    # Create a proper copy of active loans and calculate duration
    active_loans = loans_df[loans_df['return_date'].isna()].copy()
    active_loans.loc[:, 'loan_duration'] = (datetime.today() - pd.to_datetime(active_loans['loan_date'], format='%d/%m/%Y')).dt.days
    
    # Create a proper copy of late loans
    late_loans = active_loans[active_loans['loan_duration'] > 30].copy()
    
    active_loaners_count = len(active_loans['loaner_id'].unique())
    late_loaners_count = len(late_loans['loaner_id'].unique())
    late_loans_count = len(late_loans)
    
    total_books = len(books_df)
    borrowed_books = len(active_loans['book_id'].unique())
    late_books = len(late_loans['book_id'].unique())
    available_books = total_books - borrowed_books
    metrics ={
        'active_loaners': active_loaners_count,
        'late_loaners': late_loaners_count,
        'active_loans': len(active_loans),
        'late_loans': late_loans_count,
        'total_books': total_books,
        'borrowed_books': borrowed_books,
        'late_books': late_books,
        'available_books': available_books
    }
    with st.container(horizontal=True, horizontal_alignment="center"):
        st.metric("📚 סה״כ ספרים", f"{metrics['total_books']:,}")
        st.metric("✅ ספרים זמינים", f"{metrics['available_books']:,}")
        st.metric("📖 ספרים מושאלים", f"{metrics['borrowed_books']:,}")

def expanded_status(books_df, loans_df):# deprecated
    # Calculate book status
    active_loans = loans_df[loans_df['return_date'].isna()].copy()
    active_loans.loc[:, 'loan_duration'] = (datetime.today() - pd.to_datetime(active_loans['loan_date'], format='%d/%m/%Y')).dt.days

    # Create status mapping
    book_status = {}
    for _, loan in active_loans.iterrows():
        if loan['loan_duration'] > 30:
            book_status[loan['book_id']] = f"באיחור - {loan['loan_duration']} ימים⚠️"
        else:
            book_status[loan['book_id']] = f"מושאל - {loan['loan_duration']} ימים📚"

    # Add status to books_df
    books_df.loc[:, 'status'] = books_df['id'].apply(lambda x: book_status.get(x, '✅ זמין'))
    return books_df

def table_render(books_df, search_term=None):
    # Filter books based on search and category
    if search_term:
        filtered_books = books_df[
            books_df['combination'] == search_term
            # books_df['name'].str.contains(search_term, case=False) |
            # books_df['author'].str.contains(search_term, case=False)
        ]
    else:
        filtered_books = books_df

    # Configure columns for books table
    books_columns = {
        'available': st.column_config.TextColumn('👀 זמינות', width='40px'),
        'author': st.column_config.TextColumn('✍️ מחבר', width='50px'),
        'name': st.column_config.TextColumn('📖 שם הספר', width="9px"),
        # 'status': st.column_config.TextColumn('🩺 סטטוס', width='medium'),
        # 'id': st.column_config.NumberColumn('🔢 מזהה', width='small'),
        # 'category': st.column_config.TextColumn('🏷️ קטגוריה', width='medium'),
        # 'active': st.column_config.CheckboxColumn('🟢 פעיל', width='small'),
    }
    df_show = books_df[books_df.columns[::-1]].drop(columns=["id"])
    st.dataframe(
        df_show.sort_values(["author","name"],ascending=True),
        column_config=books_columns,
        column_order=books_columns.keys(),
        hide_index=True,
        use_container_width=True,
    )
    return filtered_books

def render_books_search_and_table(books_df, loans_df):
    """Render the books search and table section"""
    # Search and filter
    # books_df = books_df.copy()

    with st.form(key="form_search",border=False,enter_to_submit=True,clear_on_submit=True):
        st.session_state.dynamic_key = f"search_{0}" if "dynamic_key" not in st.session_state else st.session_state.dynamic_key
        search_options = [''] + sorted(books_df['combination'],reverse=True)

        search_term = st.selectbox("חיפוש ספרים לפי שם או מחבר",
                                    options=search_options,
                                    placeholder='בחר/י ספר או מחבר', label_visibility="collapsed",key="search_selectbox")
        search_row = st.container(horizontal=True, horizontal_alignment="center")
        
        status_cont = st.container(horizontal_alignment="center",
                                height=140, border=False,
                                vertical_alignment="center",key="dynamic_status")
        st.divider()
        center_header(level=5, text="קטלוג הספרים 📚")
        df_show = table_render(books_df, search_term)

        if not search_term:
            status_cont.markdown(
                    """
                    <div style='display: flex; justify-content: center;'>
                        <div style='background-color: #fcf7e4; color: #856404; border: 1px solid #ffeeba; border-radius: 8px; padding: 10px 20px; margin: 10px 0; font-size: 1em; text-align: center; max-width: 400px;'>
                             יש להקליד שם ספר או מחבר ולהקיש 🔎 לחיפוש
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
            )

        if search_row.form_submit_button(":material/search:", type="primary"):
            # if len(df_show) == 1:
            if search_term:
                with status_cont:
                    center_header(5, f"{df_show['name'].values[0]}")
                    center_header(6, f"{df_show['author'].values[0]}")
                    center_header(7, f"{df_show['available'].values[0]}")

        if search_row.form_submit_button(":material/refresh:", type="primary"):
            
            search_term = ""
        calculate_metrics(books_df, loans_df)
        
    # with table_cont:

def center_header(level=1, text="📚 ספרייה קהילתית 🌳"):
    """level >= 7 is not bold"""
    if level >= 7:
        st.markdown(f"<div style='text-align: center;'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h{level} style='text-align: center;'>{text}</h{level}>", unsafe_allow_html=True)
