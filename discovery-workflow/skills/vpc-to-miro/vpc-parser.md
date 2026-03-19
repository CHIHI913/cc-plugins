# VPC Markdownパースルール

## 対象テーブルの識別

**先頭列が「ラベル」のテーブルのみパース対象。** それ以外のテーブル（凡例、ペルソナ分類、ステップ表、候補比較等）は無視する。凡例テーブルはパース対象セクション（`###`）の外にあるため自動的にスキップされる。

## 対象セクション（これ以外はスキップ）

| キーワード（部分一致） | セクション | 除外条件 |
|----------------------|-----------|---------|
| `Customer Jobs` | jobs | — |
| `Pains` | pains | `Pain Relievers`を含まない |
| `Gains` | gains | `Gain Creators`を含まない |
| `Pain Relievers` | painRelievers | — |
| `Gain Creators` | gainCreators | — |
| `Products & Services` / `Products and Services` | products | — |
| `事実` | facts | — |
| `分析` | analysis | — |
| `戦略` | strategy | 番号/アルファベット付き（戦略1, 戦略A...）で分岐可能 |
| `提案` | proposal | 番号/アルファベット付き（提案1, 提案A...）で分岐可能 |

`###` ヘッダーで分割。括弧付き（例: `### Customer Jobs（達成したいこと）`）や番号付き（例: `### 1. 事実`）にもマッチさせる。

## カラム判定

先頭列は常に「ラベル」。セクション種別に応じて固定位置で読む:

**カスタマープロファイル側（jobs/pains/gains）**: col1=`ラベル`、col2=`フェーズ`、col3=`content`、以降無視

**バリューマップ側（painRelievers/gainCreators/products）**: col1=`ラベル`、col2=`ref`、col3=`content`、以降無視

**事実→分析→戦略→提案**: col1=`ラベル`、col2=`content`、以降無視

## フィルタリング

- **棄却行**: `❌`を含む行、または`~~テキスト~~`で囲まれた行 → スキップ
- **区切り行**: `|---|---|`パターン → スキップ
- **複数テーブル**: 同一セクション内で先頭列が「ラベル」のテーブルのみ結合。先頭列が「ラベル」でないテーブルは無視

## ラベル→type判定

先頭列（ラベル列）の絵文字からtypeを判定（マッピングはSKILL.md参照）。ラベルなしはhypothesis。

## 付箋テキスト構成

- カスタマープロファイル側（フェーズベースレイアウト用）:
  - フェーズヘッダー付箋: `フェーズ`列の値のみ（例: "情報収集"）→ light_green固定
  - コンテンツ付箋: `content`列の値のみ → ラベルに基づく色
- バリューマップ側: `content`列の値のみ（refは含めない）
- 事実→分析→戦略→提案: `content`列の値のみ

## 出力形式

```json
{
  "title": "VPC: ...",
  "customerProfile": {
    "jobs": [{ "phase": "...", "content": "...", "type": "verified", "label": "📗" }],
    "pains": [...],
    "gains": [...]
  },
  "valueMap": {
    "painRelievers": [{ "content": "...", "type": "verified", "label": "📗" }],
    "gainCreators": [...],
    "products": [...]
  },
  "deepDive": {
    "facts": [{ "content": "...", "type": "fact", "label": "📘" }],
    "analysis": [...],
    "strategies": {
      "1": [{ "content": "...", "type": "hypothesis", "label": "💡" }],
      "2": [...]
    },
    "proposals": {
      "1": [...],
      "2": [...]
    }
  },
  "stats": { "jobs": 5, "pains": 8, "gains": 6, "painRelievers": 8, "gainCreators": 6, "products": 4, "facts": 3, "analysis": 4, "strategy": 2, "proposal": 5, "skipped": 3, "total": 50 }
}
```
