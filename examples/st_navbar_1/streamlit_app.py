import streamlit as st
from streamlit_navigation_bar import st_navbar


page = st_navbar(["A", "B", "C", "D", "E"])
st.write(page)
st.write("This should fail")
