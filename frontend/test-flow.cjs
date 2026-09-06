const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const CLASS1_IMAGE = 'C:\\Users\\amit nagar\\Projects\\oilguard\\data\\CSIRO\\S1SAR_UnBalanced_400by400_Class_1\\1\\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg';

  // Capture console logs
  const logs = [];
  page.on('console', msg => {
    if (msg.type() === 'log' || msg.type() === 'error') {
      logs.push(`[${msg.type()}] ${msg.text()}`);
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

  console.log('Waiting for analysis...');
  await page.waitForTimeout(12000);

  // Print captured logs
  console.log('\n=== Console Logs ===');
  logs.forEach(log => console.log(log));

  // Check final state
  const globeProps = await page.evaluate(() => {
    const container = document.querySelector('.globe-container');
    if (!container) return { error: 'No container' };
    const propsKey = Object.keys(container).find(k => k.startsWith('__reactProps'));
    if (!propsKey) return { error: 'No props key' };
    const props = container[propsKey];
    return {
      vesselsLength: props.vessels ? props.vessels.length : 0,
      vesselsNames: props.vessels ? props.vessels.map(v => v.name) : [],
      spillResult: props.spillResult ? { detected: props.spillResult.detected, confidence: props.spillResult.confidence } : null
    };
  });
  console.log('\n=== Final GlobeContainer Props ===');
  console.log(JSON.stringify(globeProps, null, 2));

  await browser.close();
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});