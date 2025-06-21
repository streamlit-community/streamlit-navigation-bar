import os
import base64
from importlib.metadata import version as _version

from typing import TYPE_CHECKING, Callable, Union

from typing_extensions import TypeAlias

from streamlit.navigation.page import StreamlitPage
import streamlit as st

import streamlit.components.v1 as components
from jinja2 import FileSystemLoader, Environment

from pathlib import Path
from streamlit_navigation_bar.match_navbar import MatchNavbar
from streamlit_navigation_bar.errors import (
    check_pages,
    check_selected,
    check_logo_path,
    check_logo_page,
    check_urls,
    check_styles,
    check_options,
    check_adjust,
    check_key,
)

# These are needed for setup_navigation
from streamlit.runtime.pages_manager import PagesManager
from streamlit.errors import StreamlitAPIException
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from streamlit.proto.Navigation_pb2 import Navigation as NavigationProto

from streamlit.runtime.scriptrunner_utils.script_run_context import (
    get_script_run_ctx,
)

if TYPE_CHECKING:
    from streamlit.source_util import PageHash, PageInfo

SectionHeader: TypeAlias = str
PageType: TypeAlias = Union[str, Path, Callable[[], None], StreamlitPage]

_RELEASE = "STREAMLIT_COMMUNITY_DEVELOPMENT" not in os.environ

if not _RELEASE:
    _st_navbar = components.declare_component(
        "st_navbar",
        url="http://localhost:5173",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _st_navbar = components.declare_component(
        "st_navbar",
        path=build_dir,
    )


def print_version():
    """Show the installed version of the Streamlit Navigation Bar package."""
    version = _version("streamlit-navigation-bar")
    print(f"Streamlit Navigation Bar, version {version}")


def _encode_svg(path):
    """Encode an SVG to base64, from an absolute path."""
    svg = open(path).read()
    return base64.b64encode(svg.encode("utf-8")).decode("utf-8")


def _prepare_urls(urls, pages):
    """Build dict with given hrefs, targets and defaults where omitted."""
    if urls is None:
        urls = {}
    for page in pages:
        # Add {page: [href, target]} to the `urls` dict.
        if page in urls:
            urls[page] = [urls[page], "_blank"]
        else:
            urls[page] = ["#", "_self"]
    return urls


def _prepare_icons(icons):
    if icons is None:
        icons = {}

    icons = {
        k: v.strip(":").split("/")[-1].replace("_", " ").title().replace(" ", "")
        for k, v in icons.items()
    }

    return icons


def _prepare_options(options):
    """Build dict with given options, state and defaults where omitted."""
    available = {
        "show_menu": True,
        "show_sidebar": True,
        "hide_nav": True,
        "fix_shadow": True,
        "use_padding": True,
        "sidebar_under_navbar": True,
    }
    for option in available:
        if isinstance(options, dict) and option in options:
            available[option] = options[option]
        elif isinstance(options, bool) and not options:
            available[option] = options
    return available


def _adjust(css):
    """Apply a CSS adjustment."""
    st.html("<style>" + css + "</style>")


def get_path(directory):
    """Get the abs path for a directory in the same location as this file."""
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(parent_dir, directory)


def load_env(path):
    """Load the Jinja environment from a given absolute path."""
    loader = FileSystemLoader(path)
    return Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)


def position_body(key, use_padding):
    """
    Add a stylized container to the app that adjusts the position of the body.

    Insert a container into the app, to add an ``st.html``, using either the
    "with" notation or by calling the method directly on the returned object.

    This container serves to position the body of the app in the y axis of the
    window. Which can be the same as the default in Streamlit (6rem from the
    top), or right below the navbar.

    It does so by having a unique CSS selector, and being inserted in a <div>
    palced immediately before the <div> of the body of the app. Then, it styles
    the margin-bottom property and moves the body to the desired position.

    Parameters
    ----------
    key : str, int or None
        A key associated with this container. This needs to be unique since all
        styles will be applied to the container with this key.

    Returns
    -------
    container : DeltaGenerator
        A container object. ``st.html`` can be added to this container using
        either the ``"with"`` notation or by calling methods directly on the
        returned object.
    """
    if use_padding:
        # The position of the body will be 6rem from the top.
        margin_bottom = "-4.875rem"
    else:
        # The position of the body will be right below the navbar.
        margin_bottom = "-8rem"

    html = f"""
        <style>
            div[data-testid="stVerticalBlockBorderWrapper"]:has(
                div[data-testid="stVerticalBlock"]
                > div.element-container
                > div.stHtml
                > span.{key}
            ) {{
                margin-bottom: {margin_bottom};
            }}
        </style>
        <span class='{key}'></span>
        """
    container = st.container()
    container.html(html)
    return container


def adjust_css(styles, options, key, path):
    """
    Apply CSS adjustments to display the navbar correctly.

    By default, Streamlit limits the position of components in the web app to
    a certain width and adds a padding to the top. This function renders Jinja
    templates to adjust the CSS and display the navbar at the full width at the
    top of the window, among other options that can be toggled on or off.

    It also matches the style, theme and configuration between the navbar and
    Streamlit's User Interface (UI) elements, to make them look seamless.

    Parameters
    ----------
    styles : dict of {str : dict of {str : str}}
        Apply CSS styles to desired targets, through a dictionary with the HTML
        tag or pseudo-class name as the key and another dictionary to style it
        as the value. In the second dictionary, the key-value pair is the name
        of a CSS property and the value it takes, both in string format. It
        accepts CSS variables to be passed as values.

        The available HTML tags are: ``"nav"``, ``"div"``, ``"ul"``, ``"li"``,
        ``"a"``, ``"img"`` and ``"span"``.

        The available pseudo-classes are: ``"active"`` and ``"hover"``, which
        direct the styling to the ``"span"`` tag. The menu and sidebar buttons
        are only styled by ``"hover"`` (if they are set to ``True`` in
        `options`). Currently, ``"hover"`` only accepts two CSS properties,
        they are: ``"color"`` and ``"background-color"``.
    options : bool or dict of {str : bool}
        Customize the navbar with options that can be toggled on or off. It
        accepts a dictionary with the option name as the key and a boolean as
        the value. The available options are: ``"show_menu"``,
        ``"show_sidebar"``, ``"hide_nav"``, ``"fix_shadow"`` and
        ``"use_padding"``.

        It is also possible to toggle all options to the same state. Simply
        pass ``True`` or ``False`` to `options`.
    key : str, int or None
        A key associated with the container that adjusts the CSS. This needs to
        be unique since all styles will be applied to the container with this
        key.
    path : str
        The absolute path to the directory containing the Jinja templates with
        the CSS adjustments.
    """
    ui = MatchNavbar(styles, key)

    ui.height = ui.get_value(
        css_property="height",
        targets=["nav"],
        default="2.875rem",
    )
    ui.hover_bg_color = ui.get_value(
        css_property="background-color",
        targets=["hover"],
        default="transparent",
    )
    ui.color = ui.get_value(
        css_property="color",
        targets=["span"],
        default="rgb(49, 51, 63)",
        theme_config="textColor",
    )
    ui.bg_color = ui.get_value(
        css_property="background-color",
        targets=["nav"],
        default="rgb(240, 242, 246)",
        theme_config="secondaryBackgroundColor",
    )
    ui.hover_color = ui.get_value(
        css_property="color",
        targets=["hover", "span"],
        default="rgb(49, 51, 63)",
        theme_config="textColor",
    )

    options = _prepare_options(options)
    margin = options["show_menu"] or options["show_sidebar"]
    key = f"st_navbar_key_{key}"

    env = load_env(path)
    template = env.get_template("options.css")
    css = template.render(
        ui=ui,
        options=options,
        margin=margin,
        key=key,
    )
    with position_body(key, options["use_padding"]):
        _adjust(css)


# A placeholder object to implement the default rules for `selected`.
sentinel = object()


def st_navbar(
    pages,
    right=None,
    selected=sentinel,
    logo_path=None,
    logo_page="Home",
    urls=None,
    icons=None,
    styles=None,
    css=None,
    options=True,
    adjust=True,
    on_change=None,
    allow_reselect=False,
    set_path=False,
    links=None,
    key=None,
):
    """
    Place a navigation bar in your Streamlit app.

    If there is no ``st.set_page_config`` command on the app page,
    ``st_navbar`` must be the first Streamlit command used, and must only be
    set once per page. If there is a ``st.set_page_config`` command, then
    ``st_navbar`` must be the second one, right after it.

    Parameters
    ----------
    pages : list of str
        A list with the name of each page that will be displayed in the
        navigation bar.
    right : list of str
        A list with the name of each page that will be displayed in the
        right part of the navigation bar.
    selected : str or None, optional
        The preselected page on first render. It can be a name from `pages`,
        the `logo_page` (when there is a logo) or ``None``. Defaults to the
        `logo_page` value, if there is a logo. In case there is not one,
        defaults to the first page of the `pages` list. When set to ``None``,
        it will initialize empty and return ``None`` until the user selects a
        page.
    logo_path : str, optional
        The absolute path to an SVG file for a logo. It will be shown on the
        left side of the navigation bar. Defaults to ``None``, where no logo is
        displayed.
    logo_page : str or None, default="Home"
        The page value that will be returned when the logo is selected, if
        there is one. Defaults to ``"Home"``. For a non-clickable logo, set
        this to ``None``.
    urls : dict of {str : str}, optional
        A dictionary with the page name as the key and an external URL as the
        value, both as strings. The page name must be contained in the `pages`
        list. The URL will open in a new window or tab.
    icons : dict of {str : str}, optional
        A dictionary with the page name as the key and a reference to an icon
        in the Material Symbols library in the format
        ``":material/icon_name:"`` where "icon_name" is the name of the icon
        in snake case.
    css : str, optional
        Custom CSS styles. Allows arbitrary css to be added to the component.
    styles : dict of {str : dict of {str : str}}, optional
        Apply CSS styles to desired targets, through a dictionary with the HTML
        tag or pseudo-class name as the key and another dictionary to style it
        as the value. In the second dictionary, the key-value pair is the name
        of a CSS property and the value it takes, both in string format. It
        accepts CSS variables to be passed as values. Defaults to ``None``,
        where just the default style is applied.

        The available HTML tags are: ``"nav"``, ``"div"``, ``"ul"``, ``"li"``,
        ``"a"``, ``"img"`` and ``"span"``.

        The available pseudo-classes are: ``"active"`` and ``"hover"``, which
        direct the styling to the ``"span"`` tag. The menu and sidebar buttons
        are only styled by ``"hover"`` (if they are set to ``True`` in
        `options`). Currently, ``"hover"`` only accepts two CSS properties,
        they are: ``"color"`` and ``"background-color"``.

        To understand the Document Object Model from the navbar, the CSS
        variables and the default style, go to the API reference in the Notes
        section.
    options : bool or dict of {str : bool}, default=True
        Customize the navbar with options that can be toggled on or off. It
        accepts a dictionary with the option name as the key and a boolean as
        the value. The available options are: ``"show_menu"``,
        ``"show_sidebar"``, ``"hide_nav"``, ``"fix_shadow"`` and
        ``"use_padding"``. Check the API reference in the Notes section for a
        description of each one.

        It is also possible to toggle all options to the same state. Simply
        pass ``True`` to `options`, which is the parameter default value, or
        ``False``.
    adjust : bool, default=True
        When set to ``True`` (default), it overrides some Streamlit behaviors
        and makes a series of CSS adjustments to display the navbar correctly.

        In most cases, the CSS adjustments do not interfere with the rest of
        the web app, however there could be some situations where this occurs.
        If this happens, or it is desired to disable all of them, pass
        ``False`` to `adjust` and, when necessary, make your own CSS
        adjustments with ``st.html``.

        If set to ``False``, it will also disable all adjustments made by
        `options`, regardless of whether they are on or off.
    allow_reselect : bool, default=False
        By default clicking on the currently selected page will not do
        anything.

        If set to ``True``, this will invoke the on_change callback even
        if the clicked page is currently selected.
    set_path : bool, default=False
        If set to ``True``, selecting a page will also update the browser URL.

        This option makes the navigation bar behave more like streamlit's
        native navigation component. It does cause brief flicker in the
        navigation bar for each change.
    links : list
        A list of stylesheets to be included.
        This can be used to include new icons.
    key : str or int, optional
        A string or integer to use as a unique key for the component. If this
        is omitted, a key will be generated for the widget based on its
        content. Multiple navbars of the same type may not share the same key.

    Returns
    -------
    page : str or None
        The page selected by the user. If there has been no interaction yet,
        returns the preselected page or ``None``.

    Notes
    -----
    To learn more about how to use the navbar, check the API reference
    available at:

    https://github.com/gabrieltempass/streamlit-navigation-bar/wiki/API-reference

    Examples
    --------
    >>> import streamlit as st
    >>> from streamlit_navigation_bar import st_navbar
    >>> page = st_navbar(
    ...     ["Home", "Documentation", "Examples", "Community", "About"]
    ... )
    >>> st.write(page)

    .. output::
       https://st-navbar-1.streamlit.app/
       height: 300px
    """
    # Do some trickery to differentiate between
    # the left part of the navigation menu
    # and the right part
    left = pages
    right = right or []
    pages = left + right

    check_pages(pages)
    check_selected(selected, logo_page, logo_path, pages)
    check_logo_path(logo_path)
    check_logo_page(logo_page)
    check_urls(urls, pages)
    check_styles(styles)
    check_options(options)
    check_adjust(adjust)
    check_key(key)

    if selected is sentinel:
        if logo_path is not None:
            default = logo_page
        else:
            default = pages[0] if isinstance(pages[0], str) else pages[0].url_path
    else:
        default = selected

    default = default.lower()

    base64_svg = None
    if logo_path is not None:
        base64_svg = _encode_svg(logo_path)

    urls = _prepare_urls(urls, pages)

    if icons is None:
        icons = {}
    icons = {k: v.strip(":").split("/")[-1] for k, v in icons.items()}

    page_objects = {}
    page_list = []

    # disable regular mpa uses
    PagesManager.uses_pages_directory = False

    if logo_path:
        st_page = st.Page(
            lambda: None,
            title=logo_page,
            icon=icons.get(logo_page),
            url_path=logo_page.lower(),
        )
        page_list.append(st_page)

    # TODO: code here is weird
    def to_dict(page):
        if isinstance(page, StreamlitPage):
            page._default = False
            page_objects[page.url_path] = page
            page_list.append(page)
            return {
                "title": page.title,
                "icon": page.icon or None,
                "url": urls.get(page.title, ["#", "_self"]),
                "key": page.url_path,
            }
        else:
            st_page = st.Page(
                lambda: None,
                title=page,
                url_path=page.lower(),
            )
            page_list.append(st_page)
            return {
                "title": page,
                "icon": icons.get(page),
                "url": urls.get(page, ["#", "_self"]),
                "key": page.lower(),
            }

    left = [to_dict(title) for title in left]
    right = [to_dict(title) for title in right]

    default_page = next(page for page in page_list if default == page.url_path)
    default_page_original_key = default_page.url_path
    default_page._default = True

    # Prepare frontend navigation
    pagehash_to_pageinfo: dict[PageHash, PageInfo] = {}
    for page in page_list:
        if isinstance(page._page, Path):
            script_path = str(page._page)
        else:
            script_path = ""

        script_hash = page._script_hash
        if script_hash in pagehash_to_pageinfo:
            # The page script hash is soley based on the url path
            # So duplicate page script hashes are due to duplicate url paths
            raise StreamlitAPIException(
                f"Multiple Pages specified with URL pathname {page.url_path}. "
                "URL pathnames must be unique. The url pathname may be "
                "inferred from the filename, callable name, or title."
            )

        pagehash_to_pageinfo[script_hash] = {
            "page_script_hash": script_hash,
            "page_name": page.title,
            "icon": page.icon,
            "script_path": script_path,
            "url_pathname": page.url_path,
        }

    ctx = get_script_run_ctx()
    ctx.pages_manager.set_pages(pagehash_to_pageinfo)

    # This allows deep links
    found_page = ctx.pages_manager.get_page_script(
        fallback_page_hash=default_page._script_hash
    )

    if found_page and found_page["page_script_hash"] != default_page._script_hash:
        default = found_page["url_pathname"]

    links = links or []

    # Now run our own component
    page_name, _ = _st_navbar(
        left=left,
        right=right,
        # This is required for the first call
        # to ensure we return two values
        default=(default, None),
        base64_svg=base64_svg,
        logo_page=logo_page.lower(),
        styles=styles,
        css=css,
        on_change=on_change,
        allow_reselect=allow_reselect,
        links=links,
        key=key,
    )
    if adjust:
        adjust_css(styles, options, key, get_path("templates"))

    page_name = page_name.lower()
    if page_name == default_page_original_key:
        page_to_return = default_page
    else:
        page_to_return = next(_ for _ in page_list if _.url_path == page_name)
    page_to_return._can_be_called = True

    msg = ForwardMsg()
    msg.navigation.position = NavigationProto.Position.HIDDEN
    msg.navigation.expanded = False

    msg.navigation.sections[:] = [""]
    for page in page_list:
        p = msg.navigation.app_pages.add()
        p.page_script_hash = page._script_hash
        p.page_name = page.title
        p.icon = page.icon
        p.is_default = page._default
        p.section_header = ""
        p.url_pathname = page.url_path

    if set_path:
        msg.navigation.page_script_hash = page_to_return._script_hash
    else:
        msg.navigation.page_script_hash = default_page._script_hash

    # Set the current page script hash to the page that is going to be executed
    ctx.set_mpa_v2_page(page_to_return._script_hash)

    # This will either navigation or yield if the page is not found
    ctx.enqueue(msg)

    # For backwards compatibility
    # if the user passed a string iso a page we will return the title
    if page_name in page_objects:
        return page_to_return
    else:
        return page_to_return.title
