// Mini Nowcast - 3-slide intro deck (Japanese, for a casual HR meeting).
// Spoken-presentation version: few words per slide, one claim each; speaker notes carry the talk.
//
//   npm install pptxgenjs        (not a project dependency - only needed to rebuild the deck)
//   node scripts/build_deck.js   -> docs/mini-nowcast-intro.pptx
const pptxgen = require("pptxgenjs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const OUT = process.argv[2] || path.join(ROOT, "docs", "mini-nowcast-intro.pptx");
const ASSETS = path.join(ROOT, "docs", "deck-assets"); // crops of docs/screenshots, see crop_deck_assets.py

// Midnight Executive palette + the dashboard's own orange as the single accent.
const NAVY = "1E2761";
const NAVY_SOFT = "2E3C7A";
const ICE = "CADCFC";
const ICE_DEEP = "8FB3E8";
const WHITE = "FFFFFF";
const INK = "16203F";
const INK_MUTED = "5B6485";
const ACCENT = "EB6834";
const CARD = "F4F7FD";

const HEAD = "Yu Gothic"; // ships with Office on Windows and Mac
const BODY = "Yu Gothic";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5 in
pres.author = "Mini Nowcast";
pres.title = "Mini Nowcast";

const numberCircle = (slide, n, x, y, color = NAVY) => {
  slide.addShape(pres.ShapeType.ellipse, {
    x, y, w: 0.34, h: 0.34, fill: { color },
  });
  slide.addText(String(n), {
    x, y, w: 0.34, h: 0.34, isTextBox: true, margin: 0,
    align: "center", valign: "middle", fontFace: BODY, fontSize: 14, bold: true, color: WHITE,
  });
};

/* ---------------------------------------------------------------- Slide 1 */
const s1 = pres.addSlide();
s1.background = { color: NAVY };

s1.addText("つくったもの", {
  x: 0.7, y: 0.5, w: 5.0, h: 0.35, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 16, color: ICE_DEEP, charSpacing: 2,
});

s1.addText(
  [
    { text: "購買データ", options: { color: WHITE, bold: true } },
    { text: "から物価の動きを毎日測り、", options: { color: ICE, breakLine: true } },
    { text: "そのデータに", options: { color: ICE } },
    { text: "日本語で質問できる", options: { color: WHITE, bold: true } },
    { text: "しくみ", options: { color: ICE } },
  ],
  {
    x: 0.7, y: 1.0, w: 12.0, h: 1.45, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 30, lineSpacing: 44,
  }
);

// Three stat callouts
const stats = [
  { v: "104万件", l: "2年分の購買データを処理" },
  { v: "+4.7%", l: "2年間の物価上昇を算出" },
  { v: "20/20", l: "AIへの質問に正しく回答" },
];
stats.forEach((s, i) => {
  const x = 0.7 + i * 4.05;
  s1.addShape(pres.ShapeType.roundRect, {
    x, y: 2.75, w: 3.7, h: 1.45, rectRadius: 0.12,
    fill: { color: NAVY_SOFT },
  });
  s1.addText(s.v, {
    x: x + 0.3, y: 2.92, w: 3.1, h: 0.68, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 36, bold: true, color: WHITE,
  });
  s1.addText(s.l, {
    x: x + 0.3, y: 3.6, w: 3.15, h: 0.45, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, color: ICE_DEEP,
  });
});

// Dashboard banner
s1.addImage({
  path: path.join(ASSETS, "home.png"),
  x: 0.7, y: 4.5, w: 11.9, h: 2.11,
});

s1.addText("Python / SQL / DuckDB / dbt / Streamlit / 生成AI（LLM）", {
  x: 0.7, y: 6.75, w: 11.9, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11, color: ICE_DEEP,
});

s1.addNotes(
  "スーパーのレシートのような購買データを使って、物価が毎日どう動いているかを測るしくみを作りました。" +
  "さらに、そのデータに日本語で質問すると答えが返ってくるAIアシスタントもつけています。" +
  "画面は実際に動いているものです。データは英国の小売2年分、約104万件の公開データを使いました。"
);

/* ---------------------------------------------------------------- Slide 2 */
const s2 = pres.addSlide();
s2.background = { color: WHITE };

s2.addText("なぜ、これをつくったか", {
  x: 0.7, y: 0.55, w: 8.0, h: 0.6, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 36, bold: true, color: INK,
});
s2.addText("御社の2つの事業を、自分の手で小さく体験してみたいと思ったのがきっかけです。", {
  x: 0.7, y: 1.25, w: 11.9, h: 0.4, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 15, color: INK_MUTED,
});

const rows = [
  {
    n: 1,
    left: "JCB消費NOW・日経CPINow",
    leftSub: "購買データから経済指標をつくる",
    right: "公開データで同じ仕組みを小さく再現",
    rightSub: "英国の小売2年分から、日次・月次の物価指数を算出",
  },
  {
    n: 2,
    left: "データ × 生成AI のソリューション",
    leftSub: "企業のデータ活用を支援する",
    right: "データに日本語で質問できるAIを実装",
    rightSub: "質問 → 自動でデータを検索 → 根拠つきで回答",
  },
];

s2.addText("ナウキャスト様の事業", {
  x: 1.35, y: 1.95, w: 4.6, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, bold: true, color: INK_MUTED,
});
s2.addText("今回つくったもの", {
  x: 7.3, y: 1.95, w: 5.3, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, bold: true, color: ACCENT,
});

rows.forEach((r, i) => {
  const y = 2.4 + i * 2.05;
  numberCircle(s2, r.n, 0.7, y + 0.42);

  s2.addShape(pres.ShapeType.roundRect, {
    x: 1.35, y, w: 4.6, h: 1.65, rectRadius: 0.1, fill: { color: CARD },
  });
  s2.addText(r.left, {
    x: 1.6, y: y + 0.25, w: 4.1, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 16, bold: true, color: NAVY,
  });
  s2.addText(r.leftSub, {
    x: 1.6, y: y + 0.72, w: 4.1, h: 0.7, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: INK_MUTED,
  });

  s2.addShape(pres.ShapeType.rightArrow, {
    x: 6.25, y: y + 0.63, w: 0.78, h: 0.4, fill: { color: ICE },
  });

  s2.addShape(pres.ShapeType.roundRect, {
    x: 7.3, y, w: 5.3, h: 1.65, rectRadius: 0.1, fill: { color: NAVY },
  });
  s2.addText(r.right, {
    x: 7.55, y: y + 0.25, w: 4.8, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 16, bold: true, color: WHITE,
  });
  s2.addText(r.rightSub, {
    x: 7.55, y: y + 0.72, w: 4.8, h: 0.7, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: ICE,
  });
});

s2.addText("※ 御社の事業内容は、採用ページと各サービスのサイトを読んで整理しました。", {
  x: 1.35, y: 6.65, w: 11.25, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11.5, color: INK_MUTED,
});

s2.addNotes(
  "応募の前に御社の事業を調べました。ナウキャストさんは、JCBのカードデータや日経のPOSデータから" +
  "消費や物価の指標をつくる事業と、企業のデータ活用を生成AIで支援する事業の2つをされています。" +
  "その2つを、公開データを使って自分で小さく作ってみたのが今回のものです。"
);

/* ---------------------------------------------------------------- Slide 3 */
const s3 = pres.addSlide();
s3.background = { color: WHITE };

s3.addText("つくりながら学んだこと", {
  x: 0.7, y: 0.55, w: 8.5, h: 0.6, isTextBox: true, margin: 0,
  fontFace: HEAD, fontSize: 36, bold: true, color: INK,
});

s3.addText("今回はじめて使った技術", {
  x: 0.7, y: 1.35, w: 5.6, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, bold: true, color: INK_MUTED,
});
s3.addText(
  [
    { text: "dbt（データ加工を自動化する仕組み）", options: { bullet: true, breakLine: true } },
    { text: "クラウド前提のデータ基盤の作り方", options: { bullet: true, breakLine: true } },
    { text: "生成AIをサービスに組み込む方法", options: { bullet: true } },
  ],
  {
    x: 0.8, y: 1.72, w: 5.5, h: 1.2, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14, color: INK, paraSpaceAfter: 6,
  }
);

s3.addShape(pres.ShapeType.roundRect, {
  x: 0.7, y: 3.05, w: 5.75, h: 3.15, rectRadius: 0.1, fill: { color: CARD },
});
s3.addText("一番苦労したこと", {
  x: 0.98, y: 3.25, w: 5.2, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, bold: true, color: ACCENT,
});
s3.addText(
  [
    { text: "AIが出した数字が正しいか分からない。\n", options: { color: INK, bold: true } },
    {
      text: "→ 回答に出てくる数字を、元データと自動で突き合わせて確認する仕組みをつくりました。" +
            "AIは間違えることがあるので、人が最後に確認できる形にしています。",
      options: { color: INK_MUTED },
    },
  ],
  {
    x: 0.98, y: 3.58, w: 5.2, h: 2.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, lineSpacing: 21,
  }
);

s3.addText("確認できた数字には ✅ がつきます", {
  x: 6.95, y: 1.35, w: 5.65, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, bold: true, color: INK_MUTED,
});
s3.addImage({
  path: path.join(ASSETS, "assistant.png"),
  x: 6.95, y: 1.72, w: 5.65, h: 1.20,
});

s3.addShape(pres.ShapeType.roundRect, {
  x: 6.95, y: 3.3, w: 5.65, h: 2.9, rectRadius: 0.1, fill: { color: NAVY },
});
s3.addText("インターンでやりたいこと", {
  x: 7.23, y: 3.58, w: 5.1, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 13, bold: true, color: ICE_DEEP,
});
s3.addText(
  "実データを使って、Python・SQL・生成AIで手を動かしたいです。\n" +
  "地道な確認作業も含めて、最後までやり切ることを大事にしています。",
  {
    x: 7.23, y: 4.05, w: 5.1, h: 2.0, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13.5, color: WHITE, lineSpacing: 22,
  }
);

s3.addText("github.com/Calista0429/mini-nowcast", {
  x: 0.7, y: 6.55, w: 11.9, h: 0.3, isTextBox: true, margin: 0,
  fontFace: BODY, fontSize: 11, color: INK_MUTED,
});

s3.addNotes(
  "dbtやクラウド前提のデータ基盤、生成AIの組み込みは今回がはじめてで、調べながら進めました。" +
  "一番苦労したのは、AIが出してくる数字が正しいかどうか分からないことです。" +
  "そこで、回答に出てくる数字を元データと自動で突き合わせて、確認できたものには印をつけるようにしました。" +
  "インターンでは、実際のデータで手を動かしながら、こうした地道な確認も含めて最後までやり切りたいです。"
);

pres.writeFile({ fileName: OUT }).then(() => console.log("written:", OUT));
