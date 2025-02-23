import streamlit as st
from streamlit_navigation_bar import st_navbar

css = """
span[data-text="Home"] > div {
    color: red;
    pointer-events: none;
}
"""

page = st_navbar(["Home", "Documentation", "Examples", "Community", "About"], css=css)
st.write(page)
