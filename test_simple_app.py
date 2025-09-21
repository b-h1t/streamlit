#!/usr/bin/env python3
"""
Simple test app to verify Azure deployment is working.
"""

import streamlit as st

st.title("🎉 Azure Deployment Test - SUCCESS!")
st.write("If you can see this page, your Azure deployment is working correctly!")

st.header("Test Information")
st.write(f"**Python version:** {st.__version__}")
st.write(f"**Streamlit version:** {st.__version__}")

st.header("Next Steps")
st.write("1. ✅ Azure deployment is working")
st.write("2. ✅ Streamlit is running")
st.write("3. ✅ You can now deploy your main app")

if st.button("Test Button"):
    st.success("Button clicked! Everything is working perfectly!")
    st.balloons()

st.info("You can now go back to your main Document Assignment & Labelling app!")
