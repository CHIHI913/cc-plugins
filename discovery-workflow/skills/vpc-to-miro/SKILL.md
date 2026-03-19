---
name: vpc-to-miro
description: >
  MarkdownのVPC（Value Proposition Canvas）をMiroボード上のテンプレートフレームに付箋として自動配置する。
  VPCの6セクション（Jobs/Pains/Gains/Pain Relievers/Gain Creators/Products & Services）と
  Deep Diveの4セクション（事実/分析/戦略/提案）をパースし、
  ラベルに基づく色分け付きでMiro Bulk Create APIで一括作成する。
  「/vpc-to-miro」「miroにvpcを配置」「vpcをmiroに反映」で起動。
argument-hint: "file:<VPCファイルパス> board_url:<MiroフレームURL>"
triggers:
  - /vpc-to-miro
  - miroにvpcを配置
  - vpcをmiroに反映
allowed-tools: Read, Bash, AskUserQuestion
---

## 使い方

```
/vpc-to-miro file:<VPCファイルパス> board_url:<テンプレートフレームのURL>
```

`board_url`にはMiroでテンプレートフレームを開いたときのURL（`moveToWidget`パラメータ含む）を指定する。

## 処理フロー

1. **引数解析・URLパース**: URLから`BOARD_ID`と`FRAME_ID`を抽出（miro-api.md参照）
2. **Markdownパース**: `scripts/vpc_parser.py`でVPC構造をJSONとして抽出
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/vpc_parser.py <VPCファイルパス> /tmp/vpc_data.json
   ```
   パースルールの詳細は`vpc-parser.md`参照。
3. **ユーザー確認**: `vpc_parser.py`のstderr出力をそのまま表示して続行を確認。**JSONの中身を確認するアドホックスクリプトは書かないこと**（構造の誤解によるエラーの原因になる）
4. **Miro配置**: `scripts/vpc_miro_placer.py`で一括配置
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/vpc_miro_placer.py BOARD_ID FRAME_ID /tmp/vpc_data.json
   ```
   スクリプトが自動処理する内容:
   - アンカー座標の動的取得（凡例含む）
   - Customer Profile側: フェーズヘッダー付箋+コネクター（矢印）+コンテンツ付箋
   - Value Map側・Deep Dive: 3列グリッド配置
   - 凡例配置
   - 配置検証（作成数照合）

**トークンリフレッシュ**: 401エラー時に自動リフレッシュ（フロー全体に適用）

## ラベル→色マッピング（全ファイル共通の定義）

| ラベル | type       | fillColor    |
| ------ | ---------- | ------------ |
| 📗     | verified   | light_green  |
| 📘     | fact       | light_blue   |
| 💡     | hypothesis | light_yellow |
| ⭐     | new        | light_pink   |
| なし   | hypothesis | light_yellow |

## 環境変数

```
MIRO_ACCESS_TOKEN / MIRO_REFRESH_TOKEN / MIRO_CLIENT_ID / MIRO_CLIENT_SECRET
```

## 参照

- `vpc-parser.md`: Markdownパースルール（セクション判定・カラム判定・フィルタリング・出力形式）
- `miro-api.md`: Miro API仕様（URLパース・認証・Bulk Create・座標推定・検証）
- `scripts/vpc_parser.py`: Markdownパーサー（VPC MD → JSON変換。LLMパース不要で高速）
- `scripts/vpc_miro_placer.py`: Miro配置スクリプト（アンカー検出→座標計算→全配置→検証を一括実行）
