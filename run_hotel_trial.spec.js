import { test, expect } from '@playwright/test';

test.describe('HOTEL PLANISPHERE 既存サイト適合テスト', () => {
  test('宿泊プラン一覧画面での日付指定と空室プランのみの表示テスト', async ({ page }) => {
    // 1. プラン一覧ページに直接遷移
    await page.goto('https://hotel-example-site.takeyaqa.dev/ja/plans.html');
    
    // 2. ATDD基準: 日付入力フィールド (#checkin-date) にチェックイン日を入力しようとする
    // （※既存サイトには存在しないため、ここでタイムアウトエラーが発生するはずです）
    console.log("【テスト実行】宿泊日フィルター（#checkin-date）の検索を試みます...");
    const dateInput = page.locator('#checkin-date');
    
    try {
      await expect(dateInput).toBeVisible({ timeout: 5000 }); // 5秒でタイムアウトさせる
      await dateInput.fill('2026-07-10');
      
      // 3. 検索ボタンを押す
      await page.locator('#search-vacant-btn').click();
      
      // 4. プランが正しく絞り込まれたかアサーション
      const plans = page.locator('.plan-item');
      await expect(plans).toHaveCount(1);
    } catch (e) {
      console.error("【テスト失敗】予定通り、宿泊日フィルター (#checkin-date) がプラン一覧画面に存在しないため、検証に失敗しました。");
      throw e;
    }
  });
});
