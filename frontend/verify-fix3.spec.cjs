const { test, expect } = require('@playwright/test');

test.describe('Verify Fix 3', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Check vessels source exists in map', async ({ page }) => {
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

    // Check maplibre map via canvas
    const mapData = await page.evaluate(() => {
      const canvas = document.querySelector('canvas.maplibre-canvas');
      if (!canvas) return { error: 'No canvas' };

      // The map instance is attached to the canvas by maplibre
      // Try various ways to access it
      let map = null;
      if (canvas._map) map = canvas._map;
      else if (canvas.__map) map = canvas.__map;
      else if (canvas._eventedParent) map = canvas._eventedParent;

      if (!map && window.maplibregl && window.maplibregl._maps) {
        const keys = Object.keys(window.maplibregl._maps);
        if (keys.length > 0) map = window.maplibregl._maps[keys[0]];
      }

      if (!map) return { error: 'No map found', canvasProps: Object.keys(canvas) };

      const style = map.getStyle();
      const sources = {};
      if (style && style.sources) {
        Object.keys(style.sources).forEach(key => {
          sources[key] = { type: style.sources[key].type, _data: style.sources[key]._data ? 'has _data' : 'no _data' };
        });
      }

      // Check vessels source
      let vesselsData = 'NOT FOUND';
      if (map.getSource('vessels')) {
        const src = map.getSource('vessels');
        vesselsData = src._data?.features?.length || 0;
      }

      return { sources, vesselsData, layers: style?.layers?.map(l => l.id) || [] };
    });

    console.log('Map data:', JSON.stringify(mapData, null, 2));

    // Also check click handling by clicking on the map
    const mapContainer = page.locator('.globe-container');
    const box = await mapContainer.boundingBox();
    if (box) {
      // Click at center
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      await page.waitForTimeout(2000);
    }

    // Check investigation panel
    const panel = page.locator('.vessel-investigation-panel');
    const isVisible = await panel.isVisible().catch(() => false);
    console.log('Panel visible after click:', isVisible);

    if (isVisible) {
      const panelText = await panel.textContent();
      console.log('Panel text (first 500):', panelText.substring(0, 500));
    }
  });
});