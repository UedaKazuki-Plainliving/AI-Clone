const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 1024 });

  page.on('pageerror', exception => {
    console.error(`[BROWSER ERROR DETAIL] ${exception.stack || exception.toString()}`);
  });

  page.on('console', message => {
    console.log(`[BROWSER CONSOLE] [${message.type()}] ${message.text()}`);
  });

  page.on('dialog', async dialog => {
    console.log(`[BROWSER DIALOG] [${dialog.type()}] ${dialog.message()}`);
    await dialog.dismiss();
  });

  try {
    console.log("Navigating to http://localhost:8001/ ...");
    await page.goto('http://localhost:8001/');
    await page.waitForTimeout(2000);

    // Verify input fields are present and empty by default
    const sysName = await page.inputValue('#system-name');
    const surveyText = await page.inputValue('#survey-input');
    console.log(`Initial system name: "${sysName}" (Expected: "")`);
    console.log(`Initial survey text: "${surveyText}" (Expected: "")`);

    // Fill with custom zoo values
    console.log("Filling system name and survey text...");
    await page.fill('#system-name', '動物園予約システム');
    
    const surveyContent = `
お名前：吉田花子
年齢：32歳
役割：一般ユーザー
ITリテラシー：中
イラっとした出来事 →（スマホからチケットを事前購入しようとしたが、大人と子供の人数を間違えて選択した際に、決済完了前に警告メッセージがなく、そのまま間違った金額で決済されてしまった。）
まっ先に直したいことは？ →（決済完了の直前ステップで、購入するチケットの種類と合計金額を大きく確認表示し、誤りがないか最終確認ダイアログを表示してほしい。）
`;
    await page.fill('#survey-input', surveyContent.trim());

    // Run simulation
    console.log("Clicking '🧬 シミュレーションを実行' button...");
    await page.click('#btn-run-simulation');

    // Wait for the navigation to change or for a spinner to disappear.
    // The original app.js does:
    // document.getElementById('nav-clones').click();
    // when it completes. So the active nav item will be '#nav-clones'!
    console.log("Waiting for simulation to complete...");
    let completed = false;
    for (let i = 0; i < 30; i++) {
      await page.waitForTimeout(1000);
      const isClonesActive = await page.locator('#nav-clones').evaluate(el => el.classList.contains('active'));
      if (isClonesActive) {
        console.log(`Simulation completed successfully after ${i} seconds!`);
        completed = true;
        break;
      }
    }

    if (!completed) {
      throw new Error("Simulation timed out or failed to complete.");
    }

    // Take screenshot of results page
    const screenshotPath = 'C:/Users/plain/.gemini/antigravity/brain/752de375-5841-460e-a77e-ed98142b0ce3/original_simulation_result_ui.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`Screenshot saved to ${screenshotPath}`);

  } catch (error) {
    console.error("Simulation verification failed:", error);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
