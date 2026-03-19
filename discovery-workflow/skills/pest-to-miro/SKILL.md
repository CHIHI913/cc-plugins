---
name: pest-to-miro
description: MarkdownのPEST分析をMiroボード上のテンプレートフレームに付箋として自動配置する。P（政治）/E（経済）/S（社会）/T（技術）の4セクションのテーブルをパースし、PEST要因評価に記載された重要要因をlight_pink、それ以外をlight_yellowで配置する。「/pest-to-miro」「miroにPESTを配置」「PESTをmiroに反映」で起動。
---

## 使い方

```
/pest-to-miro file:<PEST分析ファイルパス> board_url:<テンプレートフレームのURL>
```

## 処理フロー

1. **引数解析・URLパース**: URLから`BOARD_ID`と`FRAME_ID`を抽出
2. **Markdownパース**: `scripts/pest_parser.py`でPEST構造をJSONとして抽出
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/pest_parser.py <ファイルパス> /tmp/pest_data.json
   ```
3. **ユーザー確認**: パーサーのstderr出力をそのまま表示して続行を確認
4. **Miro配置**: `scripts/pest_placer.py`で一括配置
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/pest_placer.py BOARD_ID FRAME_ID /tmp/pest_data.json
   ```

## セクション対応

| Markdownセクション | パーサーキー | Miroアンカーキーワード |
|-------------------|------------|---------------------|
| ## P（Politics） | politics | 政治 |
| ## E（Economy） | economy | 経済 |
| ## S（Society） | society | 社会 |
| ## T（Technology） | technology | 技術 |

## パースルール

各P/E/S/Tセクション内のテーブル行（`# / 要因 / 事実・データ / プロダクトへの示唆`）を「要因: プロダクトへの示唆」の形式で1付箋にまとめる。サマリーとPEST要因評価セクションはスキップ。

## ハイライト

`## PEST要因評価`テーブルの要因名と、各P/E/S/Tセクションの要因名が一致するものをlight_pink（ピンク）で配置。一致しない要因はlight_yellow。要因名は完全一致で判定するため、PEST要因評価と各セクションで名称を揃える必要がある。

**トークンリフレッシュ**: 401エラー時に自動リフレッシュ

## 環境変数

```
MIRO_ACCESS_TOKEN / MIRO_REFRESH_TOKEN / MIRO_CLIENT_ID / MIRO_CLIENT_SECRET
```
