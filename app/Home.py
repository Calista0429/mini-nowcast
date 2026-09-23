import streamlit as st

from common import q

st.set_page_config(page_title="Mini Nowcast", page_icon="📈", layout="wide")

st.title("Mini Nowcast")
st.caption("オルタナティブデータ → 物価指数 → 自然言語での分析　｜　UCI Online Retail II（英国ギフト卸, 2009-12〜2011-12）")

kpi = q("""
    select
        (select sum(line_count) from marts.mart_cleaning_summary)                       as raw_lines,
        (select line_count from marts.mart_cleaning_summary where outcome = 'kept')      as kept_lines,
        (select count(*) from marts.mart_data_quality_daily)                              as trading_days,
        (select price_index from marts.mart_price_index_monthly order by period desc limit 1) as latest_index,
        (select count(*) from marts.mart_data_quality_daily where is_volume_drop)         as alerts
""").iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("取込行数（重複除去後）", f"{kpi.raw_lines:,.0f}")
c2.metric("クリーニング後", f"{kpi.kept_lines:,.0f}", f"{kpi.kept_lines / kpi.raw_lines - 1:.1%}", delta_color="off")
c3.metric("物価指数 2011-11（2009-12=100）", f"{kpi.latest_index:.1f}")
c4.metric("⚠ データ量急減アラート", f"{int(kpi.alerts)} 日", help="クリーニング後の行数が、過去4週の同じ曜日の平均の50%未満")

st.subheader("パイプライン")
st.code(
    """xlsx (1,067,371行)
  └─ ingest/load_raw.py ──► DuckDB raw
       └─ dbt  staging       型変換・シート重複（2010-12-01〜09）除去
               intermediate  除外理由付きクリーニング → 商品×チャネル×期間の単価
               marts         Törnqvist 物価指数 / 寄与度 / 売上 / データ品質
                             + 28 件の dbt テスト
                    └─ Streamlit ダッシュボード
                    └─ AIアシスタント（意味層 → SQL生成 → 安全検査 → 実行 → 数値検証）""",
    language=None,
)

st.subheader("設計上のポイント")
st.markdown("""
- **単純平均は使わない**：平均単価は「何が売れたか」で動く。同一商品の価格を前期と比べる Törnqvist 指数を採用。
- **価格チャネルを分ける**：顧客IDなしの取引は登録顧客の約2倍の単価。混ぜると11月に見かけ上 +7.5% の物価上昇が出る → 商品×チャネル単位で比較し +2.0% に。
- **日次の連鎖はしない**：日々の連鎖はノイズが累積し2年で指数が約2倍に（chain drift）。日次値は「前月平均価格」と比較して月次指数に接続。
- **LLMの出力は信用しない**：生成SQLは構文解析で検査し読み取り専用接続で実行。回答中の数値は結果セルと突合して検証。
""")
st.info("左のメニューから「物価指数」「データ品質」「AIアシスタント」を選択してください。")
