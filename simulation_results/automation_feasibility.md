# 自動化実現性分析報告書 (automation_feasibility.md)

自動化エンジニアクローンによる、ホテル予約サイトにおける Playwright テスト自動化の実現性検証結果です。

---

## 📊 自動化評価マトリクス

| 評価項目 | 判定 | 評価詳細・課題点 |
| :--- | :---: | :--- |
| **ロケーター (Selectors)** | **○** | 日付入力フィールド（`#checkin-date`）や検索ボタン（`#search-vacant-btn`）は標準的なID指定で動作可能。ただしプラン一覧の要素は動的描画（PMSからのAPI応答後）となるため、`.plan-item` の `waitFor` 処理を明示的に組み込む必要がある。 |
| **手順の明確化** | **○** | 選択時のリアルタイム照会APIの遅延があるため、API送信からローディングスピナーが消えるまで待機し、その後に価格内訳のアサーションを行うフロー設計が必須。 |
| **前提条件とデータ** | **△** | テスト対象日に実際に空室がある状態を作るため、ホテル在庫システム（PMSモック）へテスト実行前に初期シードデータ（2026年7月10日の在庫残数 > 0）を登録する仕組みが必須。 |
| **総合判定** | **実装可能 (Feasible)** | PMS（在庫管理）と価格計算エンジンのモック環境、およびテスト前データクリアスクリプトを用意すれば、100%安定した自動化テストが実装できる。 |

---

## 🛠 Playwright実装時のベストプラクティス提案

1.  **非同期描画のハンドリング**:
    ```javascript
    // プルダウンやリストが非同期でAPIから読込まれるのを待つ
    await page.locator('.plan-item').first().waitFor({ state: 'visible', timeout: 5000 });
    ```
2.  **外部満室チェックAPIのモック化**:
    サードパーティPMSとの直接連携は接続状況によりテストが不安定になるため、テスト環境ではAPIをインターセプトしてモックレスポンス（空室あり）を返却させる。
    ```javascript
    await page.route('**/api/v1/availability/*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ available: true, remaining: 3 })
      });
    });
    ```
