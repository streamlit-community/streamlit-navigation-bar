import streamlit as st
from streamlit_navigation_bar import st_navbar


def about():
    st.write("call about page")


about = st.Page(about, title="About")

page = st_navbar(
    ["Home", "Documentation", "Examples", "Account", about],
    allow_reselect=True,
    options={
        "use_padding": True,
    },
    key="navbar",
)

st.session_state.previous_page = page

if page == about:
    page.run()
else:
    st.write(page)
