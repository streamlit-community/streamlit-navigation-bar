import streamlit as st
from streamlit_navigation_bar import st_navbar

css = """
span[data-text="Home"] > div {
    border: 1px solid red !important;
}
"""

page = st_navbar(
    ["Home", "Documentation", "Examples", "Community", "About"],
    css=css
)
st.write(page)
