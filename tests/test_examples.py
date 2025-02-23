from __future__ import annotations

from contextlib import contextmanager
from time import sleep
import cv2
import numpy as np
import os
import shutil

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


def mse(img1, img2):
    h, w, _ = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff**2)
    mse = err / (float(h * w))
    return mse


@pytest.mark.parametrize("index", list(range(1, 9)))
def test_screenshot(page: Page, index):
    i = index
    with run_streamlit(f"examples/st_navbar_{i}/streamlit_app.py"):
        page.goto(f"localhost:{PORT}")
        page.set_viewport_size({"width": 700, "height": 700})
        expect.set_options(timeout=5_000)
        sleep(3)
        page.screenshot(path=f"/tmp/screenshot_{i}.png")
        current = cv2.imread(f"/tmp/screenshot_{i}.png")
        if os.path.exists(f"examples/screenshots/screenshot_{i}.png"):
            original = cv2.imread(f"examples/screenshots/screenshot_{i}.png")
            assert mse(current, original) == 0.0
        else:
            shutil.copy(
                f"/tmp/screenshot_{i}.png", f"examples/screenshots/screenshot_{i}.png"
            )
            raise Exception("no screenshot made")
