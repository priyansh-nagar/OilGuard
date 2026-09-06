const { test, expect } = require('@playwright/test');

test.describe('OilGuard Debug 4', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Debug: Check HTML structure', async ({ page }) => {
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

    // Get full HTML structure of globe area
    const html = await page.locator('.globe-wrapper').innerHTML();
    console.log('Globe wrapper HTML:', html.substring(0, 2000));

    // Check for canvas elements
    const canvases = await page.locator('canvas').count();
    console.log('Canvas count:', canvases);

    for (let i = 0; i < canvases; i++) {
      const canvas = page.locator('canvas').nth(i);
      const className = await canvas.getAttribute('class');
      const width = await canvas.getAttribute('width');
      const height = await canvas.getAttribute('height');
      console.log(`Canvas ${i}: class=${className}, width=${width}, height=${height}`);
    }

    // Check globe-container
    const globeContainer = await page.locator('.globe-container').innerHTML();
    console.log('Globe container innerHTML:', globeContainer.substring(0, 1000));

    // Check if maplibre CSS is loaded
    const stylesheets = await page.evaluate(() => {
      return Array.from(document.styleSheets).map(s => s.href).filter(h => h);
    });
    console.log('Stylesheets:', stylesheets);
  });
});