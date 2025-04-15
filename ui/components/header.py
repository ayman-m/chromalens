"""
Header component for ChromaLens UI
"""

import streamlit as st

def render_header():
    """Render the app header with styling"""
    # Custom styling
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #4B7BEC;
            margin-bottom: 0;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #666;
            margin-top: 0;
        }
        .success-box {
            padding: 1rem;
            background-color: #D5F5E3;
            border-radius: 0.5rem;
            border-left: 0.5rem solid #2ECC71;
        }
        .info-box {
            padding: 1rem;
            background-color: #D6EAF8;
            border-radius: 0.5rem;
            border-left: 0.5rem solid #3498DB;
        }
        .warning-box {
            padding: 1rem;
            background-color: #FCF3CF;
            border-radius: 0.5rem;
            border-left: 0.5rem solid #F1C40F;
        }
        .error-box {
            padding: 1rem;
            background-color: #F9EBEA;
            border-radius: 0.5rem;
            border-left: 0.5rem solid #E74C3C;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            white-space: pre-wrap;
            border-radius: 4px 4px 0 0;
        }
        .metric-card {
            background-color: #f9f9f9;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.3s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #4B7BEC;
        }
        .metric-label {
            font-size: 1rem;
            color: #666;
        }
        .card-container {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 1rem;
        }
        .card {
            flex: 1;
            min-width: 200px;
            background-color: white;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .card-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # App header
    st.markdown('<h1 class="main-header">ChromaLens</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">A powerful interface for ChromaDB vector database management</p>', unsafe_allow_html=True)

def show_success(message):
    """Display a success message box"""
    st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)

def show_info(message):
    """Display an info message box"""
    st.markdown(f'<div class="info-box">{message}</div>', unsafe_allow_html=True)

def show_warning(message):
    """Display a warning message box"""
    st.markdown(f'<div class="warning-box">{message}</div>', unsafe_allow_html=True)

def show_error(message):
    """Display an error message box"""
    st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)