// Mini Nowcast - 6-slide technical deck (Japanese), written to be read without a presenter.
// Every slide follows: 課題 -> 選択肢 -> 判断 -> 根拠（数字 or コード）.
//
//   npm install pptxgenjs                   (not a project dependency)
//   node scripts/build_engineer_deck.js     -> docs/mini-nowcast-engineering.pptx
const pptxgen = require("pptxgenjs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const OUT = process.argv[2] || path.join(ROOT, "docs", "mini-nowcast-engineering.pptx");
const ASSETS = path.join(ROOT, "docs", "deck-assets");

const NAVY = "1E2761";
const NAVY_SOFT = "2E3C7A";
const ICE = "CADCFC";
const ICE_DEEP = "8FB3E8";
const WHITE = "FFFFFF";
const INK = "16203F";
const INK_MUTED = "5B6485";
const ACCENT = "EB6834";
const CARD = "F4F7FD";
const CODE_BG = "EEF2FB";

const HEAD = "Yu Gothic";
const BODY = "Yu Gothic";
const MONO = "Courier New";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Mini Nowcast";
pres.title = "Mini Nowcast - 技術資料";

/* ------------------------------------------------------------------ helpers */
const slideTitle = (slide, kicker, title) => {
  slide.addText(kicker, {
    x: 0.6, y: 0.42, w: 8, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, bold: true, color: ACCENT, charSpacing: 1,
  });
  slide.addText(title, {
    x: 0.6, y: 0.72, w: 12.1, h: 0.55, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 28, bold: true, color: INK,
  });
};

// A labelled content block: small bold label, then body text.
const block = (slide, { x, y, w, h, label, labelColor = INK_MUTED, body, bodySize = 12.5, fill }) => {
  if (fill) {
    slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill } });
  }
  const px = fill ? x + 0.24 : x;
  const pw = fill ? w - 0.48 : w;
  if (label) {
    slide.addText(label, {
      x: px, y: y + (fill ? 0.18 : 0), w: pw, h: 0.26, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 11.5, bold: true, color: labelColor,
    });
  }
  slide.addText(body, {
    x: px, y: y + (fill ? 0.52 : 0.32), w: pw, h: h - (fill ? 0.7 : 0.32), isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: bodySize, color: INK, lineSpacing: bodySize * 1.6,
  });
};

const codeBox = (slide, { x, y, w, h, lines, size = 10 }) => {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.06, fill: { color: CODE_BG } });
  slide.addText(lines, {
    x: x + 0.18, y: y + 0.14, w: w - 0.36, h: h - 0.28, isTextBox: true, margin: 0,
    fontFace: MONO, fontSize: size, color: NAVY, lineSpacing: size * 1.75,
  });
};

// Flow diagram: a row of boxes joined by chevrons.
const flow = (slide, { x, y, w, h, steps, boxFill = CARD, textColor = INK }) => {
  const gap = 0.3;
  const bw = (w - gap * (steps.length - 1)) / steps.length;
  steps.forEach((s, i) => {
    const bx = x + i * (bw + gap);
    slide.addShape(pres.ShapeType.roundRect, {
      x: bx, y, w: bw, h, rectRadius: 0.08,
      fill: { color: s.fill || boxFill },
    });
    slide.addText(s.title, {
      x: bx + 0.12, y: y + 0.16, w: bw - 0.24, h: 0.3, isTextBox: true, margin: 0,
      align: "center", fontFace: BODY, fontSize: 12, bold: true, color: s.color || textColor,
    });
    slide.addText(s.sub, {
      x: bx + 0.1, y: y + 0.5, w: bw - 0.2, h: h - 0.62, isTextBox: true, margin: 0,
      align: "center", fontFace: BODY, fontSize: 10, color: s.subColor || INK_MUTED, lineSpacing: 14,
    });
    if (i < steps.length - 1) {
      slide.addShape(pres.ShapeType.rightArrow, {
        x: bx + bw + 0.045, y: y + h / 2 - 0.1, w: 0.21, h: 0.2, fill: { color: ICE_DEEP },
      });
    }
  });
};

/* ------------------------------------------------------------- 1. 全体像 */
const s1 = pres.addSlide();
s1.background = { color: NAVY };

s1.addText("Mini Nowcast ｜ 技術資料", {
  x: 0.6, y: 0.42, w: 8, h: 0.28, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 12, bold: true, color: ICE_DEEP, charSpacing: 1,
});
s1.addText("全体像と技術選定", {
  x: 0.6, y: 0.72, w: 12.1, h: 0.55, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 28, bold: true, color: WHITE,
});
s1.addText("購買データ（UCI Online Retail II, 英国小売 2年分）から物価指数をつくり、そのデータに自然言語で質問できるようにした小さなデータ基盤です。", {
  x: 0.6, y: 1.35, w: 12.1, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 12.5, color: ICE,
});

flow(s1, {
  x: 0.6, y: 1.95, w: 12.1, h: 1.35,
  steps: [
    { title: "xlsx", sub: "1,067,371 行\n公開データ", fill: NAVY_SOFT, color: WHITE, subColor: ICE },
    { title: "ingest（Python）", sub: "Parquet 化 → DuckDB\n取込行数をログに記録", fill: NAVY_SOFT, color: WHITE, subColor: ICE },
    { title: "dbt", sub: "staging → intermediate → marts\n16 モデル / 28 テスト", fill: ICE, color: NAVY, subColor: NAVY },
    { title: "DuckDB", sub: "raw / ref / intermediate / marts\n166 MB・単一ファイル", fill: NAVY_SOFT, color: WHITE, subColor: ICE },
    { title: "Streamlit / AI", sub: "ダッシュボード\n自然言語アシスタント", fill: NAVY_SOFT, color: WHITE, subColor: ICE },
  ],
});

const choices = [
  {
    t: "DuckDB",
    b: "ゼロ依存・単一ファイルで、clone 後すぐ再現できる。列指向で 104 万行の集計が 11 ms、全量再構築は 18.5 秒。" +
       "アシスタントには read_only かつ外部ファイルアクセス無効の接続を渡し、エンジン側の安全境界として使う。",
  },
  {
    t: "dbt",
    b: "ref() で依存 DAG を自動決定。Törnqvist の計算式は macro 1 本にまとめ、日次・月次・カテゴリ別・月接続の 4 モデルで再利用。" +
       "profiles の target を切り替えれば同じモデルを Snowflake でも実行できる構成（本番未検証）。",
  },
  {
    t: "LLM は OpenAI 互換 API",
    b: "function calling を使わない設計にしたため、provider を選ばない。DeepSeek / OpenAI / ローカル Ollama などを環境変数 3 つで差し替え可能。",
  },
];
choices.forEach((c, i) => {
  const x = 0.6 + i * 4.09;
  s1.addShape(pres.ShapeType.roundRect, {
    x, y: 3.65, w: 3.92, h: 2.5, rectRadius: 0.08, fill: { color: NAVY_SOFT },
  });
  s1.addText(c.t, {
    x: x + 0.24, y: 3.85, w: 3.44, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14, bold: true, color: WHITE,
  });
  s1.addText(c.b, {
    x: x + 0.24, y: 4.22, w: 3.44, h: 1.8, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, color: ICE, lineSpacing: 16,
  });
});

s1.addText("Python 3.12 / uv ・ DuckDB 1.5 ・ dbt 1.12（dbt-duckdb）・ Streamlit ・ sqlglot ・ pytest 26 件", {
  x: 0.6, y: 6.45, w: 12.1, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 10.5, color: ICE_DEEP,
});

/* --------------------------------------------- 2. 決定①：比較の単位 */
const s2 = pres.addSlide();
s2.background = { color: WHITE };
slideTitle(s2, "決定 ①", "何と何を比べるか：価格チャネルの分離");

block(s2, {
  x: 0.6, y: 1.5, w: 6.1, h: 1.35, label: "課題",
  body: "同じ商品でも、顧客 ID のない取引は登録顧客より単価が高い。商品単位で平均すると、" +
        "チャネル構成が月ごとに変わるだけで「値上がり」に見えてしまう。",
});

s2.addText("商品 85123A の例", {
  x: 7.1, y: 1.5, w: 5.6, h: 0.26, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11.5, bold: true, color: INK_MUTED,
});
const rows85 = [
  ["チャネル", "平均単価", "中央値数量"],
  ["顧客 ID なし（未登録）", "£5.42", "2 個"],
  ["登録顧客（卸売）", "£2.87", "6 個"],
];
s2.addTable(rows85, {
  x: 7.1, y: 1.84, w: 5.6, colW: [2.6, 1.5, 1.5],
  border: { type: "solid", color: "DCE3F5", pt: 1 },
  fill: { color: WHITE },
  fontFace: BODY, fontSize: 11, color: INK, valign: "middle",
  rowH: 0.34, margin: 0.08,
});
s2.addText("商品×月の 63% が複数の単価を持つ（平均 1.97 通り）", {
  x: 7.1, y: 3.15, w: 5.6, h: 0.26, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11, color: INK_MUTED,
});

block(s2, {
  x: 0.6, y: 3.0, w: 6.1, h: 1.5, label: "判断",
  body: "指数の比較単位を「商品」ではなく「商品 × 価格チャネル」にした。" +
        "同じ商品でもチャネルが違えば別アイテムとして扱い、常に同じアイテム同士の価格を前期と比べる。",
});

codeBox(s2, {
  x: 0.6, y: 4.62, w: 6.1, h: 1.25,
  lines:
    "case when customer_id is null\n" +
    "     then 'unregistered' else 'registered'\n" +
    "end as price_channel\n" +
    "-- item_id = stock_code || '|' || price_channel",
});

s2.addShape(pres.ShapeType.roundRect, {
  x: 7.1, y: 3.62, w: 5.6, h: 2.25, rectRadius: 0.08, fill: { color: CARD },
});
s2.addText("根拠：2011年11月の前月比", {
  x: 7.34, y: 3.8, w: 5.12, h: 0.28, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11.5, bold: true, color: ACCENT,
});
s2.addText(
  [
    { text: "商品単位（チャネル混在）", options: { color: INK_MUTED, breakLine: true } },
    { text: "+7.5%", options: { fontSize: 24, bold: true, color: INK_MUTED, breakLine: true } },
    { text: "商品 × チャネル単位", options: { color: INK, breakLine: true } },
    { text: "+2.0%", options: { fontSize: 24, bold: true, color: NAVY } },
  ],
  {
    x: 7.34, y: 4.18, w: 5.12, h: 1.62, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11.5, lineSpacing: 26,
  }
);

s2.addText("この分離をしないまま「2年で +4.7%」と報告していたら、季節的なチャネル構成の変化を物価変動として説明してしまっていた。", {
  x: 0.6, y: 6.1, w: 12.1, h: 0.4, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11.5, color: INK_MUTED,
});

/* ------------------------------------------- 3. 決定②：chain drift */
const s3 = pres.addSlide();
s3.background = { color: WHITE };
slideTitle(s3, "決定 ②", "日次指数から「連鎖」を外した理由");

block(s3, {
  x: 0.6, y: 1.5, w: 5.6, h: 1.3, label: "課題",
  body: "日々の価格変化を連鎖（前日比の積み上げ）で指数にすると、2 年で 218 まで上昇した。" +
        "同じデータの月次指数は 104.7。日次の単価ノイズが累積する chain drift。",
});

s3.addText("選択肢と判断", {
  x: 0.6, y: 2.95, w: 5.6, h: 0.26, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11.5, bold: true, color: INK_MUTED,
});
const options = [
  ["a", "日次で連鎖する", "却下：ドリフトが累積", INK_MUTED],
  ["b", "月次だけを出す", "却下：日次の粒度を失う", INK_MUTED],
  ["c", "前月の平均価格と比較し\n月次指数に接続する", "採用：日次を保ちつつ\n誤差を累積させない", NAVY],
];
options.forEach((o, i) => {
  const y = 3.28 + i * 0.78;
  const chosen = o[0] === "c";
  s3.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y, w: 5.6, h: 0.68, rectRadius: 0.06,
    fill: { color: chosen ? CARD : "FAFBFE" },
  });
  s3.addText(o[0], {
    x: 0.78, y, w: 0.3, h: 0.68, isTextBox: true, margin: 0, valign: "middle",
    fontFace: BODY, fontSize: 12, bold: true, color: chosen ? ACCENT : INK_MUTED,
  });
  s3.addText(o[1], {
    x: 1.15, y, w: 2.3, h: 0.68, isTextBox: true, margin: 0, valign: "middle",
    fontFace: BODY, fontSize: 11, bold: chosen, color: o[3], lineSpacing: 14,
  });
  s3.addText(o[2], {
    x: 3.5, y, w: 2.55, h: 0.68, isTextBox: true, margin: 0, valign: "middle",
    fontFace: BODY, fontSize: 10.5, color: o[3], lineSpacing: 14,
  });
});

block(s3, {
  x: 0.6, y: 5.8, w: 5.6, h: 1.0, label: "採用した方式（c）の中身", bodySize: 11,
  body: "日 t の各アイテム価格を「前月の平均価格」と比べて Törnqvist を取り、前月の月次指数の水準に乗せる。連鎖は月次のみ。",
});

s3.addText("根拠：同じデータ・3 つの計算方法", {
  x: 6.6, y: 1.5, w: 6.1, h: 0.26, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11.5, bold: true, color: INK_MUTED,
});
s3.addImage({ path: path.join(ASSETS, "index_methods.png"), x: 6.6, y: 1.84, w: 6.1, h: 2.79 });
s3.addText("青＝月接続（採用, 103）　橙＝日次連鎖（218）　緑＝単純平均単価", {
  x: 6.6, y: 4.68, w: 6.1, h: 0.26, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 10.5, color: INK_MUTED,
});

block(s3, {
  x: 6.6, y: 5.05, w: 6.1, h: 1.4, label: "あわせて入れた防御", fill: CARD,
  bodySize: 11,
  body: "前期比が ln(3) を超える価格比はデータ誤りとして除外し、除外件数を指数と一緒に出力する（marts に outliers_trimmed 列）。" +
        "黙って捨てず、件数が見える形にしている。",
});

/* ------------------------------------------------- 4. 決定③：テスト */
const s4 = pres.addSlide();
s4.background = { color: WHITE };
slideTitle(s4, "決定 ③", "データ品質をテストで担保する");

const tests = [
  {
    t: "一般テスト",
    n: "not_null / unique / accepted_values / 範囲・複合キー（自作）",
    b: "dbt_utils は入れず、between と unique_combination を自作。外部パッケージの取得に依存せず動く。",
  },
  {
    t: "恒等式テスト",
    n: "数学的に必ず成り立つ関係を検証",
    b: "① 各商品の寄与度の合計 = その月の指数の log 変化　② 取込行数 = 採用 + 除外。式を書き間違えれば即座に落ちる。",
  },
  {
    t: "意味層 ↔ DB 整合テスト",
    n: "ドキュメントとスキーマの乖離を検出",
    b: "実際に列名の大文字小文字の不一致（Country / country）を検出。AI アシスタントが参照する定義が実体とずれない。",
  },
];
tests.forEach((t, i) => {
  const x = 0.6 + i * 4.09;
  s4.addShape(pres.ShapeType.roundRect, { x, y: 1.5, w: 3.92, h: 2.35, rectRadius: 0.08, fill: { color: CARD } });
  s4.addText(t.t, {
    x: x + 0.24, y: 1.68, w: 3.44, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14, bold: true, color: NAVY,
  });
  s4.addText(t.n, {
    x: x + 0.24, y: 2.02, w: 3.44, h: 0.32, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, bold: true, color: ACCENT, lineSpacing: 14,
  });
  s4.addText(t.b, {
    x: x + 0.24, y: 2.42, w: 3.44, h: 1.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, color: INK, lineSpacing: 16,
  });
});

block(s4, {
  x: 0.6, y: 4.1, w: 6.1, h: 1.9, label: "アラート基準を作り直した", labelColor: ACCENT, fill: CARD, bodySize: 11.5,
  body: "当初は「直近 7 営業日平均の 50% 未満」で行数急減を検知 → 営業時間の短い日曜がほぼ毎週アラートに。" +
        "基準を「同じ曜日の過去 4 週平均」に変更し、24 日 → 19 日（うち 14 日が年末年始）。" +
        "誤報が続く監視は、本番で誰にも見られなくなる。",
});

block(s4, {
  x: 7.1, y: 4.1, w: 5.6, h: 1.9, label: "計算式は macro 1 本に集約", fill: CARD, bodySize: 11.5,
  body: "Törnqvist の式は macro 1 つ。引数（group_col / chain）で、全体・カテゴリ別・日次連鎖・月接続の 4 モデルに展開している。" +
        "式を直す場所が 1 箇所なので、直し漏れが起きない。",
});

s4.addText("除外した行は削除せず exclusion_reason を付けて保持。クリーニングの内訳をダッシュボードから追える。", {
  x: 0.6, y: 6.15, w: 12.1, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11, color: INK_MUTED,
});

/* ------------------------------------------ 5. 決定④：LLM の扱い */
const s5 = pres.addSlide();
s5.background = { color: WHITE };
slideTitle(s5, "決定 ④", "LLM の出力を「信用しない入力」として扱う");

flow(s5, {
  x: 0.6, y: 1.5, w: 12.1, h: 1.2,
  steps: [
    { title: "意味層", sub: "7 テーブルの定義\n集計不可の列も明記" },
    { title: "SQL 生成", sub: "JSON で受け取る\nLLM は実行しない" },
    { title: "構文木で検査", sub: "sqlglot\nホワイトリスト" },
    { title: "read_only 実行", sub: "外部アクセス無効\nエンジン側の防御" },
    { title: "回答生成", sub: "結果の行だけを\n根拠にさせる" },
    { title: "数値照合", sub: "引用値を結果と突合\n不一致は ⚠ 表示", fill: ICE, color: NAVY, subColor: NAVY },
  ],
});

block(s5, {
  x: 0.6, y: 2.95, w: 6.1, h: 2.0, label: "ガードの 4 規則（13 の攻撃ケースでテスト）", fill: CARD, bodySize: 11,
  body: "① 1 文のみ　② 読み取り専用クエリのみ（DDL/DML・COPY・ATTACH・PRAGMA を拒否）\n" +
        "③ 許可テーブルのみ（CTE 別名での偽装も検出）　④ テーブル関数を禁止\n" +
        "read_csv('/etc/passwd') は構文的には正当な SELECT なので、正規表現ではなく構文木で判定している。",
});

block(s5, {
  x: 7.1, y: 2.95, w: 5.6, h: 2.0, label: "自己修正（上限 3 回）", fill: CARD, bodySize: 11,
  body: "検査や実行でエラーになったら、エラー文をそのまま LLM に返して書き直させる。" +
        "ループを許すのはここだけで、回数は固定。無制限の自律ループにはしていない。",
});

block(s5, {
  x: 0.6, y: 5.15, w: 12.1, h: 1.2, label: "function calling を使わなかった理由", labelColor: ACCENT, bodySize: 11.5,
  body: "ツールが「SQL を 1 本投げる」だけなら、function calling はプロトコルの追加コストにしかならない。" +
        "また tools を使わないことで、JSON さえ返せればどの provider でも動く。欲しかったのは「モデルが提案し、コードが承認する」形であって、「モデルが呼び、フレームワークが実行する」形ではない。" +
        "テーブルが数百に増えてスキーマ探索が要るようになれば、search_tables / describe_table / run_query を tool として足す。",
});

/* -------------------------------------- 6. 評価・テスト・限界 */
const s6 = pres.addSlide();
s6.background = { color: WHITE };
slideTitle(s6, "評価と限界", "測れるようにした部分と、まだ出来ていない部分");

const metrics = [
  { v: "20 / 20", l: "eval set 正解率\n日本語・中文・英語、うち 2 問は\n「答えられない」が正解" },
  { v: "1.6 秒", l: "1 問あたりの平均応答\n2 回の LLM 呼び出し・約 2,000 tokens" },
  { v: "26 件", l: "pytest（ネットワーク不要）\nLLM を注入で差し替え、拒否→再生成の\n全経路をテスト" },
];
metrics.forEach((m, i) => {
  const x = 0.6 + i * 4.09;
  s6.addShape(pres.ShapeType.roundRect, { x, y: 1.5, w: 3.92, h: 1.7, rectRadius: 0.08, fill: { color: NAVY } });
  s6.addText(m.v, {
    x: x + 0.24, y: 1.66, w: 3.44, h: 0.5, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 26, bold: true, color: WHITE,
  });
  s6.addText(m.l, {
    x: x + 0.24, y: 2.18, w: 3.44, h: 0.95, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10, color: ICE, lineSpacing: 14,
  });
});

block(s6, {
  x: 0.6, y: 3.4, w: 6.1, h: 1.45, label: "評価スクリプト自体のバグを 1 件見つけた", labelColor: ACCENT, fill: CARD, bodySize: 11,
  body: "モデルは 5.06（%）、正解 SQL は 0.0506（比率）を返し、両方正しいのに不正解と判定していた。" +
        "採点側の単位の扱いが原因。評価結果も検証の対象にしている。",
});

block(s6, {
  x: 0.6, y: 5.0, w: 6.1, h: 1.35, label: "観測できるようにしたもの", fill: CARD, bodySize: 11,
  body: "質問・生成 SQL・再試行回数・未検証の数値・tokens・レイテンシを JSONL に記録。" +
        "本番で監視したい項目をそのまま出している。",
});

s6.addText("まだ出来ていないこと（次の一手）", {
  x: 7.1, y: 3.4, w: 5.6, h: 0.28, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11.5, bold: true, color: INK_MUTED,
});
s6.addText(
  [
    { text: "Snowflake は target を用意しただけで未実行。まず接続して同じモデルを流す。", options: { bullet: true, breakLine: true } },
    { text: "同一チャネル内の数量割引バイアスが未処理。数量帯で分けるか中央値を使う。", options: { bullet: true, breakLine: true } },
    { text: "カテゴリはキーワード分類で約 4 割が「その他」。LLM 分類＋人の確認に置き換えたい。", options: { bullet: true, breakLine: true } },
    { text: "eval が 20/20 = まだ易しい。曖昧な質問や、集計できない列を足す罠を追加する。", options: { bullet: true, breakLine: true } },
    { text: "月次連鎖のドリフトは未検証。GEKS-Törnqvist と突き合わせたい。", options: { bullet: true } },
  ],
  {
    x: 7.2, y: 3.75, w: 5.5, h: 2.6, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: INK, lineSpacing: 17, paraSpaceAfter: 7,
  }
);

s6.addText("github.com/Calista0429/mini-nowcast", {
  x: 0.6, y: 6.6, w: 12.1, h: 0.28, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 10.5, color: INK_MUTED,
});

pres.writeFile({ fileName: OUT }).then(() => console.log("written:", OUT));
