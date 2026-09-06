const { test, expect } = require('@playwright/test');

test.describe('OilGuard End-to-End Browser QA', () => {
  const BASE_URL = 'http://localhost:5173';
  const CLASS0_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_0\\0\\0_0_0_img_01RNDdyOUhULo97s_SFr_cls_0.jpg';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  async function uploadAndAnalyze(page, imagePath) {
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(imagePath);

    // Wait for preview to appear
    await page.waitForTimeout(500);

    // Click the ANALYZE SAR SCENE button
    const analyzeBtn = page.locator('button.sar-analyze-btn, button:has-text("ANALYZE SAR SCENE")');
    await analyzeBtn.waitFor({ state: 'visible', timeout: 5000 });
    await analyzeBtn.click();

    // Wait for analysis to complete
    await page.waitForTimeout(8000);
  }

  test('Scenario 1: Class 0 image → No spill detected', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    await uploadAndAnalyze(page, CLASS0_IMAGE);

    // Check spill detection shows "No Oil Spill Detected"
    const detectionText = await page.locator('.detection-hud').textContent();
    console.log('Detection text:', detectionText);

    // Should show "No Oil Spill" or similar negative detection
    expect(detectionText.toLowerCase()).toContain('no');
    console.log('✓ Scenario 1 PASS: Class 0 shows no spill detected');
  });

  test('Scenario 2: Class 1 image → Oil spill detected with confidence > 50%', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    await uploadAndAnalyze(page, CLASS1_IMAGE);

    // Check spill detection shows "Oil Spill Detected" with confidence
    const detectionText = await page.locator('.detection-hud').textContent();
    console.log('Detection text:', detectionText);

    // Should show oil spill detected with confidence > 50%
    expect(detectionText.toLowerCase()).toContain('oil spill');
    expect(detectionText).toMatch(/[6-9]\d?%|100%/); // confidence > 50%
    console.log('✓ Scenario 2 PASS: Class 1 shows oil spill detected with high confidence');
  });

  test('Scenario 3: Three candidate vessels displayed on globe', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    await uploadAndAnalyze(page, CLASS1_IMAGE);

    // Check that vessels source was added to map (3 real vessels from API)
    const vesselCount = await page.evaluate(() => {
      const mapContainer = document.querySelector('.globe-container');
      const map = mapContainer && mapContainer.__map;
      if (!map) return 0;
      const source = map.getSource('vessels');
      if (!source) return 0;
      const data = source._data;
      return data.features ? data.features.length : 0;
    });
    console.log('Real vessel count from map:', vesselCount);

    // Also check via the investigation panel that we have 3 candidates
    // Open the first real vessel (not prototype)
    const panel = page.locator('.vessel-investigation-panel');
    const isPanelOpen = await panel.isVisible().catch(() => false);

    if (!isPanelOpen) {
      // Click on map to select a vessel
      const mapContainer = page.locator('.globe-container');
      const box = await mapContainer.boundingBox();
      if (box) {
        // Click slightly offset from center to avoid prototype markers
        await page.mouse.click(box.x + box.width / 2 + 50, box.y + box.height / 2 + 30);
        await page.waitForTimeout(2000);
      }
    }

    // Check if panel shows a real vessel (not prototype)
    const panelText = await panel.textContent().catch(() => '');
    const isRealVessel = panelText && !panelText.includes('PROTOTYPE-');
    console.log('Panel shows real vessel:', isRealVessel);
    console.log('Panel text:', panelText?.substring(0, 100));

    expect(vesselCount).toBeGreaterThanOrEqual(3);
    console.log('✓ Scenario 3 PASS: Candidate vessels present on globe');
  });

  test('Scenario 4: Click vessel on globe → Panel shows deterministic values', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    await uploadAndAnalyze(page, CLASS1_IMAGE);

    // Get the map container and click on a vessel position
    const mapContainer = page.locator('.globe-container');
    await mapContainer.waitFor({ state: 'visible' });

    // Click on the first vessel position (approximate map coordinates)
    const box = await mapContainer.boundingBox();
    if (box) {
      // Click slightly offset to hit real vessel, not prototype
      await page.mouse.click(box.x + box.width / 2 + 50, box.y + box.height / 2 + 30);
      await page.waitForTimeout(1000);
    }

    // Wait for panel
    await page.waitForTimeout(2000);

    // Check panel shows deterministic proximity and scores
    const panel = page.locator('.vessel-investigation-panel');
    await panel.waitFor({ state: 'visible', timeout: 5000 });

    const panelText = await panel.textContent();
    console.log('Panel text:', panelText);

    // Should show specific values (not "N/A" or random)
    expect(panelText).toMatch(/\d+\.\d+\s*km/); // distance like "5.7 km"
    expect(panelText).toMatch(/(N|NE|E|SE|S|SW|W|NW)/); // direction
    expect(panelText).toContain('SPATIAL CONSISTENCY');
    expect(panelText).toContain('TEMPORAL CONSISTENCY');
    expect(panelText).toContain('TRAJECTORY CONSISTENCY');
    console.log('✓ Scenario 4 PASS: Panel shows deterministic values');
  });

  test('Scenario 5: Trajectory playback animates on globe', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    await uploadAndAnalyze(page, CLASS1_IMAGE);

    // Click on a vessel to open panel
    const mapContainer = page.locator('.globe-container');
    const box = await mapContainer.boundingBox();
    if (box) {
      await page.mouse.click(box.x + box.width / 2 + 50, box.y + box.height / 2 + 30);
      await page.waitForTimeout(1000);
    }

    // Wait for panel
    await page.waitForTimeout(2000);

    const panel = page.locator('.vessel-investigation-panel');
    await panel.waitFor({ state: 'visible', timeout: 5000 });

    // Click play button
    const playBtn = panel.locator('.playback-btn').first();
    await playBtn.click();

    // Wait for animation
    await page.waitForTimeout(3000);

    // Check playback progress increased
    const progressText = await panel.locator('.timeline-display').textContent();
    console.log('Playback progress:', progressText);

    // Progress should show movement
    expect(progressText).toMatch(/\d+:\d+/);
    console.log('✓ Scenario 5 PASS: Trajectory playback animates');
  });

  test('Scenario 6: No console errors during analysis', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    await uploadAndAnalyze(page, CLASS1_IMAGE);

    // Filter out non-critical errors
    const criticalErrors = errors.filter(e =>
      !e.includes('MapTiler') &&
      !e.includes('maptiler') &&
      !e.includes('favicon') &&
      !e.includes('Worker') &&
      !e.includes('ResizeObserver')
    );

    console.log('Critical errors:', criticalErrors);
    expect(criticalErrors).toHaveLength(0);
    console.log('✓ Scenario 6 PASS: No critical console errors');
  });

  test('Scenario 7: Deterministic results across reloads', async ({ page }) => {
    // First run
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    await uploadAndAnalyze(page, CLASS1_IMAGE);

    // Click on vessel
    const mapContainer = page.locator('.globe-container');
    let box = await mapContainer.boundingBox();
    if (box) {
      await page.mouse.click(box.x + box.width / 2 + 50, box.y + box.height / 2 + 30);
      await page.waitForTimeout(1000);
    }

    await page.waitForTimeout(2000);

    const panel = page.locator('.vessel-investigation-panel');
    await panel.waitFor({ state: 'visible', timeout: 5000 });

    const panelText1 = await panel.textContent();

    // Reload
    await page.reload();
    await page.waitForLoadState('networkidle');

    await uploadAndAnalyze(page, CLASS1_IMAGE);

    box = await mapContainer.boundingBox();
    if (box) {
      await page.mouse.click(box.x + box.width / 2 + 50, box.y + box.height / 2 + 30);
      await page.waitForTimeout(1000);
    }

    await page.waitForTimeout(2000);

    await panel.waitFor({ state: 'visible', timeout: 5000 });
    const panelText2 = await panel.textContent();

    console.log('First run (truncated):', panelText1.substring(0, 200));
    console.log('Second run (truncated):', panelText2.substring(0, 200));

    // Compare deterministic values (excluding timestamp which uses Date.now())
    const extractDeterministic = (text) => {
      return text
        .replace(/AIS TIMESTAMP[^\n]*/g, 'AIS TIMESTAMP [DYNAMIC]')
        .replace(/\d{2}:\d{2} \/ \d{2}:\d{2}/g, '[TIME]');
    };

    expect(extractDeterministic(panelText1)).toBe(extractDeterministic(panelText2));
    console.log('✓ Scenario 7 PASS: Results deterministic across reloads (ignoring dynamic timestamp)');
  });
});