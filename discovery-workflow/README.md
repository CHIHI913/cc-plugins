# discovery-workflow

プロダクトの「誰に・何を・なぜ」を検証するディスカバリーフェーズを、Claude Code上で対話的に進めるプラグイン。

リーンキャンバスからブランドコンセプトまで、10種のフレームワークをテンプレートに沿って作成でき、作成したドキュメントはMiroボードへ自動転記できる。

## ワークフロー

```
Phase 1  リーンキャンバス v1（全体俯瞰）
Phase 2  VPC v1（課題と価値の初期仮説）
Phase 3  PEST → SWOT → 競合分析 → STP（プロダクト側調査）
Phase 4  VPC v2 → 仮説立案（仮説深化）
Phase 5  インタビュー（ペイン・ゲイン検証）
Phase 6  ユーザータイプ分析（ユーザー理解の構造化）
Phase 7  ブランドコンセプト + リーンキャンバス v2（Core-Why Fit）
```

各Phaseに対応するスキルがあり、`/discovery-workflow` で全体の進め方を確認できる。

## インストール

```bash
claude plugin add github:CHIHI913/cc-plugins/discovery-workflow
```

## 使い方

### フレームワーク作成

スキルを呼び出すと、テンプレートに沿って対話的にドキュメントを作成する。

```
/lean-canvas          リーンキャンバス
/vpc                  バリュー・プロポジション・キャンバス
/pest                 PEST分析
/swot                 SWOT分析
/competitor           競合分析
/stp                  STP分析
/hypothesis           仮説立案
/interview            インタビュースクリプト
/user-type            ユーザータイプ分析
/brand-concept        ブランドコンセプト
```

### Miro自動転記

Markdownで作成したドキュメントをMiroボード上の付箋として自動配置する。

```
/lean-canvas-to-miro  file:<ファイルパス> board_url:<MiroフレームURL>
/vpc-to-miro          file:<ファイルパス> board_url:<MiroフレームURL>
/pest-to-miro         file:<ファイルパス> board_url:<MiroフレームURL>
/swot-to-miro         file:<ファイルパス> board_url:<MiroフレームURL>
```

### ワークフロー確認

```
/discovery-workflow   全Phase の目的・進め方・判断基準を確認
```

## 前提条件

Miro連携スキルを使う場合、以下の環境変数が必要：

```
MIRO_ACCESS_TOKEN
MIRO_REFRESH_TOKEN
MIRO_CLIENT_ID
MIRO_CLIENT_SECRET
```

## サンプル

各フレームワークに架空の料理レシピ共有アプリ「CookPal」を題材にしたサンプルを同梱。実例として参照できる。

## License

MIT
