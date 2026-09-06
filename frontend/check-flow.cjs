const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  console.log('Navigating to OilGuard...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });

  // Check initial state
  console.log('\n=== Initial State ===');
  const initialProps = await page.evaluate(() => {
    const container = document.querySelector('.globe-container');
    if (!container) return { error: 'No container' };
    const propsKey = Object.keys(container).find(k => k.startsWith('__reactProps'));
    if (!propsKey) return { error: 'No props key' };
    const props = container[propsKey];
    return {
      vessels: props.vessels,
      spillResult: props.spillResult
    };
  });
  console.log('Initial GlobeContainer props:', JSON.stringify(initialProps, null, 2));

  // Upload and analyze
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(CLASS1_IMAGE);
  await page.waitForTimeout(500);

  const analyzeBtn = page.locator('button:has-text("ANALYZE SAR SCENE")');
  await analyzeBtn.click();

  // Check state after click but before analysis completes
  console.log('\n=== During Analysis (5s) ===');
  await page.waitForTimeout(5000);
  const duringProps = await page.evaluate(() => {
    const container = document.querySelector('.globe-container');
    if (!container) return { error: 'No container' };
    const propsKey = Object.keys(container).find(k => k.startsWith('__reactProps'));
    if (!propsKey) return { error: 'No props key' };
    const props = container[propsKey];
    return {
      vessels: props.vessels,
      spillResult: props.spillResult
    };
  });
  console.log('During analysis GlobeContainer props:', JSON.stringify(duringProps, null, 2));

  // Check state after analysis completes
  console.log('\n=== After Analysis (12s) ===');
  await page.waitForTimeout(7000);
  const afterProps = await page.evaluate(() => {
    const container = document.querySelector('.globe-container');
    if (!container) return { error: 'No container' };
    const propsKey = Object.keys(container).find(k => k.startsWith('__reactProps'));
    if (!propsKey) return { error: 'No props key' };
    const props = container[propsKey];
    return {
      vessels: props.vessels,
      spillResult: props.spillResult
    };
  });
  console.log('After analysis GlobeContainer props:', JSON.stringify(afterProps, null, 2));

  // Also check App state
  const appState = await page.evaluate(() => {
    const root = document.getElementById('root');
    if (!root) return { error: 'No root' };
    const fiberKey = Object.keys(root).find(k => k.startsWith('__reactFiber'));
    if (!fiberKey) return { error: 'No fiber' };
    const fiber = root[fiberKey];
    // Walk to find App
    let appFiber = null;
    const findApp = (f, depth = 0) => {
      if (!f || depth > 30) return;
      if (f.type && f.type.name === 'App') {
        appFiber = f;
        return;
      }
      if (f.child) findApp(f.child, depth + 1);
      if (f.sibling) findApp(f.sibling, depth + 1);
    };
    findApp(fiber);
    if (!appFiber) return { error: 'App not found' };

    // Get state
    const states = [];
    let state = appFiber.memoizedState;
    while (state) {
      if (state.memoizedState !== undefined && state.memoizedState !== null) {
        states.push({
          type: typeof state.memoizedState,
          keys: state.memoizedState && typeof state.memoizedState === 'object' ? Object.keys(state.memoizedState) : null,
          isResult: state.memoizedState && state.memoizedState.candidates !== undefined,
          candidatesCount: state.memoizedState?.candidates?.length,
          spill: state.memoizedState?.spill
        });
      }
      state = state.next;
    }
    return { states };
  });
  console.log('\n=== App State ===');
  console.log(JSON.stringify(appState, null, 2));

  await browser.close();
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});