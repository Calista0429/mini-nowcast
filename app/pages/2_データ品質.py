import json

import plotly.graph_objects as go
import streamlit as st

from common import CRITICAL, INK_2, ROOT, SERIES, q, style

st.set_page_config(page_title="データ品質", page_icon="🧹", layout="wide")
st.title("データ品質")

# --- dbt test status ----------------------------------------------------------------------
run_results = ROOT / "dbt" / "target" / "run_results.json"
if run_results.exists():
    results = json.loads(run_results.read_text())["results"]
    tests = [r for r in results if r["unique_id"].startswith("test.")]
    failed = [r for r in tests if r["status"] != "pass"]
    label = "✅ 全テスト合格" if not failed else f"❌ {len(failed)} 件失敗"
    st.metric("dbt テスト（最新ビルド）", f"{len(tests) - len(failed)} / {len(tests)}", label, delta_color="off")
    if failed:
        st.error("\n".join(r["unique_id"] for r in failed))

# --- cleaning summary ---------------------------------------------------------------------
st.subheader("クリーニングで除外した行")
REASON_JA = {
    "cancellation": "キャンセル伝票", "non_positive_quantity": "数量 ≤ 0（破損・棚卸調整）",
    "non_positive_price": "単価 ≤ 0", "missing_description": "商品名なし",
    "non_product:postage": "送料", "non_product:manual_adjustment": "手動調整",
    "non_product:marketplace_listing": "マーケットプレイス出品", "non_product:gift_voucher": "ギフト券",
    "non_product:fee": "手数料", "non_product:test_product": "テスト商品",
    "non_product:discount": "値引き", "non_product:samples": "サンプル",
    "non_product:bad_debt_adjustment": "貸倒調整",
}
cs = q("select * from marts.mart_cleaning_summary where outcome <> 'kept' order by line_count")
cs["理由"] = cs.outcome.map(REASON_JA).fillna(cs.outcome)
fig = go.Figure(go.Bar(
    x=cs.line_count, y=cs["理由"], orientation="h", marker_color=SERIES[0],
    text=cs.line_count.map("{:,}".format), textposition="outside", textfont_color=INK_2,
    customdata=cs.line_amount_gbp, hovertemplate="%{x:,} 行<br>金額 £%{customdata:,.0f}<extra></extra>",
))
fig.update_layout(hovermode="closest")
fig = style(fig, 420)
fig.update_xaxes(range=[0, cs.line_count.max() * 1.12])  # room for the outside labels
st.plotly_chart(fig, use_container_width=True)
st.caption("除外した行は削除せず理由付きで保持（int_sales_lines_flagged）。取込行数 = 採用 + 除外 を dbt テストで照合。"
           "別途、2つのシートが重複していた 2010-12-01〜09 の 22,523 行は staging で除去。")

# --- daily volume monitor -----------------------------------------------------------------
st.subheader("日次データ量モニタリング")
dq = q("select * from marts.mart_data_quality_daily order by sale_date")
alerts = dq[dq.is_volume_drop]
fig = go.Figure()
fig.add_scatter(x=dq.sale_date, y=dq.clean_lines, name="クリーニング後の行数", line_color=SERIES[0],
                hovertemplate="%{y:,} 行")
fig.add_scatter(x=dq.sale_date, y=dq.baseline_lines * 0.5, name="アラート閾値（過去4週の同じ曜日の平均 × 50%）",
                line=dict(color=INK_2, width=1, dash="dot"), hovertemplate="%{y:,.0f}")
fig.add_scatter(x=alerts.sale_date, y=alerts.clean_lines, mode="markers", name="⚠ 急減アラート",
                marker=dict(color=CRITICAL, size=13, symbol="triangle-down", line=dict(color="white", width=2)),
                hovertemplate="⚠ %{y:,} 行")
st.plotly_chart(style(fig, 380, "行数"), use_container_width=True)
year_end = alerts.sale_date.apply(lambda d: (d.month == 12 and d.day >= 15) or (d.month == 1 and d.day <= 15)).sum()
st.markdown(
    f"**⚠ アラート {len(alerts)} 日**（うち年末年始 12/15〜1/15 が {year_end} 日）。"
    "当初は「直近7営業日平均」を基準にしていたが、営業時間の短い日曜日がほぼ毎週アラートになったため、"
    "「同じ曜日の過去4週平均」に変更。本番運用では Slack 通知やパイプライン停止のトリガーになる。"
)
with st.expander("アラート日の一覧"):
    st.dataframe(alerts[["sale_date", "clean_lines", "baseline_lines", "excluded_share"]]
                 .rename(columns={"sale_date": "日付", "clean_lines": "行数", "baseline_lines": "同曜日4週平均",
                                  "excluded_share": "除外率"}),
                 hide_index=True, use_container_width=True)
