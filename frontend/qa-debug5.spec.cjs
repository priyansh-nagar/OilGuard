const { test, expect } = require('@playwright/test');

test.describe('OilGuard Debug 5', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Debug: Check if result state has candidates', async ({ page }) => {
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

    // Check the React component state by looking at the App component
    const appState = await page.evaluate(() => {
      // Find the root React fiber
      const root = document.querySelector('#root') || document.querySelector('[data-reactroot]');
      if (!root) return { error: 'No root' };

      // Try to access React internals
      const fiber = root._reactRootContainer || root._reactInternals;
      if (!fiber) return { error: 'No fiber' };

      // This is very hacky but let's try
      return { fiberKeys: Object.keys(fiber).slice(0, 10) };
    });

    console.log('App state:', JSON.stringify(appState, null, 2));

    // Check the network requests to see what the API returned
    const networkData = await page.evaluate(() => {
      return window.__OILGUARD_API_RESPONSE || 'not captured';
    });
    console.log('Network data:', networkData);

    // Let's intercept the API call
    await page.route('**/api/analyze', async route => {
      const response = await route.fetch();
      const body = await response.json();
      console.log('API Response:', JSON.stringify(body, null, 2));
      route.continue();
    });

    // Reload and test again
    await page.reload();
    await page.waitForLoadState('networkidle');

    await fileInput.setInputFiles(CLASS1_IMAGE);
    await page.waitForTimeout(500);
    await analyzeBtn.click();
    await page.waitForTimeout(10000);
  });
});