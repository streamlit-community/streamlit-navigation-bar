def test_release():
    from streamlit_navigation_bar import _RELEASE

    assert _RELEASE, "Release needs to be set to True after finished testing locally"
