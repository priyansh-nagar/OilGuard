const { test, expect } = require('@playwright/test');

test.describe('OilGuard Debug 2', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Debug: Check map access and vessel data', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Upload and analyze
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(CLASS1_IMAGE);
    await page.waitForTimeout(500);

    const analyzeBtn = page.locator('button.sar-analyze-btn, button:has-text("ANALYZE SAR SCENE")');
    await analyzeBtn.waitFor({ state: 'visible', timeout: 5000 });
    await analyzeBtn.click();

    await page.waitForTimeout(8000);

    // Try to access map via maplibre-gl instance on window
    const mapInfo = await page.evaluate(() => {
      // Check if maplibre map is on window
      if (window.map) return { map: 'window.map', sources: Object.keys(window.map.getStyle().sources) };

      // Check all elements with maplibre map
      const canvas = document.querySelector('.maplibre-gl-canvas');
      if (canvas && canvas._map) {
        const map = canvas._map;
        return {
          map: 'canvas._map',
          sources: Object.keys(map.getStyle().sources),
          vesselsSource: map.getSource('vessels') ? 'exists' : 'missing',
          vesselsData: map.getSource('vessels')?._data?.features?.length || 0
        };
      }

      // Try to get map from maplibre global
      if (window.maplibregl && window.maplibregl._maps) {
        const maps = window.maplibregl._maps;
        return { maps: Object.keys(maps) };
      }

      return { error: 'No map access found' };
    });

    console.log('Map info:', JSON.stringify(mapInfo, null, 2));

    // Check the sidebar for candidate vessels (LeftSidebar might show them)
    const sidebarText = await page.locator('.left-sidebar').textContent();
    console.log('Sidebar text:', sidebarText);

    // Check the detection HUD for vessel info
    const detectionText = await page.locator('.detection-hud').textContent();
    console.log('Detection HUD:', detectionText);

    // Check if there's a candidate list anywhere
    const allText = await page.locator('body').textContent();
    const hasMV = allText.includes('MV Ocean Pioneer');
    const hasMT = allText.includes('MT Gulf Harmony');
    const hasFV = allText.includes('FV Sagar Kiran');
    console.log('Has MV Ocean Pioneer:', hasMV);
    console.log('Has MT Gulf Harmony:', hasMT);
    console.log('Has FV Sagar Kiran:', hasFV);

    // Check investigation panel visibility
    const panelVisible = await page.locator('.vessel-investigation-panel').isVisible();
    console.log('Panel visible:', panelVisible);
  });
});