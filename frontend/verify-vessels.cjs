const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const BASE_URL = 'http://localhost:5173';
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  console.log('Navigating to OilGuard...');
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });

  // Upload and analyze
  console.log('Uploading Class 1 image...');
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(CLASS1_IMAGE);
  await page.waitForTimeout(500);

  console.log('Clicking ANALYZE...');
  const analyzeBtn = page.locator('button:has-text("ANALYZE SAR SCENE")');
  await analyzeBtn.waitFor({ state: 'visible', timeout: 5000 });
  await analyzeBtn.click();

  // Wait for analysis
  console.log('Waiting for analysis...');
  await page.waitForTimeout(12000);

  // Check maplibre map via evaluate
  console.log('\n=== Checking Maplibre Vessels ===');
  const mapData = await page.evaluate(() => {
    // Get the map container
    const container = document.querySelector('.globe-container');
    if (!container) return { error: 'No container' };

    // Find React fiber to get map ref
    const fiberKey = Object.keys(container).find(k => k.startsWith('__reactFiber'));
    if (!fiberKey) return { error: 'No fiber' };

    const fiber = container[fiberKey];
    // Find GlobeContainer fiber
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

    // Get state
    const state = globeFiber.memoizedState;
    if (!state) return { error: 'No state' };

    // Find mapRef in memoizedState - it's a linked list of useState hooks
    let map = null;
    let hookState = state;
    while (hookState) {
      // mapRef is stored in the memoizedState of useRef
      if (hookState.memoizedState && hookState.memoizedState.current && hookState.memoizedState.current.getStyle) {
        map = hookState.memoizedState.current;
        break;
      }
      hookState = hookState.next;
    }

    if (!map) return { error: 'No map found in state' };

    const style = map.getStyle();
    const sources = {};
    if (style && style.sources) {
      Object.keys(style.sources).forEach(key => {
        sources[key] = style.sources[key].type;
      });
    }

    let vesselsData = 'NOT FOUND';
    let vesselsFeatures = 0;
    if (map.getSource('vessels')) {
      const src = map.getSource('vessels');
      vesselsData = 'FOUND';
      vesselsFeatures = src._data?.features?.length || 0;
    }

    const layers = style?.layers?.map(l => l.id) || [];

    return { sources, vesselsData, vesselsFeatures, layers };
  });

  console.log('Map data:', JSON.stringify(mapData, null, 2));

  // Check if prototype markers are removed
  const protoMarkers = await page.locator('.prototype-vessel-marker').count();
  console.log('\nPrototype DOM markers:', protoMarkers, '(should be 0)');

  // Check React props to confirm vessels were passed
  const reactProps = await page.evaluate(() => {
    const container = document.querySelector('.globe-container');
    if (!container) return { error: 'No container' };
    const propsKey = Object.keys(container).find(k => k.startsWith('__reactProps'));
    if (!propsKey) return { error: 'No props' };
    const props = container[propsKey];
    return {
      vesselsLength: props.vessels ? props.vessels.length : 0,
      vesselsNames: props.vessels ? props.vessels.map(v => v.name) : [],
      spillResult: props.spillResult ? { detected: props.spillResult.detected, confidence: props.spillResult.confidence } : null
    };
  });

  console.log('\n=== React Props ===');
  console.log('Vessels count:', reactProps.vesselsLength);
  console.log('Vessel names:', reactProps.vesselsNames);
  console.log('Spill result:', reactProps.spillResult);

  // Try clicking on the map center
  console.log('\n=== Click Test ===');
  const mapContainer = page.locator('.globe-container');
  const box = await mapContainer.boundingBox();
  if (box) {
    console.log('Map container size:', box.width, 'x', box.height);

    // Click at center
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    await page.waitForTimeout(2000);

    const panel = page.locator('.vessel-investigation-panel');
    const isVisible = await panel.isVisible().catch(() => false);
    console.log('Panel visible after click:', isVisible);

    if (isVisible) {
      const panelText = await panel.textContent();
      console.log('Panel text (first 400):', panelText.substring(0, 400));
    }
  }

  await browser.close();
  console.log('\nDone');
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
