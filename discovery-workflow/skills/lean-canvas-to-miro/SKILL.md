---
name: lean-canvas-to-miro
description: >
  Markdownのリーンキャンバスを Miro ボード上のテンプレートフレームに付箋として自動配置する。
  リーンキャンバスを作成した後に Miro に転記したいとき、チームでリーンキャンバスを共有・議論したいときに使う。
  「Miro に配置」「Miro に転記」「リーンキャンバスを Miro に」「ボードに反映」といった文脈で積極的に起動すること。
---

## 使い方

```
/lean-canvas-to-miro file:<リーンキャンバスファイルパス> board_url:<テンプレートフレームのURL>
```

`board_url`にはMiroでテンプレートフレームを開いたときのURL（`moveToWidget`パラメータ含む）を指定する。

## 処理フロー

1. **引数解析・URLパース**: URLから`BOARD_ID`と`FRAME_ID`を抽出
   ```
   https://miro.com/app/board/{BOARD_ID}/?moveToWidget={FRAME_ID}&cot=14
   ```
2. **Markdownパース**: `scripts/lean_canvas_parser.py`でリーンキャンバス構造をJSONとして抽出
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/lean_canvas_parser.py <ファイルパス> /tmp/lean_canvas_data.json
   ```
3. **ユーザー確認**: パーサーのstderr出力（セクション別件数）をそのまま表示して続行を確認
4. **Miro配置**: `scripts/lean_canvas_placer.py`で一括配置
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/lean_canvas_placer.py BOARD_ID FRAME_ID /tmp/lean_canvas_data.json
   ```
   スクリプトが自動処理する内容:
   - アンカー座標の動的取得（ゼロ幅文字の除去含む）
   - エリアサイズに応じた列数の自動決定（幅2000+→3列、1200+→2列、他→1列）
   - エリア内で上下左右中央配置
   - 配置検証（作成数照合）

**トークンリフレッシュ**: 401エラー時に自動リフレッシュ

## セクション対応

| Markdownセクション | パーサーキー | Miroアンカーキーワード |
|-------------------|------------|---------------------|
| ## 1: カスタマーセグメント → ### カスタマーセグメント | customer_segments | カスタマーセグメント |
| ## 1: → ### アーリーアダプター | early_adopters | アーリーアダプター |
| ## 2: 課題 | problems | 課題 |
| ## 2: → ### 既存の代替品（テーブル） | existing_alternatives | 既存の代替品 |
| ## 3: → ### UVP | uvp | 独自の価値提案 |
| ## 3: → ### ハイレベルコンセプト | high_level_concept | ハイレベルコンセプト |
| ## 4: ソリューション | solutions | ソリューション |
| ## 5: チャネル | channels | チャネル |
| ## 6: 収益の流れ | revenue | 収益の流れ |
| ## 7: コスト構造 | costs | コスト構造 |
| ## 8: 主要指標 → ### NSM + ### KPI | key_metrics | 主要指標 |
| ## 9: 圧倒的な優位性 | unfair_advantage | 圧倒的な優位性 |

## 付箋の色

全付箋 `light_yellow`（リーンキャンバスは全て仮説ベースのため）。

## 既存の代替品のパース

テーブル形式の行を `課題 / 直接競合 / 代替行動` の形式で1つの付箋にまとめる。

## 環境変数

```
MIRO_ACCESS_TOKEN / MIRO_REFRESH_TOKEN / MIRO_CLIENT_ID / MIRO_CLIENT_SECRET
```
