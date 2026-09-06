const { test, expect } = require('@playwright/test');

test.describe('Verify Fix', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Backend vessels rendered on globe', async ({ page }) => {
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

    // Check map for vessels source
    const mapInfo = await page.evaluate(() => {
      const container = document.querySelector('.globe-container');
      if (!container) return { error: 'No container' };

      const fiberKey = Object.keys(container).find(k => k.startsWith('__reactFiber'));
      const propsKey = Object.keys(container).find(k => k.startsWith('__reactProps'));

      if (!fiberKey) return { error: 'No fiber' };

      const fiber = container[fiberKey];
      // Traverse to find the GlobeContainer fiber
      let current = fiber;
      let globeFiber = null;
      while (current) {
        if (current.type && current.type.name === 'GlobeContainer') {
          globeFiber = current;
          break;
        }
        current = current.return;
      }

      if (!globeFiber) return { error: 'No GlobeContainer fiber' };

      return {
        mapExists: !!globeFiber.memoizedState,
        mapKeys: globeFiber.memoizedState ? Object.keys(globeFiber.memoizedState) : []
      };
    });

    console.log('Map info:', JSON.stringify(mapInfo, null, 2));

    // Check maplibre map directly
    const mapData = await page.evaluate(() => {
      const canvas = document.querySelector('canvas.maplibre-canvas');
      if (!canvas) return { error: 'No canvas' };

      // Try to access map via the canvas's _map or __map
      const map = canvas._map || canvas.__map;
      if (!map) {
        // Try maplibregl global
        if (window.maplibregl && window.maplibregl._maps) {
          const keys = Object.keys(window.maplibregl._maps);
          if (keys.length > 0) {
            return checkMap(window.maplibregl._maps[keys[0]]);
          }
        }
        return { error: 'No map on canvas' };
      }

      return checkMap(map);
    });

    console.log('Map data:', JSON.stringify(mapData, null, 2));

    function checkMap(map) {
      const sources = {};
      const style = map.getStyle();
      if (style && style.sources) {
        Object.keys(style.sources).forEach(key => {
          sources[key] = style.sources[key].type;
        });
      }

      let vesselsData = 'NOT FOUND';
      if (map.getSource('vessels')) {
        const src = map.getSource('vessels');
        vesselsData = src._data?.features?.length || 0;
      }

      return { sources, vesselsData, layers: style?.layers?.map(l => l.id) || [] };
    }

    // Check detection HUD
    const detectionText = await page.locator('.detection-hud').textContent();
    console.log('Detection HUD:', detectionText);
  });
});