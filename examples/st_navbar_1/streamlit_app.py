import streamlit as st
from streamlit_navigation_bar import st_navbar


page = st_navbar(["*", "*", "*", "*", "*"])
st.write(page)

"This should break the visual tests again 1"
