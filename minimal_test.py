#!/usr/bin/env python3
"""
Minimal test app for Azure deployment.
This should work with any startup command.
"""

import streamlit as st

st.title("Hello Azure!")
st.write("If you can see this, Azure deployment is working!")

if st.button("Click me"):
    st.write("Button clicked! Success!")
