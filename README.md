[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://github.com/CHIHI913/cc-plugins/blob/main/LICENSE)

# cc-plugins: プロダクトマネジメントのためのClaude Codeプラグイン集

> 15スキルでディスカバリーフェーズを対話的に進める。フレームワーク作成からMiro転記まで。

## すぐに使う

新しいプロダクト企画？ → `/lean-canvas`
顧客の課題を整理？ → `/vpc`
市場環境を分析？ → `/pest`
インタビュー準備？ → `/interview`
全体の進め方を確認？ → `/discovery-workflow`

## インストール

マーケットプレイスを登録（初回のみ）：

```
/plugin marketplace add CHIHI913/cc-plugins
```

プラグインをインストール：

```
/plugin install discovery-workflow@cc-plugins
```

## プラグイン一覧

### [discovery-workflow](./discovery-workflow/)

プロダクトの「誰に・何を・なぜ」を検証するディスカバリーフェーズを、Claude Code上で対話的に進めるプラグイン。リーンキャンバスからブランドコンセプトまで10種のフレームワークをテンプレートに沿って作成でき、作成したドキュメントはMiroボードへ自動転記できます。

ワークフロー全体像・各スキルの使い方・前提条件は [discovery-workflow/README.md](./discovery-workflow/README.md) を参照してください。

| コマンド | 概要 |
|----------|------|
| `/discovery-workflow` | ワークフロー全体ガイド（各Phaseの目的・判断基準） |
| `/lean-canvas` | リーンキャンバス作成 |
| `/vpc` | バリュー・プロポジション・キャンバス作成 |
| `/pest` | PEST分析（政治・経済・社会・技術） |
| `/swot` | SWOT分析 + クロスSWOT戦略導出 |
| `/competitor` | 競合分析（Who-What-How + 機能比較） |
| `/stp` | STP分析 |
| `/hypothesis` | 仮説立案（検証ポイント定義） |
| `/interview` | インタビュースクリプト作成 |
| `/user-type` | ユーザータイプ分析（2軸4象限） |
| `/brand-concept` | ブランドコンセプト作成 |
| `/lean-canvas-to-miro` | リーンキャンバス → Miro自動転記 |
| `/vpc-to-miro` | VPC → Miro自動転記 |
| `/pest-to-miro` | PEST分析 → Miro自動転記 |
| `/swot-to-miro` | SWOT分析 → Miro自動転記 |

## なぜこのプラグイン？

汎用AIに「リーンキャンバスを作って」と頼むと、それっぽいテキストが出てきます。でも実際のディスカバリーでは、フレームワーク間の整合性、仮説の検証状況の追跡、ドキュメントのバージョン管理が必要です。

このプラグインは：

- **ワークフローとして統合** — 各フレームワークが次のPhaseにどうつながるか定義済み（PEST→SWOT→STP→VPC v2→仮説立案→インタビュー→...）
- **仮説の状態管理** — 📗検証済み / 📘事実 / 💡仮説のラベルで、どの情報が確認済みでどれが未検証かを可視化
- **バージョニング** — VPCはv1→v2→v3...とインタビューのたびに更新。リーンキャンバスもPhaseごとにv1→v2→v3
- **Miro連携** — 作成したMarkdownをワンコマンドでMiroボードに付箋として自動配置。チームでの議論にすぐ使える

## 対象ユーザー

- プロダクトマネージャー
- 新規事業・新機能の仮説検証を進めるチーム
- Claude Codeをプロダクトマネジメントに活用したい方

## 要件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) がインストール済みであること
- Miro連携を使う場合は Miro API トークンが必要（詳細は各プラグインのREADMEを参照）

## License

MIT
