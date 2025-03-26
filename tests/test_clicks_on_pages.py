from __future__ import annotations

from contextlib import contextmanager
from time import sleep


import pytest

from playwright.sync_api import Page, expect

LOCAL_TEST = False

PORT = "8503" if LOCAL_TEST else "8699"


@contextmanager
def run_streamlit(example_app):
    """Run the streamlit app at examples/streamlit_app.py on port 8599"""
    import subprocess

    if LOCAL_TEST:
        try:
            yield 1
        finally:
            pass
    else:
        p = subprocess.Popen(
            [
                "streamlit",
                "run",
                example_app,
                "--server.port",
                PORT,
                "--server.headless",
                "true",
            ]
        )

        sleep(5)

        try:
            yield 1
        finally:
            p.kill()


@pytest.mark.parametrize("index", [3, 10])
def test_screenshot(page: Page, index):
    i = index
    with run_streamlit(f"examples/st_navbar_{i}/streamlit_app.py"):
        page.goto(f"localhost:{PORT}")
        page.set_viewport_size({"width": 700, "height": 700})
        expect.set_options(timeout=5_000)
        sleep(1)

        for title in [
            "Install",
            "User Guide",
            "API",
            "Examples",
            "Community",
        ]:
            page.frame_locator(
                'internal:attr=[title="streamlit_navigation_bar.st_navbar"]'
            ).get_by_role("link", name=title).click()

            expect(page.get_by_role("heading", name=title)).to_be_visible()
