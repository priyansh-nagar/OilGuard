const { test, expect } = require('@playwright/test');

test.describe('OilGuard Debug 8', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Debug: Check React props for GlobeContainer', async ({ page }) => {
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

    // Access React props
    const globeProps = await page.evaluate(() => {
      const container = document.querySelector('.globe-container');
      if (!container) return { error: 'No container' };

      const fiberKey = Object.keys(container).find(k => k.startsWith('__reactFiber'));
      const propsKey = Object.keys(container).find(k => k.startsWith('__reactProps'));

      if (!fiberKey || !propsKey) return { error: 'No React keys' };

      const fiber = container[fiberKey];
      const props = container[propsKey];

      return {
        propsKeys: Object.keys(props),
        vessels: props.vessels,
        spillResult: props.spillResult,
        selectedVessel: props.selectedVessel,
        playbackProgress: props.playbackProgress,
        hasOnVesselSelect: !!props.onVesselSelect
      };
    });

    console.log('GlobeContainer props:', JSON.stringify(globeProps, null, 2));

    // Also check App component state
    const appProps = await page.evaluate(() => {
      // Find the root div
      const root = document.querySelector('.page') || document.querySelector('#root');
      if (!root) return { error: 'No root' };

      const fiberKey = Object.keys(root).find(k => k.startsWith('__reactFiber'));
      const propsKey = Object.keys(root).find(k => k.startsWith('__reactProps'));

      if (!fiberKey) return { error: 'No fiber key' };

      const fiber = root[fiberKey];
      // Try to get memoizedState
      return {
        memoizedState: fiber.memoizedState,
        alternate: fiber.alternate ? fiber.alternate.memoizedState : null
      };
    });

    console.log('App fiber:', JSON.stringify(appProps, null, 2));
  });
});