from __future__ import annotations

from contextlib import contextmanager
from time import sleep
import os
import shutil

from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch


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


@pytest.mark.parametrize("index", list(range(1, 10)))
def test_screenshot(page: Page, index):
    i = index
    with run_streamlit(f"examples/st_navbar_{i}/streamlit_app.py"):
        page.goto(f"localhost:{PORT}")
        page.set_viewport_size({"width": 700, "height": 700})
        expect.set_options(timeout=5_000)
        sleep(1.5)
        page.screenshot(path=f"/tmp/screenshot_new_{i}.png")

        img_a = Image.open(f"/tmp/screenshot_new_{i}.png")

        if os.path.exists(f"examples/screenshots/screenshot_{i}.png"):
            img_b = Image.open(f"examples/screenshots/screenshot_{i}.png")

            img_diff = Image.new("RGBA", img_a.size)
            # note how there is no need to specify dimensions
            mismatch = pixelmatch(img_a, img_b, img_diff, threshold=0.2, includeAA=True)

            img_diff.save(f"/tmp/screenshot_diff_{i}.png")
            assert mismatch < 50

        else:
            shutil.copy(
                f"/tmp/screenshot_new_{i}.png",
                f"examples/screenshots/screenshot_{i}.png",
            )
            raise Exception("no screenshot available, generating new")
