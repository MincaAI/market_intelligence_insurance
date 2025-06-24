from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.set_page_config(page_title="App")
st.title("App")
st.write("Welcome! Use the sidebar to navigate between T&C extraction, review analysis, insurance comparison, and other analysis.")

st.info("Select a section from the sidebar to get started.") 