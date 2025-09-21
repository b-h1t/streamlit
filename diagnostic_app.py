#!/usr/bin/env python3
"""
Diagnostic app to check what's being served at the Azure URL.
"""

import streamlit as st
import os
import sys

st.title("🔍 Azure Diagnostic App")
st.write("**URL:** https://benstreamlit101.azurewebsites.net/")
st.write("**Status:** ✅ App is running!")

st.header("System Information")
st.write(f"**Python version:** {sys.version}")
st.write(f"**Current directory:** {os.getcwd()}")
st.write(f"**Files in directory:** {os.listdir('.')}")

st.header("Streamlit Status")
st.write("✅ Streamlit is working correctly")
st.write("✅ Azure deployment is successful")

st.header("Next Steps")
st.write("1. If you see this page, your Azure deployment is working")
st.write("2. You can now switch back to your main app")
st.write("3. Change startup command back to: `python3 -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0`")

if st.button("Test Button"):
    st.success("🎉 Everything is working perfectly!")
    st.balloons()

st.info("This is a diagnostic page. Once confirmed working, switch back to your main Document Assignment & Labelling app.")
