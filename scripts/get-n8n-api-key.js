/**
 * Playwright script to get n8n API key
 * Run: node scripts/get-n8n-api-key.js <email> <password>
 */

const { chromium } = require('playwright');

async function getN8nApiKey(email, password) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Navigating to n8n...');
    await page.goto('https://n8n.lexxautomates.com', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);

    // Take a screenshot to see the page
    await page.screenshot({ path: 'n8n-initial.png' });
    console.log('Initial screenshot saved to n8n-initial.png');

    // Check if we need to log in - look for various login indicators
    const emailInput = await page.$('input[type="email"], input[name="email"], input[placeholder*="email"], input[placeholder*="Email"]');
    
    if (emailInput) {
      console.log('Login form found, logging in...');
      
      // Fill email
      await emailInput.fill(email);
      await page.waitForTimeout(500);
      
      // Find and fill password
      const passwordInput = await page.$('input[type="password"], input[name="password"]');
      if (passwordInput) {
        await passwordInput.fill(password);
        await page.waitForTimeout(500);
      }
      
      // Take screenshot before clicking
      await page.screenshot({ path: 'n8n-before-submit.png' });
      
      // Find and click submit button - try multiple selectors
      const submitBtn = await page.$('button[type="submit"], button:has-text("Login"), button:has-text("Sign in"), button:has-text("Log in"), [data-test-id="submit"]');
      if (submitBtn) {
        await submitBtn.click();
      } else {
        // Try pressing Enter
        await page.keyboard.press('Enter');
      }
      
      console.log('Waiting for login to complete...');
      await page.waitForTimeout(5000);
      
      // Take screenshot after login
      await page.screenshot({ path: 'n8n-after-login.png' });
      console.log('After-login screenshot saved to n8n-after-login.png');
    }

    // Check if we're logged in by looking for user menu
    console.log('Looking for user menu...');
    await page.waitForTimeout(2000);
    
    // Try to find user menu button - n8n uses various selectors
    const userMenuSelectors = [
      '[data-test-id="user-menu"]',
      '[data-test-id="user-menu-button"]',
      'button[aria-label*="user"]',
      'button[aria-label*="User"]',
      'button[aria-label*="account"]',
      '.user-menu',
      '[class*="UserMenu"]',
      'button[class*="avatar"]',
      '[class*="avatar"]'
    ];
    
    let userMenuFound = false;
    for (const selector of userMenuSelectors) {
      const menu = await page.$(selector);
      if (menu) {
        console.log(`Found user menu with selector: ${selector}`);
        await menu.click();
        userMenuFound = true;
        break;
      }
    }
    
    if (!userMenuFound) {
      // Try clicking on the top right area where user menu typically is
      console.log('Trying to find user menu by position...');
      await page.screenshot({ path: 'n8n-no-menu.png' });
      
      // Look for any clickable element in the header
      const headerButtons = await page.$$('header button, [class*="header"] button');
      console.log(`Found ${headerButtons.length} buttons in header`);
    }

    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'n8n-menu-click.png' });

    // Look for Settings link
    console.log('Looking for Settings...');
    const settingsSelectors = [
      'a:has-text("Settings")',
      'button:has-text("Settings")',
      '[data-test-id="settings"]',
      'text=Settings'
    ];
    
    for (const selector of settingsSelectors) {
      const settings = await page.$(selector);
      if (settings) {
        console.log(`Found Settings with selector: ${selector}`);
        await settings.click();
        break;
      }
    }
    
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'n8n-settings.png' });

    // Look for API section
    console.log('Looking for API section...');
    const apiSelectors = [
      'a:has-text("API")',
      'button:has-text("API")',
      '[data-test-id="api"]',
      'text=API'
    ];
    
    for (const selector of apiSelectors) {
      const api = await page.$(selector);
      if (api) {
        console.log(`Found API with selector: ${selector}`);
        await api.click();
        break;
      }
    }
    
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'n8n-api-page.png' });

    // Look for Create API Key button
    console.log('Looking for Create API Key button...');
    const createKeySelectors = [
      'button:has-text("Create")',
      'button:has-text("Create API Key")',
      '[data-test-id="create-api-key"]',
      'button:has-text("Add")'
    ];
    
    for (const selector of createKeySelectors) {
      const createBtn = await page.$(selector);
      if (createBtn) {
        console.log(`Found Create button with selector: ${selector}`);
        await createBtn.click();
        break;
      }
    }
    
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'n8n-create-key.png' });

    // Look for API key in the page
    console.log('Looking for API key...');
    const pageContent = await page.content();
    
    // Look for JWT-style API key
    const jwtMatch = pageContent.match(/eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+/g);
    if (jwtMatch && jwtMatch.length > 0) {
      console.log('\n=== YOUR API KEY ===');
      console.log(jwtMatch[jwtMatch.length - 1]); // Get the last match (most likely the new key)
      console.log('====================\n');
      return jwtMatch[jwtMatch.length - 1];
    }

    // Look for any code element or input with the key
    const keyElement = await page.$('code, pre, input[type="text"][readonly]');
    if (keyElement) {
      const keyText = await keyElement.textContent();
      if (keyText && keyText.startsWith('eyJ')) {
        console.log('\n=== YOUR API KEY ===');
        console.log(keyText);
        console.log('====================\n');
        return keyText;
      }
    }

    console.log('Could not find API key automatically.');
    console.log('Check the screenshots to see the current state:');
    console.log('- n8n-initial.png');
    console.log('- n8n-after-login.png');
    console.log('- n8n-settings.png');
    console.log('- n8n-api-page.png');
    console.log('- n8n-create-key.png');

  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: 'n8n-error.png' });
    console.log('Error screenshot saved to n8n-error.png');
  } finally {
    await browser.close();
  }
}

// Get credentials from command line
const email = process.argv[2];
const password = process.argv[3];

if (!email || !password) {
  console.log('Usage: node scripts/get-n8n-api-key.js <email> <password>');
  process.exit(1);
}

getN8nApiKey(email, password);