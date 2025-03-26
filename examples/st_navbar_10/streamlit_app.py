import os

import streamlit as st
from streamlit_navigation_bar import st_navbar

import pages as pg


st.set_page_config(initial_sidebar_state="collapsed")

pages = [
    st.Page(pg.show_install, title="Install"),
    st.Page(pg.show_user_guide, title="User Guide"),
    st.Page(pg.show_api, title="API"),
    st.Page(pg.show_examples, title="Examples"),
    st.Page(pg.show_community, title="Community"),
    "GitHub",
]

parent_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(parent_dir, "cubes.svg")
urls = {"GitHub": "https://github.com/gabrieltempass/streamlit-navigation-bar"}
styles = {
    "nav": {
        "background-color": "royalblue",
        "justify-content": "left",
    },
    "img": {
        "padding-right": "14px",
    },
    "span": {
        "color": "white",
        "padding": "14px",
    },
    "active": {
        "background-color": "white",
        "color": "black",
        "font-weight": "normal",
        "padding": "14px",
    },
}

css = """
.navbar-text {
  color: white;
  display: block;
  text-align: center;
}
.navbar-span {
    padding: 14px;
}
span.active > .navbar-text {
    background-color: white;
    color: black;
    font-weight: normal;
}

"""


options = {
    "show_menu": False,
    "show_sidebar": False,
}

page = st_navbar(
    pages,
    logo_path=logo_path,
    urls=urls,
    styles=styles,
    css=css,
    options=options,
)
if page == "Home":
    pg.show_home()
else:
    page.run()
