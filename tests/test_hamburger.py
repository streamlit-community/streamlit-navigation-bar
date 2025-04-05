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


@pytest.mark.parametrize("index", [4])
def test_pointer_events_on_page(page: Page, index):
    i = index
    with run_streamlit(f"examples/st_navbar_{i}/streamlit_app.py"):
        page.goto(f"localhost:{PORT}")
        page.set_viewport_size({"width": 1000, "height": 700})
        expect.set_options(timeout=5_000)
        sleep(1)
        page.get_by_test_id("stBaseButton-secondary").click()
        expect(page.locator("p").filter(has_text="True")).to_be_visible()
        expect(page.get_by_role("code")).to_contain_text("True")


@pytest.mark.parametrize("index", [4])
def test_pointer_events_on_menu(page: Page, index):
    i = index
    with run_streamlit(f"examples/st_navbar_{i}/streamlit_app.py"):
        page.goto(f"localhost:{PORT}")
        page.set_viewport_size({"width": 1000, "height": 700})
        expect.set_options(timeout=5_000)
        sleep(1)

        page.get_by_test_id("stBaseButton-headerNoPadding").click()
        expect(page.get_by_text("About")).to_be_visible()
        expect(page.get_by_text("Record a screencast")).to_be_visible()


@pytest.mark.parametrize("index", [2])
def test_pointer_events_on_menu_wide_mode(page: Page, index):
    i = index
    with run_streamlit(f"examples/st_navbar_{i}/streamlit_app.py"):
        page.goto(f"localhost:{PORT}")
        page.set_viewport_size({"width": 1000, "height": 700})
        expect.set_options(timeout=5_000)
        sleep(1)

        page.get_by_test_id("stMainMenu").get_by_test_id(
            "stBaseButton-headerNoPadding"
        ).click()
        expect(page.get_by_text("About")).to_be_visible()
        expect(page.get_by_text("Record a screencast")).to_be_visible()
