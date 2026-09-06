const { test, expect } = require('@playwright/test');

test.describe('OilGuard Debug 3', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Debug: Check map source directly', async ({ page }) => {
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

    // Check map by accessing the React component's map ref via canvas
    const mapInfo = await page.evaluate(() => {
      // Find the maplibre canvas
      const canvas = document.querySelector('canvas.maplibre-gl-canvas') || document.querySelector('.globe-container canvas');
      if (!canvas) return { error: 'No canvas found' };

      // The map instance is typically stored on the canvas or in a global
      // Try to get it from the canvas
      const map = canvas._map || canvas.__map;
      if (!map) {
        // Try to find it via maplibregl
        if (window.maplibregl && window.maplibregl._maps) {
          const keys = Object.keys(window.maplibregl._maps);
          if (keys.length > 0) {
            const m = window.maplibregl._maps[keys[0]];
            return checkMapSources(m);
          }
        }
        return { error: 'No map instance found on canvas', canvasKeys: Object.keys(canvas).filter(k => k.includes('map')) };
      }

      return checkMapSources(map);
    });

    console.log('Map info:', JSON.stringify(mapInfo, null, 2));

    function checkMapSources(map) {
      const sources = {};
      const style = map.getStyle();
      if (style && style.sources) {
        Object.keys(style.sources).forEach(key => {
          sources[key] = style.sources[key].type;
        });
      }

      // Check vessels source data
      let vesselsData = 'NOT FOUND';
      if (map.getSource('vessels')) {
        const src = map.getSource('vessels');
        vesselsData = src._data?.features?.length || 0;
      }

      // Check layers
      const layers = style?.layers?.map(l => l.id) || [];

      return { sources, vesselsData, layers };
    }

    // Also check the GlobeContainer component directly
    const globeInfo = await page.evaluate(() => {
      const container = document.querySelector('.globe-container');
      if (!container) return { error: 'No globe container' };

      // Check if map is attached to container
      return {
        hasMap: !!container.__map,
        mapKeys: container.__map ? Object.keys(container.__map).slice(0, 20) : [],
        children: container.children.length
      };
    });

    console.log('Globe info:', JSON.stringify(globeInfo, null, 2));

    // Check if there's a click handler on the map
    const clickTest = await page.evaluate(() => {
      const canvas = document.querySelector('canvas.maplibre-gl-canvas');
      if (!canvas) return { error: 'No canvas' };
      return {
        canvasWidth: canvas.width,
        canvasHeight: canvas.height,
        listeners: canvas._events ? Object.keys(canvas._events) : 'no _events'
      };
    });

    console.log('Canvas info:', JSON.stringify(clickTest, null, 2));
  });
});