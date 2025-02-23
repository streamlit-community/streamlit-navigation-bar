import streamlit as st
from streamlit_navigation_bar import st_navbar

styles = {
    "nav": {
        "background-color": "rgb(123, 209, 146)",
        "justify-content": "space-between",
    },
    "div": {
        "max-width": "32rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "color": "rgb(49, 51, 63)",
        "margin": "0 0.125rem",
        "padding": "0.4375rem 0.625rem",
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.35)",
    },
}

icons = {"Documentation": ":material/add_home_work:"}

page = st_navbar(
    ["Home", "Documentation", "Examples", "Community", "About"],
    styles=styles,
    icons=icons,
)

st.write(page)
x = st.button("click me")
st.write(x)
