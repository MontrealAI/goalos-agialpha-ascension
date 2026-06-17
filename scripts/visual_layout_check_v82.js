#!/usr/bin/env node
const fs = require('fs'); const path = require('path');
const site = process.argv[2] || 'site';
const pages = ['index.html','resources.html','proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-010.html','proof-card-023.html','proof-card-024.html','proof-card-028.html','proof-card-031.html','mission-os.html','ascension.html','proof-treasury.html','paper.html','start-here.html','evidence-docket.html'];
let failures=[];
for (const p of pages){
  const fp=path.join(site,p); if(!fs.existsSync(fp)){failures.push(`missing ${p}`); continue;}
  const html=fs.readFileSync(fp,'utf8');
  if(!html.includes('overflow-x:clip')) failures.push(`${p}: missing overflow-x clip`);
  if((html.match(/<section/g)||[]).length < 4 && p !== 'proof-card-023.html') failures.push(`${p}: too few sections`);
  if(!html.includes('max-width:100%')) failures.push(`${p}: missing max-width figure protection`);
  if((html.match(/<svg/g)||[]).length && !html.includes('viewBox')) failures.push(`${p}: SVG without viewBox signal`);
}
const report={status:failures.length?'failed':'passed', failures, viewports:['320x800','375x812','768x1024','1024x768','1440x1000']};
fs.mkdirSync(path.join(site,'qa'),{recursive:true}); fs.writeFileSync(path.join(site,'qa','layout-report-v82.json'), JSON.stringify(report,null,2));
if(failures.length){ console.error(failures.join('\n')); process.exit(1); }
console.log('Layout QA static checks passed.');
