const { test, expect } = require('@playwright/test');

test.describe('OilGuard Debug 7', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Debug: Check file upload without interception', async ({ page }) => {
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

    // Check detection HUD for results
    const detectionText = await page.locator('.detection-hud').textContent();
    console.log('Detection HUD:', detectionText);

    // The detection worked before, so API is getting the image
    // Now check the globe for vessels
    const globeInfo = await page.evaluate(() => {
      const container = document.querySelector('.globe-container');
      if (!container) return { error: 'No container' };

      // Try to access the React component's map ref
      // Check if there's a map on the container
      const keys = Object.keys(container);
      const mapKey = keys.find(k => k.startsWith('__reactProps') || k.startsWith('__reactInternalInstance') || k === '__map' || k === '_map');
      return { keys: keys.slice(0, 20), mapKey };
    });

    console.log('Globe info:', JSON.stringify(globeInfo, null, 2));
  });
});