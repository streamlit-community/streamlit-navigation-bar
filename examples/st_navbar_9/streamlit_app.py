import streamlit as st
from streamlit_navigation_bar import st_navbar

if "show_dialog" not in st.session_state:
    st.session_state.show_dialog = True


def reset_state():
    st.session_state.show_dialog = True


page = st_navbar(
    ["Home", "Documentation", "Examples", "Account", "About"],
    on_change=reset_state,
    allow_reselect=True,
    links=["https://fonts.googleapis.com/icon?family=Material+Icons"],
)

st.write(page)


@st.dialog("My account")
def config_user():
    col1, col2, col3 = st.columns([1, 0.75, 1])
    st.text_input("**User name**", disabled=True)
    st.text_input("**Real name**", disabled=True)
    st.text_input("**Role**", disabled=True)
    st.session_state.show_dialog = False


if page == "Account" and st.session_state.show_dialog:
    config_user()

st.button("click me")
