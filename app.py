import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="ahas Dashboard",
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

#
