"""
Streamlit Dashboard - Web interface for monitoring
Run with: streamlit run tools/dashboard.py
"""

try:
    import streamlit as st
    
    st.title("Crypto Trading Bot Dashboard")
    st.write("Portfolio monitoring interface")
    st.write("Install streamlit: pip install streamlit")
except ImportError:
    print("Streamlit not installed. Run: pip install streamlit")
