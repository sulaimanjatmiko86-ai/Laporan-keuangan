import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Kasir Jaya Digital Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .income { border-left: 5px solid #28a745; }
    .expense { border-left: 5px solid #dc3545; }
    .balance { border-left: 5px solid #007bff; }
    .separator {
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        margin: 20px 0;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Custom Header
def custom_header():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("https://via.placeholder.com/100x100?text=Logo", width=80)  # Placeholder logo
    with col2:
        st.markdown("<h1 style='text-align: center; color: white;'>Kasir Jaya Digital</h1>", unsafe_allow_html=True)
    with col3:
        st.write("")  # Spacer

# Sample data (replace with your actual data loading)
@st.cache_data
def load_data():
    # Dummy data for demonstration
    data = {
        'Date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
        'Income': [1000 + i*10 for i in range(30)],
        'Expense': [800 + i*5 for i in range(30)],
        'Balance': [200 + i*5 for i in range(30)]
    }
    df = pd.DataFrame(data)
    return df

df = load_data()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Input", "Reports"])

# Main content
if page == "Input":
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    custom_header()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.header("Input Data")
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Input form
    with st.form("input_form"):
        date = st.date_input("Date", datetime.today())
        income = st.number_input("Income", min_value=0.0, step=0.01)
        expense = st.number_input("Expense", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("Data submitted successfully!")
            # Add logic to save data here

elif page == "Reports":
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    custom_header()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.header("Financial Reports")
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Modern Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card balance">', unsafe_allow_html=True)
        st.metric("Saldo (Balance)", f"Rp {df['Balance'].iloc[-1]:,.0f}", delta=f"{df['Balance'].iloc[-1] - df['Balance'].iloc[-2]:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card income">', unsafe_allow_html=True)
        st.metric("Income", f"Rp {df['Income'].sum():,.0f}", delta=f"{df['Income'].iloc[-1]:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card expense">', unsafe_allow_html=True)
        st.metric("Expense", f"Rp {df['Expense'].sum():,.0f}", delta=f"{df['Expense'].iloc[-1]:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Enhanced Charts
    st.subheader("Income and Expense Over Time")
    fig1 = px.line(df, x='Date', y=['Income', 'Expense'], 
                   color_discrete_sequence=px.colors.sequential.Sunset,
                   template="plotly_white")
    fig1.update_layout(
        title="Income vs Expense Trend",
        xaxis_title="Date",
        yaxis_title="Amount (Rp)",
        responsive=True
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    st.subheader("Balance Trend")
    fig2 = px.area(df, x='Date', y='Balance', 
                   color_discrete_sequence=px.colors.sequential.Plasma,
                   template="plotly_white")
    fig2.update_layout(
        title="Balance Over Time",
        xaxis_title="Date",
        yaxis_title="Balance (Rp)",
        responsive=True
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Monthly Summary")
    df['Month'] = df['Date'].dt.to_period('M')
    monthly = df.groupby('Month').agg({'Income': 'sum', 'Expense': 'sum', 'Balance': 'last'}).reset_index()
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=monthly['Month'].astype(str), y=monthly['Income'], name='Income', marker_color='green'))
    fig3.add_trace(go.Bar(x=monthly['Month'].astype(str), y=monthly['Expense'], name='Expense', marker_color='red'))
    fig3.update_layout(
        title="Monthly Income and Expense",
        xaxis_title="Month",
        yaxis_title="Amount (Rp)",
        barmode='group',
        template="plotly_white",
        responsive=True
    )
    st.plotly_chart(fig3, use_container_width=True)
