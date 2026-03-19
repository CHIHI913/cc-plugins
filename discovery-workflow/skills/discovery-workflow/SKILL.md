---
name: discovery-workflow
description: >
  ディスカバリーフェーズ（リーンキャンバス〜ブランドコンセプト）の全体ワークフローガイド。
  各Phaseの目的・インプット・アウトプット・判断基準を提示し、次に何をすべきか案内する。
  ディスカバリーの進め方がわからないとき、次のPhaseに進むべきか判断したいとき、
  ワークフロー全体を俯瞰したいときに使う。「ディスカバリー」「ワークフロー」「次のフェーズ」
  「Phase」「仮説検証の進め方」といった文脈で積極的に起動すること。
---

# ディスカバリーワークフロー

ディスカバリーフェーズ（リーンキャンバス〜ブランドコンセプト）の実践ワークフロー。

## 全体構成

| 層 | Phase | 内容 | スキル | 所要時間 |
|----|-------|------|--------|----------|
| Why | 1 | リーンキャンバス v1 | `/lean-canvas` | 2h |
| Why | 2 | VPC v1（関係者ブレスト） | `/vpc` | 3h |
| Why | 3 | プロダクト側調査 | `/pest` → `/swot` → `/competitor` → `/stp` | PdM単独 |
| Why | 4 | VPC v2 → 仮説立案 | `/vpc` `/hypothesis` | - |
| Why | 5 | インタビュー（都度VPC更新） | `/interview` | - |
| Why | 6 | ユーザータイプ分析 | `/user-type` | - |
| Core-Why Fit | 7 | ブランドコンセプト + LC v2 | `/brand-concept` `/lean-canvas` | - |
| What | 8 | MVP作成 | - | - |
| What | 9 | ソリューション検証 | `/interview` | - |
| Why-What Fit | 10 | Fit確認 + LC v3（最終版） | `/lean-canvas` | - |
| How | 11 | PRD作成 | - | - |

## 進め方

1. 上のテーブルのPhase順に進める
2. 各Phaseのスキルを呼び出してドキュメントを作成する
3. Fit確認（Phase 7, 10）でFitしない場合は前のPhaseに戻る

## Fit判定

- **Core-Why Fit**（Phase 7）: Whyの検討結果がCore（ビジョン）と整合しているか
- **Why-What Fit**（Phase 10）: ソリューション（What）がWhy（課題・ターゲット）と整合しているか

Fitしない場合のRefineトリガー:
- インタビューで想定と異なる反応が出た
- 競合状況が変化した
- ステークホルダーとの議論で方向性が変わった

**重要**: スケジュールより仮説検証を優先する。

## 関連スキル一覧

| フェーズ | スキル | コマンド |
|----------|--------|----------|
| Phase 1, 7, 10 | リーンキャンバス | `/lean-canvas` |
| Phase 2, 4, 5 | バリュー・プロポジション・キャンバス | `/vpc` |
| Phase 3 Step 1 | PEST分析 | `/pest` |
| Phase 3 Step 2 | SWOT分析 | `/swot` |
| Phase 3 Step 3 | 競合分析 | `/competitor` |
| Phase 3 Step 4 | STP分析 | `/stp` |
| Phase 4 | 仮説立案 | `/hypothesis` |
| Phase 5, 9 | インタビュー | `/interview` |
| Phase 6 | ユーザータイプ分析 | `/user-type` |
| Phase 7 | ブランドコンセプト | `/brand-concept` |
| Miro連携 | PEST/SWOT/VPC/LC → Miro | `/pest-to-miro` `/swot-to-miro` `/vpc-to-miro` `/lean-canvas-to-miro` |

各Phaseの詳細は `${CLAUDE_PLUGIN_ROOT}/skills/discovery-workflow/references/phases.md` を参照。
