import { test, expect } from '@playwright/test';

test.describe('ホテル予約サイト 品質向上ATDD受入テスト (US-01 〜 US-10)', () => {

  // US-01: 宿泊日指定による空室プランのダイレクト絞り込み
  test('US-01: 指定した宿泊日に実際に予約可能なプランのみが表示されること', async ({ page }) => {
    await page.goto('/hotel/search');
    await page.locator('#checkin-date').fill('2026-07-10');
    await page.locator('#search-vacant-btn').click();
    
    // 空室のあるプランのみが表示されることを検証
    const planList = page.locator('.hotel-plan-list');
    await expect(planList.locator('.plan-item')).toHaveCount(1);
    await expect(planList.locator('.plan-title').first()).toContainText('ビジネス出張応援プラン');
    // 満室プランが非表示または選択不可であることを検証
    await expect(planList.locator('.plan-item-disabled')).toBeHidden();
  });

  // US-02: 旅費規程上限（1万円）の事前ガードロック
  test('US-02: 旅費規程チェックボックスを有効化し、上限超えのプランの選択をガードする', async ({ page }) => {
    await page.goto('/hotel/search');
    // 出張モード（上限自動ロック）を有効化
    await page.locator('#limit-lock-checkbox').check();
    await page.locator('#checkin-date').fill('2026-07-10');
    await page.locator('#search-vacant-btn').click();

    // 10,001円以上の高額プランの選択ボタンが非活性化されていること
    const expensivePlanBtn = page.locator('.plan-item:has-text("スイートルーム特別プラン") .btn-select-plan');
    await expect(expensivePlanBtn).toBeDisabled();
    // 警告バッジが表示されていること
    await expect(page.locator('.limit-warning-badge').first()).toBeVisible();
    await expect(page.locator('.limit-warning-badge').first()).toContainText('旅費規程上限オーバー');
  });

  // US-03: 会社宛電子領収書の事前指定とコーポレート決済自動連携
  test('US-03: 予約完了時に会社宛ての電子領収書PDFをプレビューし自動発行する', async ({ page }) => {
    await page.goto('/hotel/booking');
    // 支払オプションでコーポレート決済を選択
    await page.locator('#payment-corporate').check();
    // 宛名入力
    await page.locator('#receipt-company-name').fill('プレインリビング株式会社');
    
    // 予約を確定
    await page.locator('#booking-submit-btn').click();
    
    // 完了表示と領収書Noの検証
    await expect(page.locator('#receipt-no')).toContainText('RC-101');
    
    // PDFダウンロードイベントの監視
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#receipt-download-link').click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('receipt_RC-101.pdf');
  });

  // US-04: 暗号化LocalStorageによる自動ドラフト保存と2時間自動消去
  test('US-04: 入力途中でブラウザが強制終了した場合、再開時にドラフトデータから復元されること', async ({ page, context }) => {
    await page.goto('/hotel/booking');
    await page.locator('#guest-name').fill('田中 一郎');
    await page.locator('#guest-phone').fill('090-9999-9999');
    
    // 5秒経過を待つ代わりにLocalStorageの書き込みをチェック
    const draftData = await page.evaluate(() => localStorage.getItem('draft_booking'));
    expect(draftData).not.toBeNull();
    // 暗号化されていることを検証（平文でないこと）
    expect(draftData).not.toContain('田中 一郎');
    
    // ブラウザタブを閉じて再アクセス
    const newPage = await context.newPage();
    await newPage.goto('/hotel/booking');
    
    // 復元ダイアログの表示と復元実行
    await expect(newPage.locator('#restore-draft-dialog')).toBeVisible();
    await newPage.locator('#restore-confirm-btn').click();
    
    // 入力値が復元されていることの検証
    await expect(newPage.locator('#guest-name')).toHaveValue('田中 一郎');
    await expect(newPage.locator('#guest-phone')).toHaveValue('090-9999-9999');
  });

  // US-05: 共用PC検知時の自動保存機能強制ブロック
  test('US-05: 共有PCチェックボックスがオンの場合、LocalStorageへの書き込みを完全に無効化する', async ({ page }) => {
    await page.goto('/hotel/booking');
    // 共有PCチェックを入れる
    await page.locator('#shared-pc-checkbox').check();
    await page.locator('#guest-name').fill('田中 一郎');
    
    // LocalStorageにドラフトが書き込まれていないことを検証
    const draftData = await page.evaluate(() => localStorage.getItem('draft_booking'));
    expect(draftData).toBeNull();
  });

  // US-06: 5分有効期限SMS認証とWebOTPによる1タップ自動入力
  test('US-06: ログイン時にSMS認証コードが送信され、WebOTP APIを介して1タップで自動入力されること', async ({ page }) => {
    await page.goto('/hotel/login');
    await page.locator('#login-phone').fill('090-1234-5678');
    await page.locator('#send-otp-btn').click();
    
    // WebOTP APIのモック設定
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'credentials', {
        value: {
          get: async () => ({
            code: '4321'
          })
        }
      });
    });
    
    // OTP入力欄に自動転記されたことを検証
    await expect(page.locator('#otp-input')).toHaveValue('4321');
    await page.locator('#verify-otp-btn').click();
    await expect(page.locator('#login-status')).toContainText('ログイン完了');
  });

  // US-07: ブラウザ標準機能を利用したA4しおり印刷専用CSS（@media print）最適化
  test('US-07: 予約完了画面を印刷した際、余計なヘッダーや広告が消え、しおりが極大フォントでA4横1枚に収まること', async ({ page }) => {
    await page.goto('/hotel/booking/complete');
    
    // 印刷メディアのエミュレート
    await page.emulateMedia({ media: 'print' });
    
    // ヘッダーやサイドバーが非表示になっていることを検証
    const header = page.locator('.site-header');
    const footer = page.locator('.site-footer');
    await expect(header).toHaveCSS('display', 'none');
    await expect(footer).toHaveCSS('display', 'none');
    
    // しおり情報が極大フォント（30px以上）であることを検証
    const printTitle = page.locator('.print-large-text');
    const fontSize = await printTitle.evaluate(el => window.getComputedStyle(el).fontSize);
    const fontSizePx = parseFloat(fontSize);
    expect(fontSizePx).toBeGreaterThanOrEqual(30);
  });

  // US-08: 誤タップ防止のための2秒長押し確定（ホールド）決済ボタン
  test('US-08: 確定ボタンを2秒間ホールドし続け、プログレスバーが100%に達した際のみ決済が実行されること', async ({ page }) => {
    await page.goto('/hotel/booking');
    const confirmBtn = page.locator('#hold-confirm-btn');
    
    // 1. 単なるクリック（短押し）では確定しないこと
    await confirmBtn.click();
    await expect(confirmBtn).not.toHaveAttribute('data-status', 'confirmed');
    
    // 2. 2秒間ホールド（mousedownのシミュレート）
    const box = await confirmBtn.boundingBox();
    expect(box).not.toBeNull();
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      // プログレスバーが進行することを監視
      await expect(confirmBtn).toHaveAttribute('aria-valuenow', '100');
      await page.mouse.up();
    }
    
    // 確定状態への遷移を検証
    await expect(confirmBtn).toHaveAttribute('data-status', 'confirmed');
  });

  // US-09: 厨房アレルギー重要フラグ連携とハートビート同期監視
  test('US-09: 予約時にアレルギー要望を入力し、厨房管理システムへハートビート監視下でデータ同期されること', async ({ page }) => {
    // 厨房同期APIがエラーを返すようにモック化
    await page.route('**/api/kitchen/sync-status', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Sync Failed' })
      });
    });
    
    await page.goto('/hotel/staff/dashboard');
    
    // 同期エラーにより、アレルギー未同期警告アラートが画面に赤色で点滅表示されていること
    const syncAlert = page.locator('#allergy-sync-alert');
    await expect(syncAlert).toBeVisible();
    await expect(syncAlert).toHaveClass(/blink-red/);
  });

  // US-10: 4桁一時共有コードによるコールセンター簡易電話セッション引き継ぎ
  test('US-10: 入力途中画面で電話サポートをリクエストし、生成された4桁コードでスタッフに情報を引き継ぐ', async ({ page, context }) => {
    // 1. ユーザー画面で入力
    await page.goto('/hotel/booking');
    await page.locator('#guest-smoke-preference').selectOption('禁煙');
    await page.locator('#guest-request-elevator').check();
    
    // 引き継ぎコード生成
    await page.locator('#phone-transfer-btn').click();
    await expect(page.locator('#transfer-code-display')).toBeVisible();
    const code = await page.locator('#transfer-code-display').innerText();
    expect(code).toMatch(/^\d{4}$/); // 4桁の数字
    
    // 2. スタッフ画面で引き継ぎコードを入力
    const staffPage = await context.newPage();
    await staffPage.goto('/hotel/staff/transfer');
    await staffPage.locator('#staff-code-input').fill(code);
    await staffPage.locator('#staff-load-btn').click();
    
    // スタッフ画面にユーザーの入力がロードされていることの検証
    await expect(staffPage.locator('#staff-smoke-preference')).toHaveValue('禁煙');
    await expect(staffPage.locator('#staff-request-elevator')).toBeChecked();
  });

});
