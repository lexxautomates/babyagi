/**
 * Playwright script to setup n8n account and get API key
 * Run: node scripts/setup-n8n-account.js
 */

const { chromium } = require('playwright');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function setupN8n() {
  const browser = await chromium.launch({ headless: false, slowMo: 300 });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Navigating to n8n...');
    await page.goto('https://n8n.lexxautomates.com');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Take screenshot to see current state
    await page.screenshot({ path: 'n8n-setup-initial.png' });
    console.log('Initial screenshot saved to n8n-setup-initial.png');

    // Check if this is the initial setup (create account page)
    const setupForm = await page.$('input[placeholder*="First name"], input[name="firstName"], h1:has-text("Create")');
    
    if (setupForm) {
      console.log('\n=== N8N INITIAL SETUP DETECTED ===');
      console.log('This appears to be a fresh n8n installation.');
      console.log('Please fill in the account details in the browser window.\n');
      
      // Get account details from user
      const firstName = await question('Enter your first name: ');
      const lastName = await question('Enter your last name: ');
      const email = await question('Enter your email: ');
      const password = await question('Enter your password: ');

      // Fill in the setup form
      console.log('\nFilling in account details...');
      
      const firstNameInput = await page.$('input[placeholder*="First name"], input[name="firstName"], input[id="firstName"]');
      const lastNameInput = await page.$('input[placeholder*="Last name"], input[name="lastName"], input[id="lastName"]');
      const emailInput = await page.$('input[type="email"], input[placeholder*="email"], input[name="email"]');
      const passwordInput = await page.$('input[type="password"], input[placeholder*="password"], input[name="password"]');

      if (firstNameInput) await firstNameInput.fill(firstName);
      if (lastNameInput) await lastNameInput.fill(lastName);
      if (emailInput) await emailInput.fill(email);
      if (passwordInput) await passwordInput.fill(password);

      await page.screenshot({ path: 'n8n-setup-filled.png' });
      
      // Click continue/start button
      const startBtn = await page.$('button:has-text("Start"), button:has-text("Continue"), button:has-text("Create"), button[type="submit"]');
      if (startBtn) {
        console.log('Clicking start button...');
        await startBtn.click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(3000);
      }

      console.log('\nAccount created! Now let\'s get the API key.');
    }

    // Now navigate to get API key
    console.log('\n=== NAVIGATING TO API SETTINGS ===');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'n8n-after-setup.png' });

    // Try to find and click user menu
    console.log('Looking for user menu...');
    
    // Wait for the page to be ready
    await page.waitForTimeout(2000);
    
    // Look for avatar/user button in top right
    const userButton = await page.$('[data-test-id="user-menu-button"], button[class*="avatar"], [class*="UserMenu"], button[aria-label*="menu"]');
    
    if (userButton) {
      console.log('Found user menu, clicking...');
      await userButton.click();
      await page.waitForTimeout(1000);
      
      // Click Settings
      const settingsBtn = await page.$('text=Settings, [data-test-id="settings"]');
      if (settingsBtn) {
        await settingsBtn.click();
        await page.waitForTimeout(1000);
      }
      
      // Click API
      const apiBtn = await page.$('text=API, [data-test-id="api"]');
      if (apiBtn) {
        await apiBtn.click();
        await page.waitForTimeout(1000);
      }
      
      // Create API Key
      const createBtn = await page.$('button:has-text("Create"), button:has-text("Create API Key")');
      if (createBtn) {
        await createBtn.click();
        await page.waitForTimeout(1000);
        
        // Enter name for key
        const nameInput = await page.$('input[placeholder*="name"], input[name="name"]');
        if (nameInput) {
          await nameInput.fill('API Key');
          const confirmBtn = await page.$('button:has-text("Create"), button:has-text("Confirm")');
          if (confirmBtn) await confirmBtn.click();
          await page.waitForTimeout(1000);
        }
      }
    }

    await page.screenshot({ path: 'n8n-api-key-page.png' });
    
    // Look for API key in page
    const pageContent = await page.content();
    const jwtMatch = pageContent.match(/eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+/g);
    
    if (jwtMatch && jwtMatch.length > 0) {
      const apiKey = jwtMatch[jwtMatch.length - 1];
      console.log('\n=== YOUR API KEY ===');
      console.log(apiKey);
      console.log('====================\n');
      
      // Save to file
      require('fs').writeFileSync('n8n-api-key.txt', apiKey);
      console.log('API key saved to n8n-api-key.txt');
    } else {
      console.log('\nCould not automatically extract API key.');
      console.log('Please copy the API key from the browser window.');
      console.log('A screenshot was saved to n8n-api-key-page.png');
    }

    console.log('\nPress Enter to close the browser...');
    await question('');

  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: 'n8n-setup-error.png' });
  } finally {
    rl.close();
    await browser.close();
  }
}

setupN8n();