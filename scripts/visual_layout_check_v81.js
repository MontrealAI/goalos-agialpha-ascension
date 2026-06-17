const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const root = process.argv[2] || 'site';
const pages = ['index.html','proof-cards.html','proof-card-001.html','proof-card-023.html','proof-card-024.html','proof-card-028.html','proof-card-031.html','mission-os.html','ascension.html','proof-treasury.html','paper.html'];
const viewports = [[320,800],[375,812],[768,1024],[1024,768],[1440,1000]];
(async () => {
  const browser = await chromium.launch();
  const failures = [];
  for (const [width,height] of viewports) {
    const page = await browser.newPage({viewport:{width,height}});
    for (const p of pages) {
      const file = 'file://' + path.resolve(root, p);
      await page.goto(file);
      const result = await page.evaluate(() => {
        const issues=[];
        if (document.documentElement.scrollWidth > window.innerWidth + 2) issues.push(`horizontal scroll ${document.documentElement.scrollWidth} > ${window.innerWidth}`);
        const selectors = '.figure-frame,.diagram-frame,.visual-shell,.proof-card-visual,.card,.panel';
        document.querySelectorAll(selectors).forEach((el,i)=>{
          const b=el.getBoundingClientRect();
          el.querySelectorAll('img,svg,canvas,video').forEach((child,j)=>{
            const c=child.getBoundingClientRect();
            if (c.left < b.left - 2 || c.right > b.right + 2 || c.top < b.top - 2 || c.bottom > b.bottom + 2) issues.push(`overflow ${selectors} #${i} child ${j}`);
          });
        });
        document.querySelectorAll('img').forEach((img,i)=>{ if (!img.getAttribute('alt') && img.getAttribute('aria-hidden')!=='true') issues.push(`missing alt image ${i}`); });
        return issues;
      });
      if (result.length) failures.push({page:p, viewport:`${width}x${height}`, issues:result});
    }
    await page.close();
  }
  await browser.close();
  fs.mkdirSync(path.join(root,'qa'), {recursive:true});
  fs.writeFileSync(path.join(root,'qa','layout-report-v81.json'), JSON.stringify({status: failures.length?'failed':'passed', failures}, null, 2));
  fs.mkdirSync('docs', {recursive:true});
  fs.writeFileSync('docs/LAYOUT_QA_ASCENSION_WEBSITE_v81.md', '# Layout QA v81\n\n' + (failures.length ? JSON.stringify(failures,null,2) : 'Passed at required viewports.\n'));
  if (failures.length) { console.error(JSON.stringify(failures,null,2)); process.exit(1); }
  console.log('Layout QA passed.');
})();
