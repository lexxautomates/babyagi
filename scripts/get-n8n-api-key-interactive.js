/**
 * Playwright script to get n8n API key - Interactive mode
 * Run: node scripts/get-n8n-api-key-interactive.js <email> <password>
 */

const { chromium } = require('playwright');

async function getN8nApiKey(email, password) {
  // Run in non-headless mode so user can see and interact
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Navigating to n8n...');
    console.log('A browser window will open. You can interact with it if needed.');
    await page.goto('https://n8n.lexxautomates.com');
    await page.waitForLoadState('networkidle');

    // Check if we need to log in
    const emailInput = await page.$('input[type="email"], input[name="email"], input[placeholder*="email"], input[placeholder*="Email"]');
    
    if (emailInput) {
      console.log('Login form found, logging in...');
      
      // Fill email
      await emailInput.fill(email);
      
      // Find and fill password
      const passwordInput = await page.$('input[type="password"], input[name="password"]');
      if (passwordInput) {
        await passwordInput.fill(password);
      }
      
      // Find and click submit button
      const submitBtn = await page.$('button[type="submit"]');
      if (submitBtn) {
        await submitBtn.click();
      } else {
        await page.keyboard.press('Enter');
      }
      
      console.log('Waiting for login to complete...');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000);
    }

    console.log('\n=== INSTRUCTIONS ===');
    console.log('The browser is now open.');
    console.log('Please navigate to: User Menu -> Settings -> API -> Create API Key');
    console.log('Once you see the API key, copy it and paste it here.');
    console.log('Press Ctrl+C when done.\n');

    // Wait indefinitely for user to complete the task
    await new Promise(() => {}); // Keep browser open

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Get credentials from command line
const email = process.argv[2];
const password = process.argv[3];

if (!email || !password) {
  console.log('Usage: node scripts/get-n8n-api-key-interactive.js <email> <password>');
  process.exit(1);
}

getN8nApiKey(email, password);