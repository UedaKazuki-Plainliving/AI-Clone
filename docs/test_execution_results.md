# 自動テスト実行結果レポート（test_execution_results.md）

対象システム：**HOTEL PLANISPHERE** & **ローカルモック予約システム**

本ドキュメントは、ATDDスキル（Phase 6）に基づき、既存テストスイートおよび新規に実装された品質・セキュリティ機能に対する全8つの自動テストを一括実行した結果のログです。

---

## 1. テスト実行概要

* **実行日時**: 2026-06-20 19:56:38 (ローカル時間)
* **実行環境**: Windows 11 / PowerShell / Desktop Chrome (Chromium)
* **テストフレームワーク**: Playwright v1.x
* **実行コマンド**: `npx playwright test`

---

## 2. 実行結果サマリー

| テストファイル | テストケースID / シナリオ名 | 対象環境 | ステータス | 実行時間 | アサーション検証内容 |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `booking.spec.js` | **TC-B1** / 出張検索〜事前決済〜領収書ダウンロード (正常系) | ローカルモック | **PASS** | - | 宛名「株式会社テストコーポレーション」、金額「¥9,000」を含む領収書HTML表示 |
| `booking.spec.js` | **TC-B2** / 最後の1室に対する同時決済 (排他制御・異常系) | ローカルモック | **PASS** | - | 在庫0衝突時にエラーメッセージ「お部屋をご用意できませんでした」が表示されること |
| `booking.spec.js` | **TC-B3** / 決済確定ボタンの連打 (二重決済防止) | ローカルモック | **PASS** | - | 連打時に2回目の送信がブロックされ、リクエストカウンターが1であることを確認 |
| `live_site_booking.spec.js` | **TC-L1** / ビジネスプラン通常ゲスト予約 | 実サイト | **PASS** | 3.1s | 実サイト料金(7,500円)の一致、完了モーダル表示 |
| `live_site_booking.spec.js` | **TC-L2** / 入力不備バリデーション | 実サイト | **PASS** | 1.6s | 名前の必須エラー、電話番号形式エラーのアサート |
| `local_input_guard.spec.js` | **TC-I1** / 全角・スペース・ハイフン混じりの自動補正 (R-17) | ローカルモック | **PASS** | 5.1s | 補正後のメールアドレス `shota@example.com` のトリム結果の検証 |
| `verify_receipt.spec.js` | **TC-V1** / 真正性照合と個人情報保護 (R-16/19 正常系) | ローカルモック | **PASS** | 5.5s | 正しいPINコードでの照合成功、および表示項目から宿泊者名「健二」が排除されていること |
| `verify_receipt.spec.js` | **TC-V2** / 3回PIN入力誤りでのセキュリティロック (R-16/19 異常系) | ローカルモック | **PASS** | 6.3s | 連続3回誤入力での24時間アクセス制限発動、制限中の送信拒否アサート |

* **テスト総数**: 8件
* **パス数**: 8件 (100% PASS)
* **リトライ回数**: 0回

---

## 3. テスト実行コンソールログ

```text
Running 8 tests using 1 worker

[1/8] [chromium] › tests\booking.spec.js:10:3 › ホテル予約システム ATDDテストシナリオ › 【Scenario B-1 & C-2】出張検索〜事前決済〜領収書PDFダウンロード（正常系）
[2/8] [chromium] › tests\booking.spec.js:59:3 › ホテル予約システム ATDDテストシナリオ › 【Scenario B-6】最後の1室に対する同時決済（排他制御・異常系）
[3/8] [chromium] › tests\booking.spec.js:103:3 › ホテル予約システム ATDDテストシナリオ › 【Scenario B-8】決済確定ボタンの連打（二重決済防止）
[4/8] [chromium] › tests\live_site_booking.spec.js:15:3 › 実サイト（HOTEL PLANISPHERE）に対する出張者クローンの予約シナリオ（Given-When-Then） › 【通常出張予約シナリオ】出張者健二がビジネスプランをゲスト予約する
[5/8] [chromium] › tests\live_site_booking.spec.js:68:3 › 実サイト（HOTEL PLANISPHERE）に対する出張者クローンの予約シナリオ（Given-When-Then） › 【入力不備バリデーションシナリオ】翔太が電話番号のハイフン等でエラーを出し自己解決する
[6/8] [chromium] › tests\local_input_guard.spec.js:5:3 › ローカルモック予約システムのインプットガード検証 (R-17) › 全角・スペース・ハイフン混じりの入力が自動クレンジング・トリムされること
[7/8] [chromium] › tests\verify_receipt.spec.js:5:3 › 領収書真正性照合とセキュリティロック機能の検証 (R-16/19) › 正常系: 予約完了後に領収書を発行し、PIN付き照合システムで真正性と個人情報保護を確認する
[8/8] [chromium] › tests\verify_receipt.spec.js:51:3 › 領収書真正性照合とセキュリティロック機能の検証 (R-16/19) › 異常系: 間違ったPINを3回入力した際、セキュリティロックが作動すること
  8 passed (27.0s)
```
