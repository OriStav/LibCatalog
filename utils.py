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
    
    return {
        'active_loaners': active_loaners_count,
        'late_loaners': late_loaners_count,
        'active_loans': len(active_loans),
        'late_loans': late_loans_count,
        'total_books': total_books,
        'borrowed_books': borrowed_books,
        'late_books': late_books,
        'available_books': available_books
    }

def render_books_tab(books_df, loans_df):
    """Render the books tab content"""
    metrics = calculate_metrics(books_df, loans_df)
    center_header(level=1, text="🌳 קטלוג ספרים 📚")
    center_header(level=3, text="ספריית שדי חמד")
    render_books_search_and_table(books_df, loans_df)
    with st.container(horizontal=True, horizontal_alignment="center"):
        st.metric("📚 סה״כ ספרים", metrics['total_books'])
        st.metric("✅ ספרים זמינים", metrics['available_books'])
        st.metric("📖 ספרים מושאלים", metrics['borrowed_books'])

def render_books_search_and_table(books_df, loans_df):
    """Render the books search and table section"""
    # Search and filter
    books_df = books_df.copy()
    center_header(level=6, text="✍️ חיפוש ספרים לפי שם או מחבר 🔎")
    search_term = st.selectbox("חיפוש ספרים לפי שם או מחבר", 
                                 options=[''] + sorted(books_df['name'].unique().tolist() + books_df['author'].unique().tolist()),
                                 placeholder='בחר/י ספר או מחבר',label_visibility="collapsed")
    
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
    # Filter books based on search and category
    if search_term:
        filtered_books = books_df[
            books_df['name'].str.contains(search_term, case=False) |
            books_df['author'].str.contains(search_term, case=False)
        ]
    else:
        filtered_books = books_df

    # Configure columns for books table
    books_columns = {
        # 'category': st.column_config.TextColumn('🏷️ קטגוריה', width='medium'),
        'available': st.column_config.TextColumn('📊 זמינות', width='50px'),
        # 'status': st.column_config.TextColumn('🩺 סטטוס', width='medium'),
        'author': st.column_config.TextColumn('✍️ מחבר', width='50px'),
        'name': st.column_config.TextColumn('📖 שם הספר', width="9px"),
        # 'id': st.column_config.NumberColumn('🔢 מזהה', width='small'),
        # 'active': st.column_config.CheckboxColumn('🟢 פעיל', width='small'),
    }
    df_show = filtered_books[filtered_books.columns[::-1]].drop(columns=["id"])
    st.dataframe(
        df_show.sort_values(["name","author"]),
        column_config=books_columns,
        column_order=books_columns.keys(),
        hide_index=True,
        use_container_width=True,
    )


def center_header(level=1, text="📚 ספרייה קהילתית 🌳"):
    """level >= 7 is not bold"""
    st.markdown(f"<h{level} style='text-align: center;'>{text}</h{level}>", unsafe_allow_html=True)
