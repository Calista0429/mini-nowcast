// Interview talk script for mini-nowcast-intro.pptx (Japanese script + Chinese stage notes).
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  BorderStyle, ShadingType, Table, TableRow, TableCell, WidthType,
} = require("docx");
const fs = require("fs");

const OUT = process.argv[2] || "docs/interview/面接トーク原稿_intro.docx";

const JP = "Yu Gothic";
const ZH = "Heiti SC";  // renders on macOS; Word on Windows falls back to a system SC font
const INK = "232A36";
const MUTED = "636C7C";
const ACCENT = "C2531F";
const TINT = "F2F4F7";

const p = (children, opts = {}) => new Paragraph({ children, spacing: { after: 120 }, ...opts });

const h1 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 200, after: 160 },
    children: [new TextRun({ text, font: JP, size: 32, bold: true, color: INK })],
  });

// Slide heading with the timing on the right of the same line.
const slideHead = (title, timing) =>
  new Paragraph({
    spacing: { before: 320, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "D7DBE2", space: 6 } },
    children: [
      new TextRun({ text: title, font: JP, size: 26, bold: true, color: INK }),
      new TextRun({ text: `　　${timing}`, font: JP, size: 19, color: MUTED }),
    ],
  });

// A line of the script. Emphasised segments are what to stress when speaking.
// (bold + accent colour rather than w:highlight, which docx-js writes in a schema-invalid way)
const line = (runs) =>
  new Paragraph({
    spacing: { after: 140, line: 340 },
    indent: { left: 280 },
    children: runs.map((r) =>
      typeof r === "string"
        ? new TextRun({ text: r, font: JP, size: 22, color: INK })
        : new TextRun({ text: r.t, font: JP, size: 22, color: ACCENT, bold: true })
    ),
  });

// Stage direction (what to do with your hands / the screen).
const stage = (text) =>
  new Paragraph({
    spacing: { after: 140 },
    indent: { left: 280 },
    children: [new TextRun({ text: `―― ${text} ――`, font: JP, size: 19, italics: true, color: MUTED })],
  });

// Chinese note for the speaker, in a tinted single-cell table.
const note = (text) =>
  new Table({
    width: { size: 9300, type: WidthType.DXA },
    columnWidths: [9300],
    borders: {
      top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
    },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: 9300, type: WidthType.DXA },
            shading: { type: ShadingType.CLEAR, fill: TINT },
            margins: { top: 120, bottom: 120, left: 180, right: 180 },
            children: [
              new Paragraph({
                spacing: { after: 0, line: 300 },
                children: [new TextRun({ text, font: ZH, size: 19, color: MUTED })],
              }),
            ],
          }),
        ],
      }),
    ],
  });

const spacer = () => new Paragraph({ spacing: { after: 160 }, children: [] });

const qa = (q, a, tip) => [
  new Paragraph({
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text: `Q. ${q}`, font: JP, size: 21, bold: true, color: INK })],
  }),
  new Paragraph({
    spacing: { after: 100, line: 320 },
    indent: { left: 280 },
    children: [new TextRun({ text: a, font: JP, size: 21, color: INK })],
  }),
  note(tip),
  spacer(),
];

const doc = new Document({
  styles: { default: { document: { run: { font: JP, size: 22, color: INK } } } },
  sections: [
    {
      properties: { page: { margin: { top: 1000, bottom: 1000, left: 1100, right: 1100 } } },
      children: [
        new Paragraph({
          spacing: { after: 60 },
          children: [new TextRun({ text: "Mini Nowcast ｜ 面接トーク原稿", font: JP, size: 34, bold: true, color: INK })],
        }),
        new Paragraph({
          spacing: { after: 320 },
          children: [
            new TextRun({
              text: "mini-nowcast-intro.pptx（3ページ）用　／　所要 約2分30秒　／　オレンジの部分を強めに読む",
              font: JP, size: 19, color: MUTED,
            }),
          ],
        }),

        slideHead("冒頭　スライドを出す前", "約12秒"),
        line([
          "本日はお時間をいただき、ありがとうございます。応募にあたって、",
          { t: "御社の事業を自分でも小さく作ってみた" },
          "ので、それをご紹介させてください。",
        ]),
        note("开场钩子。先说「我动手做了」，对方才会认真看后面的屏幕。"),

        slideHead("1ページ目　つくったもの", "約33秒"),
        line([
          "つくったのは、スーパーのレシートのような購買データから、",
          { t: "物価が毎日どう動いているかを測るしくみ" },
          "です。さらに、そのデータに",
          { t: "日本語で質問すると、答えが返ってくるAIアシスタント" },
          "もつけました。",
        ]),
        stage("画面を指す"),
        line([
          "この画面は、実際に動いているものです。データは英国の小売2年分、",
          { t: "約104万件の公開データ" },
          "を使っています。そこから計算した結果、この2年間で",
          { t: "物価は4.7パーセント上がっていました" },
          "。",
        ]),
        note("说到「実際に動いているもの」时停一拍，指一下截图。HR 最在意的是「真的做出来了」，不是算法细节。"),

        slideHead("2ページ目　なぜつくったか", "約33秒　※ 最重要"),
        line([
          "なぜこれを作ったかというと、",
          { t: "御社の事業を調べたこと" },
          "がきっかけです。ナウキャストさんは、大きく2つの事業をされていると理解しました。",
        ]),
        line([
          "ひとつは、",
          { t: "JCBのカードデータや日経のPOSデータから、消費や物価の指標をつくる事業" },
          "。もうひとつは、",
          { t: "企業のデータ活用を生成AIで支援する事業" },
          "です。その2つを、公開データを使って自分の手で小さく再現してみたのが、今回のものになります。",
        ]),
        note("这页是整个演示的核心。说两个事业时，手依次指向幻灯片左列的 ① 和 ②。HR 会记住「这个人做过功课」。"),

        slideHead("3ページ目　学んだこと", "約36秒"),
        line([
          "作ってみて、",
          { t: "はじめて使う技術" },
          "が多くありました。データ加工を自動化するdbtや、生成AIをサービスに組み込む部分は、調べながら進めました。",
        ]),
        line([
          "一番苦労したのは、",
          { t: "AIが出してくる数字が正しいかどうか、自分では分からない" },
          "ことでした。そこで、回答に出てくる数字を",
          { t: "元のデータと自動で突き合わせて、確認できたものには印をつける" },
          "仕組みをつくりました。",
        ]),
        stage("緑のチェックマークを指す"),
        line([
          "AIは間違えることがあるので、",
          { t: "人が最後に確認できる形" },
          "にしています。",
        ]),
        note("指绿色 ✅ 的时候慢一点。这段传达「不盲信 AI、做事细致」，正好对应 JD 里的「泥臭い作業も厭わない」。"),

        slideHead("締め", "約17秒"),
        line([
          "インターンでは、実際のデータを使って、PythonやSQL、生成AIで",
          { t: "手を動かしたい" },
          "です。",
          { t: "地道な確認作業も含めて、最後までやり切る" },
          "ことを大事にしています。本日はよろしくお願いいたします。",
        ]),

        new Paragraph({ children: [], spacing: { after: 400 } }),
        h1("30秒の短縮版（「手短に」と言われたら）"),
        line([
          "購買データから物価の動きを毎日測るしくみと、そのデータに日本語で質問できるAIをつくりました。",
          "御社がJCB消費NOWなどでされていることを、公開データで小さく再現してみたものです。",
          "AIの回答は間違うことがあるので、出てきた数字を元データと突き合わせて確認する仕組みも入れています。",
        ]),

        h1("想定質問"),
        ...qa(
          "どのくらいの期間でつくりましたか？",
          "設計から動くところまでで、おおよそ〇日ほどです。データを見て気づいた問題を直す時間が、半分くらいを占めました。",
          "天数自己填。后半句是重点：说明时间花在「发现并修正问题」上，而不是敲代码。"
        ),
        ...qa(
          "一人でつくりましたか？",
          "はい。分からない部分は、公式ドキュメントやAIも使いながら進めました。",
          "老实说用了 AI。这个岗位本身就是做 AI 落地的，隐瞒反而奇怪。"
        ),
        ...qa(
          "難しかったところは？",
          "先ほどの、AIの数字を確認する部分です。あとは、データの中に見た目では気づけない問題があって、それを見つけるのに時間がかかりました。",
          "若追问「什么问题」，就讲价格渠道那个例子（同じ商品なのに、お客様によって値段が2倍違った）。别主动展开，HR 面不需要。"
        ),

        h1("練習メモ"),
        ...[
          "まず2ページ目だけを練習する。一番大事で、一番言い慣れが効く。",
          "全体を通して計測し、2分30秒を目安にする。3分を超えるなら3ページ目の「はじめて使う技術」の一文を削る。",
          "スライドには発表者ノートが入っている。本番はPresenter Viewで簡略版が見られる。",
        ].map((t, i) =>
          new Paragraph({
            spacing: { after: 120, line: 320 },
            indent: { left: 280, hanging: 220 },
            children: [new TextRun({ text: `${i + 1}.　${t}`, font: JP, size: 21, color: INK })],
          })
        ),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("written:", OUT);
});
