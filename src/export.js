const puppeteer = require('puppeteer');
const path = require("path");

const htmlFile = path.resolve(process.argv[2]);
const baseName = htmlFile.replace(/\.html$/, '');

(async () => {
   const browser = await puppeteer.launch();
   const page = await browser.newPage();
   await page.goto(`file://${htmlFile}`);

   const dimensions = await page.evaluate(() => {
      return {
         height: document.documentElement.offsetHeight,
         width: document.documentElement.offsetWidth
      }
   });

   await page.pdf({
      path: `${baseName}.pdf`,
      height: dimensions.height+'px',
      width: dimensions.width+'px',
      printBackground: true
   });

   await page.screenshot({
      path: `${baseName}.png`,
      fullPage: true
   });

  await browser.close();
})();
