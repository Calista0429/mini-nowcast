"""Crop the README screenshots down to the regions the slide deck uses.

    uv run python scripts/crop_deck_assets.py     # docs/screenshots -> docs/deck-assets
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "screenshots"
DST = ROOT / "docs" / "deck-assets"

CROPS = {
    # name: (source file, box) - boxes are in the 2880x1840 screenshot coordinate space
    "home": ("01-home.png", (600, 200, 2860, 700)),        # title + KPI row, without the sidebar
    "assistant": ("06-assistant.png", (760, 650, 2740, 1072)),  # answer + the ✅ verification row
}


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for name, (src, box) in CROPS.items():
        out = DST / f"{name}.png"
        Image.open(SRC / src).crop(box).save(out)
        print(f"[ok] {out.relative_to(ROOT)}  {Image.open(out).size}")


if __name__ == "__main__":
    main()
