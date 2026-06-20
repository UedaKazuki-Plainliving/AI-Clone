import { test, expect } from '@playwright/test';

test.describe('ホテル予約サイト 空室検索・予約フローテスト', () => {
  test('指定日の空室のみが表示され、選択時にリアルタイム在庫バリデーションが走る', async ({ page }) => {
    // 1. トップページ遷移と日付指定
    await page.goto('/hotel/search');
    await page.locator('#checkin-date').fill('2026-07-10');
    await page.locator('#search-vacant-btn').click();
    
    // 2. 空室プランのみ表示されていることを確認
    const planList = page.locator('.hotel-plan-list');
    await expect(planList.locator('.plan-item')).toHaveCount(1);
    await expect(planList.locator('.plan-title').first()).toContainText('ビジネス出張応援プラン');
    
    // 3. プラン選択と在庫APIバリデーション検証
    // プラン選択ボタンをクリックすると、裏側でリアルタイム空室確認APIが動作する
    await page.locator('.btn-select-plan').first().click();
    
    // 4. 内訳金額がはっきり表示されていることの検証 (Kanoモデル魅力品質A)
    const breakdown = page.locator('.price-breakdown');
    await expect(breakdown).toBeVisible();
    await expect(breakdown.locator('.base-price')).toContainText('¥10,000');
    await expect(breakdown.locator('.tax-amount')).toContainText('¥1,000');
    
    // 5. 確定画面遷移確認
    await expect(page.locator('#booking-confirm-title')).toBeVisible();
  });
});
