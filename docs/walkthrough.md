# ATDDプロセス・オーケストレーター＆ダッシュボード開発完了報告

ユーザーが指定したアンケート・仕様情報・テストURLを元に、ATDD（受け入れテスト駆動開発）の全プロセス（ペルソナ選定、エージェント間対話、要件定義、テスト自動生成、Playwrightテスト実行、品質メトリクス算出）をリアルタイムにシミュレートし、すべての成果物とテスト実行の様子を美しく可視化する超豪華SPA（シングルページアプリケーション）を開発しました。

---

## 開発成果物の構成

本アプリケーションは、ローカル環境で軽快に動作するフロントエンド完結型のリッチSPAとして設計・実装されています。また、ATDDプロセスを通じて出力される全ての詳細な成果物を、アプリ内のダッシュボード上で直接閲覧できるように統合しました。

* **アプリケーション・ファイル**:
  * アプリ構造の定義: [index.html](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/index.html)
  * ダークフューチャリスティック・デザインシステム: [styles.css](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/styles.css)
  * 動的プロセスシミュレーション・グラフ描画・完全ローカルフィルタリングロジック: [app.js](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/app.js)
  * プレビュー動画アセット: [verify_receipt_normal.webm](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/assets/verify_receipt_normal.webm)
* **詳細化された成果物ドキュメント（生 Markdown / 全てサイト内で直接閲覧可能）**:
  * AIユーザークローン定義書: [personas.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/personas.md)
  * 深層インタビュー完全対話録: [interviews.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/interviews.md)
  * ワークショップ統合成果物: [workshop_deliverables.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/workshop_deliverables.md)
  * 要求要望仕分け一覧（マトリクス表付き）: [requirements.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/requirements.md)
  * ユーザーストーリー・Gherkin受入基準: [user_stories.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/user_stories.md)
  * ATDD自動化適性評価レビュー: [atdd_automation_status.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/atdd_automation_status.md)
  * 自動テスト実行結果レポート: [test_execution_results.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/test_execution_results.md)
  * プロダクト責任者リリース・優先度レビュー: [project_manager_review.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/project_manager_review.md)
  * 品質メトリクス評価レポート: [quality_metrics.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/quality_metrics.md)
  * 全体ウォークスルー報告書: [walkthrough.md](file:///C:/Users/plain/.gemini/antigravity/scratch/atdd-dashboard/docs/walkthrough.md)

---

## 主な機能とWOW体験のハイライト

### 1. サーバー・環境制限を100%排除した「オフライン自己完結」アーキテクチャへの刷新
* ブラウザのローカルファイル制限（`file:///` スキームでのダブルクリック起動時の CORS 制限）による fetch エラーを完全に防ぐため、**すべての成果物ドキュメントを `app.js` のメモリ内に完全な状態で直接埋め込みました。**
* サーバーの起動状況やブラウザの接続方法、CORSに一切左右されず、100%確実にすべてのブラウザで動作し、成果物が即座にロードされます。

### 2. 「起動した瞬間」からの完全表示＆直接閲覧
* プロセスのシミュレーション実行を待つ必要は一切ありません。**ダッシュボードを開いた初期状態から、すべてのタブに詳細な成果物（クローン全属性、深層インタビュー、マトリクス等）が一切のサマリーや省略なく美しくレンダリング**されます。
* ユーザーは、外部リンクに遷移したりローカルファイルを開く手間なく、ダッシュボードのタブを切り替えるだけで、すべてのプロセス成果物を即座にその場で完全に閲覧できます。

### 3. クローン選択に連動する「リアルタイム・フィルタリング」
* 画面左ペインの「高木クローン」「高橋クローン」「上田クローン」のチェックボックスを切り替えると、**プロセスの実行ボタンを押さなくても、その瞬間にメモリ内の Markdown 文字列から該当する記述や発言が動的に置換・削除され、成果物表示がリアルタイムに再描画**されます。
* ワークショップの参加体制を変更した際の影響（成果物の変化）を、一切の遅延なく目の前で即座に検証することができます。

### 4. タイムライン連動型・リアルタイム実行シミュレーター
* 「ATDDプロセスを実行する」をクリックすると、グローバルステータスが **ORCHESTRATING** に変化。
* Phase 1からPhase 6までのタイムラインがプログレッシブに進行し、バッジが「PROCESSING」から「COMPLETED」へ遷移。
* 進行中、**エージェントログ（Orchestrator Log）**と**ステークホルダーの議論チャット（Discovery Chat）**がまるで本当に裏側でAIエージェントが動作しているかのように、タイムスタンプ付きで滑らかに出力・スクロールされます。

### 5. 【完全網羅】サイト内インラインMarkdown & テーブルレンダラー
* 自作のMarkdownパーサーを `app.js` に実装し、以下の複雑なフォーマットをサイト内で美しくパース・描画します。
  * **ペルソナ全属性 & 会議対話録（完全網羅）**: H1〜H6のすべてのペルソナ詳細定義と、エージェント同士が戦わせた3つのインタビューセッションの全セリフを分離・並列表示でインライン閲覧可能。
  * **ワークショップ成果物**: ストーリーマップやリスク、暗黙要求などを整理した統合成果物。
  * **要求定義 & ユーザーストーリー（完全網羅）**: R-01〜R-19までのすべての要求を網羅した詳細な仕分けマトリクス表と、Given/When/Then形式のすべてのGherkin受入テスト仕様。
  * **自動化適性評価**: 7大観点からの各受入テストの自動化適性レビュー。
  * **自動テストコード & 詳細パスログ**: Playwrightスクリプトのコード、および実際に実行されたコンソール結果ログの完全版。
  * **POリリース判定**: 各要件に対するビジネス価値と最終リリース承認要件。
  * **品質特性 & メトリクス**: ISO 25010に基づく評価レポート。
  * **アラートボックス**: GitHubスタイルの NOTE / TIP / WARNING アラートを美麗な枠線とアイコンで描画。

### 6. Playwright テスト実行動画のインテグレーション
* テスト実行フェーズ完了後、Playwrightが実際に録画したテスト実行動画（ホテル予約システム用）がダッシュボード上で再生可能になります。

### 7. Chart.js を用いた品質メトリクスダッシュボード
* 最終フェーズにおいて、以下のメトリクスがアニメーション付きで豪華に表示されます。
  * **総合品質サマリー**: セキュリティ、インプットガード、ロックアウトなどの個別監査項目（PASS）の表示と総合パーセンテージ。
  * **品質特性レーダーチャート**: ISO 25010に基づく5軸評価。
  * **利用時品質 (UX)**: タスク完了率、SUSスコア換算、エラー削減率。
  * **自動化カバレッジ**: テストの成功率とカバー率のドーナツチャート。

---

## 起動および動作確認手順

1. ブラウザを起動し、以下のいずれかの方法で画面を開いてください。
   * **[http://localhost:8080](http://localhost:8080)** からアクセスする。
   * または、`index.html` ファイルをブラウザで**直接ダブルクリック**して開く。
2. 画面が開いた時点で、すでに全タブにすべての成果物ドキュメントが省略なしでインライン描画されています。
3. 高木、高橋、上田のチェックボックスを切り替えると、実行ボタンを押さなくても成果物の中身（ペルソナやインタビュー対話録）がその場でリアルタイムに動的に絞り込まれます。
4. 画面左上のプリセットボタンからお好みのシナリオを選択し、フォームの内容を確認します。
5. **「ATDDプロセスを実行する」** ボタンをクリックすると、右ペインの「ライブ実行プロセス」でエージェント対話がスタートします。
6. プロセスがすべて完了したら、各タブを切り替えて成果物を確認してください。
