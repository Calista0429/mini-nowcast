"""Capture the README screenshots from a running app.

    make app                       # in one terminal
    uv run --with playwright python scripts/capture_screenshots.py

The assistant shot asks a real question, so it needs a working LLM_API_KEY.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"
OUT = Path(__file__).resolve().parents[1] / "docs" / "screenshots"
VIEWPORT = {"width": 1440, "height": 920}


def settle(page, seconds: float = 2.5) -> None:
    """Streamlit streams its DOM and Plotly animates, so wait after each interaction."""
    page.wait_for_load_state("networkidle")
    time.sleep(seconds)


def shot(page, name: str, scroll_to: str | None = None, wait: float = 2.5) -> None:
    if scroll_to:
        # Streamlit scrolls an inner container, so mouse.wheel does nothing here;
        # scrolling a heading into view is what actually moves the page.
        # block:"start" forces the heading to the top; scroll_into_view_if_needed() is a no-op
        # when the element is already partly visible at the bottom edge.
        page.get_by_text(scroll_to, exact=False).first.evaluate(
            "e => e.scrollIntoView({block: 'start'})"
        )
        time.sleep(0.8)
    settle(page, wait)
    path = OUT / f"{name}.png"
    page.screenshot(path=path)
    print(f"[ok] {path.relative_to(Path.cwd())}  ({path.stat().st_size // 1024} KB)")


def open_page(page, label: str):
    page.get_by_role("link", name=label).click()
    settle(page, 3)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=2)
        page.goto(URL, wait_until="networkidle")
        settle(page, 4)

        shot(page, "01-home")

        open_page(page, "物価指数")
        shot(page, "02-price-index")
        shot(page, "03-contributions", scroll_to="寄与度：どの商品が物価を動かしたか", wait=3)

        open_page(page, "データ品質")
        shot(page, "04-cleaning", wait=3)
        shot(page, "05-quality-monitor", scroll_to="日次データ量モニタリング", wait=3)

        open_page(page, "AIアシスタント")
        page.get_by_role("button", name="2011年11月の物価上昇に最も寄与した商品トップ5は？").click()
        # "SQL と結果" only renders once the answer is complete; "数値検証" also appears
        # in the page subtitle, so it is not a usable signal.
        page.wait_for_selector("text=SQL と結果", timeout=90_000)
        shot(page, "06-assistant", wait=4)

        browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"failed: {type(e).__name__}: {e}", file=sys.stderr)
        print("is the app running?  make app", file=sys.stderr)
        raise SystemExit(1)
