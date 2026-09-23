import json

import plotly.express as px
import streamlit as st

from common import ROOT, SERIES, style

st.set_page_config(page_title="AIアシスタント", page_icon="💬", layout="wide")
st.title("AIアシスタント")
st.caption("自然言語の質問 → 意味層に基づくSQL生成 → 安全検査 → 読み取り専用で実行 → 結果のみに基づく回答 → 数値検証")

from assistant.agent import Assistant  # noqa: E402


@st.cache_resource
def get_assistant() -> Assistant:
    return Assistant()


SAMPLES = [
    "2011年で売上が一番多かった月は？金額も。",
    "2011年1月から11月で価格上昇率が最も高いカテゴリは？",
    "2011年11月の物価上昇に最も寄与した商品トップ5は？",
    "英国以外で売上が多い国トップ5",
    "哪个星期几的平均日销售额最高？",
    "2011年の営業利益率は？",
]

if "history" not in st.session_state:
    st.session_state.history = []

cols = st.columns(3)
clicked = None
for i, s in enumerate(SAMPLES):
    if cols[i % 3].button(s, use_container_width=True):
        clicked = s
question = st.chat_input("データについて質問してください（日本語・中文・English）") or clicked

if question:
    with st.spinner("SQLを生成して実行しています…"):
        st.session_state.history.insert(0, get_assistant().ask(question))


def render_chart(res) -> None:
    rows, chart = res.rows, res.chart or {}
    x, y = chart.get("x"), chart.get("y")
    if chart.get("type") not in ("line", "bar") or x not in rows.columns or y not in rows.columns or len(rows) < 2:
        return
    color = chart.get("color") if chart.get("color") in rows.columns else None
    if color and rows[color].nunique() > 3:  # beyond 3 series, colours stop being distinguishable
        return
    make = px.line if chart["type"] == "line" else px.bar
    fig = make(rows, x=x, y=y, color=color, color_discrete_sequence=SERIES)
    if chart["type"] == "bar":
        fig.update_layout(hovermode="closest")
    st.plotly_chart(style(fig, 320), use_container_width=True)


for res in st.session_state.history:
    with st.container(border=True):
        st.markdown(f"**Q. {res.question}**")
        if res.declined_reason:
            st.warning(f"回答できません：{res.declined_reason}")
        elif res.error:
            st.error(res.error)
        else:
            st.markdown(res.answer)
            if res.cited_numbers:
                badges = " ".join(
                    f"✅ `{n.text}`" if n.verified else f"⚠️ `{n.text}`（結果に存在しない）" for n in res.cited_numbers
                )
                st.caption(f"数値検証：{badges}")
            render_chart(res)
            with st.expander(f"SQL と結果（{len(res.rows)} 行）"):
                st.code(res.sql, language="sql")
                st.dataframe(res.rows, hide_index=True, use_container_width=True)
                if res.assumptions:
                    st.markdown("**解釈上の前提**\n" + "\n".join(f"- {a}" for a in res.assumptions))
        if len(res.attempts) > 1:
            with st.expander(f"🔁 自己修正 {len(res.attempts) - 1} 回"):
                for i, a in enumerate(res.attempts, 1):
                    st.markdown(f"**試行 {i}** — {'❌ ' + a.error if a.error else '✅ 成功'}")
                    st.code(a.sql, language="sql")
        st.caption(f"{res.latency_s:.1f} 秒 ・ tokens {res.usage.prompt_tokens + res.usage.completion_tokens:,}")

report = ROOT / "data" / "eval_report.json"
with st.sidebar:
    st.subheader("評価（eval set）")
    if report.exists():
        s = json.loads(report.read_text())["summary"]
        st.metric("正解率", f"{s['accuracy']:.0%}", f"{s['cases']} 問", delta_color="off")
        st.caption(f"モデル {s['model']} ・ 平均 {s['avg_latency_s']} 秒 ・ 未検証の数値を含む回答 {s['answers_with_unverified_numbers']} 件")
    else:
        st.caption("`make eval` で評価を実行")
