Import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Initialize session state for data storage
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Type', 'Category', 'Amount', 'Date'])

# Sidebar for data input
st.sidebar.header("Add Transaction")
type_ = st.sidebar.selectbox("Type", ["Income", "Expense"])
category = st.sidebar.text_input("Category")
amount = st.sidebar.number_input("Amount", min_value=0.0, step=0.01)
date = st.sidebar.date_input("Date", value=datetime.today())

if st.sidebar.button("Add Transaction"):
    if category and amount > 0:
        new_row = pd.DataFrame({'Type': [type_], 'Category': [category], 'Amount': [amount], 'Date': [date]})
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.sidebar.success("Transaction added!")
    else:
        st.sidebar.error("Please fill in all fields correctly.")

# Main dashboard
st.title("Financial Dashboard")
st.markdown("A clean, modern financial dashboard for tracking income and expenses.")

# Summary cards at the top
total_income = st.session_state.data[st.session_state.data['Type'] == 'Income']['Amount'].sum()
total_expenses = st.session_state.data[st.session_state.data['Type'] == 'Expense']['Amount'].sum()
total_balance = total_income - total_expenses

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Balance", f"${total_balance:.2f}")
with col2:
    st.metric("Total Income", f"${total_income:.2f}")
with col3:
    st.metric("Total Expenses", f"${total_expenses:.2f}")

# Visualizations
st.header("Visualizations")

# Donut Chart for Expenses
expenses = st.session_state.data[st.session_state.data['Type'] == 'Expense']
if not expenses.empty:
    fig_donut = px.pie(expenses, values='Amount', names='Category', hole=0.4, title="Expenses by Category")
    fig_donut.update_layout(margin=dict(t=50, b=50, l=50, r=50))
    st.plotly_chart(fig_donut, use_container_width=True)
else:
    st.info("No expenses data to display.")

# Bar Chart for Monthly Cash Flow
if not st.session_state.data.empty:
    st.session_state.data['Date'] = pd.to_datetime(st.session_state.data['Date'])
    st.session_state.data['Month'] = st.session_state.data['Date'].dt.to_period('M')
    monthly = st.session_state.data.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0)
    monthly['Net'] = monthly.get('Income', 0) - monthly.get('Expense', 0)
    fig_bar = px.bar(monthly, x=monthly.index.astype(str), y='Net', title="Monthly Cash Flow (Income - Expenses)")
    fig_bar.update_layout(margin=dict(t=50, b=50, l=50, r=50))
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No data to display monthly cash flow.")

# Export functionality
st.header("Export Data")
csv_data = st.session_state.data.to_csv(index=False)
st.download_button(
    label="Download as CSV",
    data=csv_data,
    file_name="financial_data.csv",
    mime="text/csv",
    key="csv_download"
)

# Optional: Export as Excel (requires openpyxl)
try:
    import openpyxl
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.data.to_excel(writer, index=False, sheet_name='Transactions')
    buffer.seek(0)
    st.download_button(
        label="Download as Excel",
        data=buffer,
        file_name="financial_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="excel_download"
    )
except ImportError:
    st.warning("Excel export requires 'openpyxl' library. Install it with 'pip install openpyxl' for Excel support.")

# Display raw data table (optional, for debugging or viewing)
st.header("Transaction Data")
st.dataframe(st.session_state.data, use_container_width=True)
