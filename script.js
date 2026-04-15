const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:3000/register');
  await page.waitForTimeout(2000);
  
  await page.fill('#fullname', 'Test User');
  await page.fill('#email', 'test@example.com');
  
  await page.screenshot({ path: 'register.jpg', type: 'jpeg', quality: 90 });
  await browser.close();
  console.log('saved register.jpg');
})();
