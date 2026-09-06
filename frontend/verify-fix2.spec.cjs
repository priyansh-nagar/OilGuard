const { test, expect } = require('@playwright/test');

test.describe('Verify Fix 2', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  test('Backend vessels rendered and clickable', async ({ page }) => {
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

    // Check HTML for vessel circle markers (not DOM markers)
    const globeHTML = await page.locator('.globe-container').innerHTML();
    console.log('Globe HTML (first 3000 chars):', globeHTML.substring(0, 3000));

    // Look for maplibre circle markers in the HTML
    const hasVesselCircles = globeHTML.includes('maplibregl-marker') ||
                              globeHTML.includes('vessels') ||
                              globeHTML.includes('circle');
    console.log('Has vessel markers:', hasVesselCircles);

    // Check for prototype DOM markers (should be removed when real vessels exist)
    const protoMarkers = await page.locator('.prototype-vessel-marker').count();
    console.log('Prototype DOM markers:', protoMarkers);

    // Try to click on map and see if investigation panel opens with real vessel data
    const mapContainer = page.locator('.globe-container');
    const box = await mapContainer.boundingBox();
    if (box) {
      // Click near center where real vessels should be
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      await page.waitForTimeout(2000);
    }

    // Check investigation panel
    const panel = page.locator('.vessel-investigation-panel');
    const isVisible = await panel.isVisible().catch(() => false);
    console.log('Panel visible:', isVisible);

    if (isVisible) {
      const panelText = await panel.textContent();
      console.log('Panel text (first 300):', panelText.substring(0, 300));

      // Check if it shows real vessel data (not PROTOTYPE-)
      const hasRealVessel = panelText.includes('MV Ocean Pioneer') ||
                            panelText.includes('MT Gulf Harmony') ||
                            panelText.includes('FV Sagar Kiran');
      console.log('Has real vessel data:', hasRealVessel);
    }
  });
});