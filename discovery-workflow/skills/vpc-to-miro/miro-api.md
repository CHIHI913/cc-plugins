# Miro API仕様

## URLパース

```
https://miro.com/app/board/{BOARD_ID}/?moveToWidget={FRAME_ID}&cot=14
```

`moveToWidget`がない場合はエラー。テンプレートフレームのURLを要求する。

## 認証

環境変数: `MIRO_ACCESS_TOKEN` / `MIRO_REFRESH_TOKEN` / `MIRO_CLIENT_ID` / `MIRO_CLIENT_SECRET`

`~/.zshrc.secrets`に保存されている。Bashツールでは非インタラクティブシェルのため`source`が効かない場合がある。以下で確実に読み込む:

```bash
eval $(grep '^export MIRO_' ~/.zshrc.secrets)
```

共通ヘッダー:
```
Authorization: Bearer ${MIRO_ACCESS_TOKEN}
Content-Type: application/json
```

### トークンリフレッシュ

401エラー時に自動実行:

```bash
curl -s -X POST "https://api.miro.com/v1/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&client_id=${MIRO_CLIENT_ID}&client_secret=${MIRO_CLIENT_SECRET}&refresh_token=${MIRO_REFRESH_TOKEN}"
```

レスポンスの`access_token`と`refresh_token`で環境変数を更新。リフレッシュは1リクエストにつき1回まで。

## 主要API

ベースURL: `https://api.miro.com/v2/boards/${BOARD_ID}`

| 操作 | メソッド | パス |
|------|---------|------|
| フレーム内アイテム取得 | GET | `/items?parent_item_id=${FRAME_ID}&limit=50` |
| 付箋一括作成 | POST | `/items/bulk` |
| 付箋単体作成 | POST | `/sticky_notes` |
| コネクター作成 | POST | `/connectors` |

### Bulk Create（付箋一括作成）

20個ずつバッチ送信。トランザクション型（1つ失敗→全体ロールバック）。

**リクエストボディはオブジェクトではなく配列**:

```json
[
  {
    "type": "sticky_note",
    "data": { "content": "付箋テキスト" },
    "style": { "fillColor": "light_green" },
    "position": { "x": 100, "y": 100 },
    "parent": { "id": "FRAME_ID" }
  }
]
```

**注意**: `position`に`relativeTo`や`origin`フィールドを含めるとエラーになる。`x`と`y`のみ指定すること。単体作成（POST /sticky_notes）も同様。

`fillColor`はSKILL.mdのラベル→色マッピングに従う。

## エラーハンドリング

- **429**: exponential backoff（`2^attempt`秒）でリトライ、最大3回
- **401**: トークンリフレッシュして再試行（1回のみ）
- **その他**: リトライ後もエラーなら中断
- API呼び出し間隔: 100ms

## 座標推定

**座標系**: フレーム左上が原点 (0, 0)。x右方向・y下方向が正。

### 動的取得（優先）

フレーム内アイテムの`data.content`または`data.plainText`にセクション名を含むshapeまたはtextを検索。見つかったアイテムの座標+y60pxオフセットを付箋配置位置とする。

検索キーワード:
- VPC: "Customer Jobs", "Pains", "Gains", "Pain Relievers", "Gain Creators", "Products and Services"
- Deep Dive: "事実", "分析", "戦略N", "提案N"（Nは番号。番号なしも許容）

**戦略・提案の分岐**: テンプレート上に「戦略1」「戦略2」「提案1」「提案2」のように番号付きアンカーが存在する。パーサーのMarkdown側も番号付きヘッダー（`### 戦略1`, `### 戦略2`等）で分岐を表現する。番号でアンカーとパース結果を対応付ける。

**テンプレート準備**: Strategyzer等のPDFベースのテンプレートではセクション名が画像内に埋め込まれておりAPIで検出できない。テンプレートフレーム内にセクション名を持つshapeまたはtextをアンカーとして配置しておくこと。

### 静的フォールバック

動的取得で見つからないセクションに適用。基準フレーム (2400x1600) の比率で定義し、実際のフレームサイズにスケーリングする:

```
基準比率（フレーム幅W・高さHに対する割合）:

右半分 = Customer Profile
  jobs:          (0.75W, 0.25H)
  pains:         (0.625W, 0.65H)
  gains:         (0.875W, 0.65H)

左半分 = Value Map
  products:      (0.25W, 0.50H)
  painRelievers: (0.35W, 0.50H)
  gainCreators:  (0.45W, 0.50H)
```

フレームサイズはGET `/items/{FRAME_ID}`の`geometry.width`/`geometry.height`から取得。一部動的+一部静的の混在OK。

### レイアウトモード

付箋サイズ: S: 125x143px, M: 199x228px, L: 271x311px（APIでは geometry.width で指定）

#### フェーズベースレイアウト（Customer Profile側: jobs/pains/gains）

phaseフィールドを持つセクションに適用。フェーズを横並びの緑付箋+矢印で表示し、各フェーズの下にコンテンツ付箋を縦配置する。

```
レイアウト:
  [Phase1] → [Phase2] → [Phase3] → [Phase4]
  [item1a]   [item2a]   [item3a]   [item4a]
  [item1b]   [item2b]   [item3b]   [item4b]
```

**作成手順**:
1. パース結果から出現順にユニークなフェーズ一覧を取得
2. フェーズヘッダー付箋を個別作成（POST /sticky_notes）→ IDを収集
3. 隣接フェーズ間にコネクター作成（POST /connectors）
4. コンテンツ付箋をBulk Createで一括作成

```
付箋サイズ: M (199x228px)
列間隔: 80px（コネクター用スペース含む）
列ピッチ: 279px (199 + 80)

フェーズヘッダー:
  x = anchor_x + phase_index * 279
  y = anchor_y
  fillColor: light_green（固定）
  content: フェーズ名のみ（例: "情報収集"）

コンテンツ:
  x = anchor_x + phase_index * 279
  y = anchor_y + 248 + row * 238
  fillColor: ラベルに基づく色マッピング
  content: コンテンツのみ（フェーズ名を含めない）
  ※ row = そのフェーズ内での0始まりインデックス
```

**コネクター（フェーズ間の矢印）**:

```json
{
  "startItem": { "id": "PHASE_N_ID" },
  "endItem": { "id": "PHASE_N+1_ID" },
  "style": { "strokeColor": "#808080", "strokeWidth": "2.0" }
}
```

フェーズヘッダーのIDはPOST /sticky_notesのレスポンスから取得。コネクターはフレームの`parent`指定不要（ボードレベルで作成）。

#### グリッド配置（Value Map側・Deep Dive）

phaseフィールドを持たないセクションに適用。アンカー座標を起点に3列グリッドで配置:

```
付箋サイズ: M (199x228px)
間隔: x=10px, y=10px
列数: 3

位置計算:
  col = index % 3
  row = index / 3 (切り捨て)
  x = anchor_x + col * (199 + 10)
  y = anchor_y + row * (228 + 10)
```

## 配置検証

付箋作成後、フレーム内の`sticky_note`アイテム数を取得し、パース結果の`stats.total`と照合。不一致時は差分を報告。

## 座標キャッシュ

`~/.cache/miro-vpc/${BOARD_ID}_${FRAME_ID}.json` に保存・読み込み。
