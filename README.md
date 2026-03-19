# cc-plugins

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) のプラグイン集です。プロダクトマネジメントや業務効率化のためのスキル・自動化ツールを提供します。

## プラグイン一覧

### [discovery-workflow](./discovery-workflow/)

プロダクトの「誰に・何を・なぜ」を検証するディスカバリーフェーズを、Claude Code上で対話的に進めるプラグイン。リーンキャンバスからブランドコンセプトまで10種のフレームワークをテンプレートに沿って作成でき、作成したドキュメントはMiroボードへ自動転記できます。

Claude Code 内で実行：

```
# 初回のみ：マーケットプレイスを登録
/plugin marketplace add CHIHI913/cc-plugins
```

```
# プラグインをインストール
/plugin install discovery-workflow@cc-plugins
```

マーケットプレイスの登録は初回のみです。今後このリポジトリに別のプラグインが追加された場合も、`/plugin install` だけでインストールできます。

<details>
<summary>スキル一覧（15スキル）</summary>

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

</details>

> 詳細は [discovery-workflow/README.md](./discovery-workflow/README.md) を参照

## 対象ユーザー

- プロダクトマネージャー
- 新規事業・新機能の仮説検証を進めるチーム
- Claude Codeをプロダクトマネジメントに活用したい方

## 要件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) がインストール済みであること
- Miro連携を使う場合は Miro API トークンが必要（詳細は各プラグインのREADMEを参照）

## License

MIT
