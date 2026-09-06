const { test, expect } = require('@playwright/test');

test.describe('OilGuard Debug', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Debug: Check what vessels are rendered', async ({ page }) => {
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

    // Check all map sources and layers
    const mapInfo = await page.evaluate(() => {
      const mapContainer = document.querySelector('.globe-container');
      const map = mapContainer && mapContainer.__map;
      if (!map) return { error: 'No map found' };

      const sources = {};
      const layers = map.getStyle().layers.map(l => l.id);

      // Check vessels source
      const vesselsSource = map.getSource('vessels');
      if (vesselsSource) {
        sources.vessels = vesselsSource._data ? (vesselsSource._data.features ? vesselsSource._data.features.length : 'no features') : 'no _data';
      } else {
        sources.vessels = 'NOT FOUND';
      }

      // Check prototype-trajectories source
      const protoSource = map.getSource('prototype-trajectories');
      if (protoSource) {
        sources.prototypeTrajectories = protoSource._data ? (protoSource._data.features ? protoSource._data.features.length : 'no features') : 'no _data';
      } else {
        sources.prototypeTrajectories = 'NOT FOUND';
      }

      // Check spill-zone source
      const spillSource = map.getSource('spill-zone');
      if (spillSource) {
        sources.spillZone = spillSource._data ? 'has data' : 'no _data';
      } else {
        sources.spillZone = 'NOT FOUND';
      }

      return { layers, sources };
    });

    console.log('Map info:', JSON.stringify(mapInfo, null, 2));

    // Also check what the API returned
    const apiData = await page.evaluate(() => {
      // The result should be in React state, let's check if there's a global or window reference
      return window.__OILGUARD_RESULT || 'not found';
    });
    console.log('API data:', apiData);

    // Try to find the vessels via DOM (prototype markers)
    const protoMarkers = await page.locator('.prototype-vessel-marker').count();
    console.log('Prototype vessel markers:', protoMarkers);

    // Check the candidate vessel data from the API
    const result = await page.evaluate(() => {
      // Try to access React devtools or component state
      return document.querySelector('[data-reactroot]')?.innerHTML || 'no react root';
    });
    console.log('React root:', result);
  });
});