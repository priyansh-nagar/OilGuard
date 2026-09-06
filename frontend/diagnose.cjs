const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const logs = [];
  page.on('console', msg => {
    if (msg.type() === 'log' || msg.type() === 'error') {
      logs.push(`[${msg.type()}] ${msg.text()}`);
    }
  });

  console.log('Navigating to OilGuard...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle', timeout: 60000 });

  console.log('Page title:', await page.title());
  console.log('Page URL:', page.url());

  // Get full HTML
  const html = await page.content();
  console.log('\n=== Page HTML (first 5000 chars) ===');
  console.log(html.substring(0, 5000));

  // Print captured logs
  console.log('\n=== Console Logs ===');
  logs.forEach(log => console.log(log));

  await browser.close();
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});