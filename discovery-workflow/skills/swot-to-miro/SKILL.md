---
name: swot-to-miro
description: >
  MarkdownのSWOT分析を Miro ボード上のテンプレートフレームに付箋として自動配置する。
  SWOTマトリクスで選定された重要要因をピンク、その他を黄色で色分けし、クロスSWOT戦略も配置する。
  SWOT分析を Miro で共有・議論したいとき、戦略検討をビジュアルに整理したいときに使う。
  「SWOT を Miro に」「Miro に配置」「ボードに反映」といった文脈で積極的に起動すること。
---

## 使い方

```
/swot-to-miro file:<SWOT分析ファイルパス> board_url:<テンプレートフレームのURL>
```

## 処理フロー

1. **引数解析・URLパース**: URLから`BOARD_ID`と`FRAME_ID`を抽出
2. **Markdownパース**: `scripts/swot_parser.py`でSWOT構造をJSONとして抽出
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/swot_parser.py <ファイルパス> /tmp/swot_data.json
   ```
3. **ユーザー確認**: パーサーのstderr出力をそのまま表示して続行を確認
4. **Miro配置**: `scripts/swot_placer.py`で一括配置
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/swot_placer.py BOARD_ID FRAME_ID /tmp/swot_data.json
   ```

## セクション対応

| Markdownセクション | パーサーキー | Miroアンカーキーワード |
|-------------------|------------|---------------------|
| ### S（強み） | strengths | 強み / Strengths |
| ### W（弱み） | weaknesses | 弱み / Weaknesses |
| ### O（機会） | opportunities | 機会 / Opportunities |
| ### T（脅威） | threats | 脅威 / Threats |
| ### 積極戦略（S×O） | so_strategy | 積極戦略 |
| ### 改善戦略（W×O） | wo_strategy | 改善戦略 |
| ### 差別化戦略（S×T） | st_strategy | 差別化戦略 |
| ### 防衛戦略（W×T） | wt_strategy | 防衛戦略 |

## ハイライト

`## SWOT マトリクス`のテーブルに記載された要因名と、S/W/O/Tセクションの要因名が一致するものをlight_pink（ピンク）で配置。マトリクスに記載されていない要因とクロスSWOTはlight_yellow。

要因名の一致は部分一致（マトリクスの項目名がセクションの要因名に含まれるか）で判定。

**トークンリフレッシュ**: 401エラー時に自動リフレッシュ

## 環境変数

```
MIRO_ACCESS_TOKEN / MIRO_REFRESH_TOKEN / MIRO_CLIENT_ID / MIRO_CLIENT_SECRET
```
