/**
 * Simple script to open n8n in a browser for manual setup
 */

const { chromium } = require('playwright');

async function openN8n() {
  console.log('Opening n8n in browser...');
  console.log('Please complete the setup and get your API key.');
  console.log('Steps:');
  console.log('1. If this is a fresh install, create your account');
  console.log('2. Click your user icon (top right)');
  console.log('3. Go to Settings -> API');
  console.log('4. Click "Create API Key"');
  console.log('5. Copy the API key');
  console.log('\nClose the browser when done.\n');

  const browser = await chromium.launch({ 
    headless: false,
    args: ['--start-maximized']
  });
  
  const context = await browser.newContext({
    viewport: null
  });
  
  const page = await context.newPage();
  
  await page.goto('https://n8n.lexxautomates.com');
  
  // Wait for browser to be closed
  await new Promise(() => {});
}

openN8n().catch(console.error);