import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from common import CATEGORY_JA, INK_2, MUTED, SERIES, q, style

st.set_page_config(page_title="物価指数", page_icon="📈", layout="wide")
st.title("物価指数")

monthly = q("select period, price_index, log_change, matched_products from marts.mart_price_index_monthly order by period")
first, last = monthly.iloc[0], monthly.iloc[-1]
c1, c2, c3 = st.columns(3)
c1.metric("最新（2011-11）", f"{last.price_index:.1f}", f"前月比 {last.log_change:+.2%}", delta_color="off")
c2.metric("2年間の上昇率", f"{last.price_index / 100 - 1:+.1%}", help="2009-12 = 100")
c3.metric("比較に使った商品×チャネル数（最新月）", f"{last.matched_products:,}")

# --- the methodology chart: three ways to measure daily prices --------------------------
st.subheader("日次物価：3つの計算方法")
st.caption("同じデータでも計算方法で結論が変わる。ヘッドラインは「前月価格と比較して月次指数に接続」する方式。")
daily = q("select sale_date, price_index, chained_daily_index, naive_index from marts.mart_price_index_daily order by sale_date")
fig = go.Figure()
# (column, legend name, colour, direct label?) - drawn back to front so the headline sits on top
series = [
    ("naive_index", "単純平均単価（構成変化に左右される）", SERIES[2], False),
    ("chained_daily_index", "日次連鎖 Törnqvist（chain drift）", SERIES[1], True),
    ("price_index", "ヘッドライン（月次接続 Törnqvist）", SERIES[0], True),
]
for col, name, color, label in series:
    fig.add_scatter(x=daily.sale_date, y=daily[col], name=name, line_color=color,
                    hovertemplate="%{y:.1f}")
    if label:
        last_row = daily.dropna(subset=[col]).iloc[-1]
        fig.add_annotation(x=last_row.sale_date, y=last_row[col], text=f"{last_row[col]:.0f}",
                           showarrow=False, xanchor="left", xshift=6, font_color=INK_2)
fig.update_layout(legend_traceorder="reversed")
fig.add_hline(y=100, line_color=MUTED, line_width=1, line_dash="dot")
st.plotly_chart(style(fig, 420, "指数（2009-12 = 100）"), use_container_width=True)

# --- category small multiples -------------------------------------------------------------
st.subheader("カテゴリ別 物価指数（月次）")
cat = q("select category, period, price_index from marts.mart_category_price_index_monthly order by period")
cat["カテゴリ"] = cat["category"].map(CATEGORY_JA)
order = (cat[cat.period == cat.period.max()].sort_values("price_index", ascending=False)["カテゴリ"].tolist())
fig = px.line(cat, x="period", y="price_index", facet_col="カテゴリ", facet_col_wrap=5,
              category_orders={"カテゴリ": order}, color_discrete_sequence=[SERIES[0]])
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font_color=INK_2))
fig.update_traces(hovertemplate="%{x|%Y-%m}: %{y:.1f}")
fig.add_hline(y=100, line_color=MUTED, line_width=1, line_dash="dot")
st.plotly_chart(style(fig, 440), use_container_width=True)
st.caption("点線 = 基準（2009-12 = 100）。カテゴリは商品名のキーワードで分類（「その他」はキーワード未一致）。")

# --- contributions ------------------------------------------------------------------------
st.subheader("寄与度：どの商品が物価を動かしたか")
months = monthly.period.dt.strftime("%Y-%m").tolist()
month = st.select_slider("月", options=months, value=months[-1])
contrib = q(f"""
    select description, price_channel, category, price_prev, price_t, price_change_pct, contribution
    from marts.mart_price_contributions_monthly
    where month = date '{month}-01'
""")
row = monthly[monthly.period.dt.strftime("%Y-%m") == month].iloc[0]
st.markdown(f"**{month}** の前月比 **{row.log_change:+.2%}**（対数変化）。各商品の寄与度を合計すると一致します（dbt テストで検証）。")
top = contrib.reindex(contrib.contribution.abs().sort_values(ascending=False).index).head(15)
top = top.assign(
    寄与度_bp=(top.contribution * 1e4).round(2),
    価格変化=top.price_change_pct.map("{:+.1%}".format),
    前月価格=top.price_prev.map("£{:.2f}".format),
    当月価格=top.price_t.map("£{:.2f}".format),
    カテゴリ=top.category.map(CATEGORY_JA),
    チャネル=top.price_channel.map({"registered": "登録顧客", "unregistered": "未登録"}),
)[["description", "カテゴリ", "チャネル", "前月価格", "当月価格", "価格変化", "寄与度_bp"]]
st.dataframe(top.rename(columns={"description": "商品", "寄与度_bp": "寄与度（bp）"}),
             hide_index=True, use_container_width=True)
