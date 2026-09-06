const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  // Intercept API response
  let apiResponse = null;
  page.on('response', async (response) => {
    const url = response.url();
    if (url.includes('/api/analyze')) {
      try {
        apiResponse = await response.json();
        console.log('API Response captured');
      } catch (e) {
        console.log('Failed to parse API response:', e.message);
      }
    }
  });

  console.log('Navigating to OilGuard...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });

  // Upload and analyze
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(CLASS1_IMAGE);
  await page.waitForTimeout(500);

  const analyzeBtn = page.locator('button:has-text("ANALYZE SAR SCENE")');
  await analyzeBtn.click();

  console.log('Waiting for API response...');
  await page.waitForTimeout(12000);

  if (apiResponse) {
    console.log('\n=== API Response Structure ===');
    console.log('Keys:', Object.keys(apiResponse));
    console.log('Spill:', JSON.stringify(apiResponse.spill, null, 2));

    if (apiResponse.candidates) {
      console.log('Candidates count:', apiResponse.candidates.length);
      if (apiResponse.candidates.length > 0) {
        console.log('First candidate:', JSON.stringify(apiResponse.candidates[0], null, 2));
      }
    } else {
      console.log('No candidates key in response');
    }
  } else {
    console.log('No API response captured');
  }

  // Now check React state directly
  const reactState = await page.evaluate(() => {
    const root = document.getElementById('root');
    if (!root) return { error: 'No root element' };

    const fiberKey = Object.keys(root).find(k => k.startsWith('__reactFiber'));
    if (!fiberKey) return { error: 'No React fiber' };

    // Walk the fiber tree to find App component state
    let fiber = root[fiberKey];
    let found = null;

    // Find the App component fiber
    const findApp = (f, depth = 0) => {
      if (!f || depth > 20) return;

      // Check if this is the App component
      if (f.type && f.type.name === 'App') {
        found = f;
        return;
      }

      // Check child and sibling
      if (f.child) findApp(f.child, depth + 1);
      if (f.sibling) findApp(f.sibling, depth + 1);
    };

    findApp(fiber);

    if (!found) return { error: 'App component not found' };

    // Extract state from memoizedState
    const states = [];
    let state = found.memoizedState;
    while (state) {
      if (state.memoizedState !== undefined && state.memoizedState !== null) {
        const val = state.memoizedState;
        if (typeof val === 'object' && val !== null && val.candidates) {
          states.push({
            type: 'result',
            candidates: val.candidates?.length || 0,
            spill: val.spill ? { detected: val.spill.detected, confidence: val.spill.confidence } : null
          });
        } else if (Array.isArray(val)) {
          states.push({ type: 'array', length: val.length });
        } else {
          states.push({ type: typeof val, value: String(val).substring(0, 50) });
        }
      }
      state = state.next;
    }

    return { states };
  });

  console.log('\n=== React State ===');
  console.log(JSON.stringify(reactState, null, 2));

  await browser.close();
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
