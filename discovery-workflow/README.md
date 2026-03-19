# discovery-workflow

ディスカバリーフェーズ（リーンキャンバス〜ブランドコンセプト〜PRD）を支援する Claude Code プラグイン。プロダクトマネジメントにおける仮説検証プロセスの各フレームワークをスキルとして提供する。

## Available Skills

### フレームワークスキル（10）

| スキル | コマンド | 概要 |
|--------|----------|------|
| リーンキャンバス | `/lean-canvas` | 9要素でプロダクト仮説を俯瞰 |
| VPC | `/vpc` | バリュー・プロポジション・キャンバスの作成・更新 |
| PEST分析 | `/pest` | 外部環境（政治・経済・社会・技術）の分析 |
| SWOT分析 | `/swot` | 内部/外部環境の整理とクロスSWOT戦略導出 |
| 競合分析 | `/competitor` | 競合のWho-What-How分析と差別化特定 |
| STP分析 | `/stp` | セグメンテーション・ターゲティング・ポジショニング |
| 仮説立案 | `/hypothesis` | 仮説の体系的整理と検証ポイント定義 |
| インタビュー | `/interview` | インタビュースクリプト作成と検証実施 |
| ユーザータイプ分析 | `/user-type` | ユーザーのタイプ分類とソリューション仮説 |
| ブランドコンセプト | `/brand-concept` | プロダクトの世界観・約束・提供価値の統合 |

### Miro連携スキル（4）

| スキル | コマンド | 概要 |
|--------|----------|------|
| PEST → Miro | `/pest-to-miro` | PEST分析結果をMiroボードに出力 |
| SWOT → Miro | `/swot-to-miro` | SWOT分析結果をMiroボードに出力 |
| VPC → Miro | `/vpc-to-miro` | VPCをMiroボードに出力 |
| リーンキャンバス → Miro | `/lean-canvas-to-miro` | リーンキャンバスをMiroボードに出力 |

### ワークフローガイド（1）

| スキル | コマンド | 概要 |
|--------|----------|------|
| ディスカバリーワークフロー | `/discovery-workflow` | 全体ワークフローの概要と各フェーズの進め方 |

## Installation

```bash
claude plugin add github:CHIHI913/cc-plugins/discovery-workflow
```

## Prerequisites

- Miro連携スキルを使用する場合は、Miro API トークンが必要です

## License

MIT
