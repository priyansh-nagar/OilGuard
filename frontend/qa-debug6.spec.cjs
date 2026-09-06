const { test, expect } = require('@playwright/test');

test.describe('OilGuard Debug 6', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Debug: Upload with network interception', async ({ page }) => {
    let apiResponse = null;

    await page.route('**/api/analyze', async route => {
      const response = await route.fetch();
      apiResponse = await response.json();
      route.continue();
    });

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Upload and analyze
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(CLASS1_IMAGE);
    await page.waitForTimeout(500);

    const analyzeBtn = page.locator('button.sar-analyze-btn, button:has-text("ANALYZE SAR SCENE")');
    await analyzeBtn.waitFor({ state: 'visible', timeout: 5000 });
    await analyzeBtn.click();

    await page.waitForTimeout(10000);

    console.log('API Response captured:', JSON.stringify(apiResponse, null, 2));

    // Check if result has candidates
    if (apiResponse && apiResponse.candidates) {
      console.log('Candidates count:', apiResponse.candidates.length);
      apiResponse.candidates.forEach((c, i) => {
        console.log(`  ${i}: ${c.name} (${c.vessel_id}) - score: ${c.attribution_score}`);
      });
    }
  });
});