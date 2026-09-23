"""Shared data access and chart styling for the Streamlit pages."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assistant import db  # noqa: E402

# Reference palette (validated categorical order; status colours reserved for alerts).
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
CRITICAL = "#d03b3b"
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"

CATEGORY_JA = {
    "bags_storage": "バッグ・収納",
    "home_decor": "インテリア雑貨",
    "home_fragrance_lighting": "キャンドル・照明",
    "jewellery_accessories": "アクセサリー",
    "kitchen_tableware": "キッチン・食器",
    "seasonal_christmas": "クリスマス",
    "seasonal_easter": "イースター",
    "stationery_gift_wrap": "文具・ラッピング",
    "toys_kids": "玩具・キッズ",
    "other": "その他",
}


@st.cache_data(show_spinner=False)
def q(sql: str) -> pd.DataFrame:
    return db.query(sql)


def style(fig: go.Figure, height: int = 380, y_title: str | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=36, b=8),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", color=INK_2, size=13),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hoverlabel=dict(bgcolor="white", font_color=INK),
    )
    fig.update_xaxes(showgrid=False, linecolor=AXIS, tickfont_color=MUTED, title=None)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont_color=MUTED, title=y_title,
                     title_font_color=MUTED)
    fig.update_traces(selector=dict(type="scatter"), line_width=2)
    return fig
