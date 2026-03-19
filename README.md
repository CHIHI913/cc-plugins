# cc-plugins

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) のプラグイン集です。プロダクトマネジメントや業務効率化のためのスキル・自動化ツールを提供します。

## プラグイン一覧

### [discovery-workflow](./discovery-workflow/)

プロダクトの「誰に・何を・なぜ」を検証するディスカバリーフェーズを、Claude Code上で対話的に進めるプラグイン。リーンキャンバスからブランドコンセプトまで10種のフレームワークをテンプレートに沿って作成でき、作成したドキュメントはMiroボードへ自動転記できます。

```bash
claude plugin add github:CHIHI913/cc-plugins/discovery-workflow
```

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
