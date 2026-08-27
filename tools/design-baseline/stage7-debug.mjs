/* stage7-debug.mjs — диагностика DOM для installCrumbs() */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
import { resolve, join } from 'node:path';
const APP = resolve('c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab');
const u = pathToFileURL(join(APP,'index.html')).href + '#manifest';
(async () => {
  const b = await chromium.launch({ channel:'chrome', headless:true, args:['--allow-file-access-from-files','--no-sandbox'] });
  const p = await b.newPage();
  p.on('console', msg => console.log('PAGE[' + msg.type() + ']: ' + msg.text()));
  await p.goto(u, { waitUntil:'domcontentloaded', timeout:15000 }).catch(()=>{});
  await p.waitForFunction('window.LabNav', { timeout:8000 }).catch(() => console.log('LabNav NOT READY'));
  await p.waitForTimeout(600);
  const r = await p.evaluate(() => {
    return {
      crumbSlot: !!document.querySelector('.lab-crumb-slot'),
      navCrumb: !!document.querySelector('.lab-crumbs'),
      currentSpan: !!document.querySelector('.lab-crumb-current'),
      navScriptSrc: Array.from(document.querySelectorAll('script[src*="nav-enhance"]')).map(s=>({src:s.getAttribute('src'),def:s.hasAttribute('defer'),pos:s.parentNode.tagName})),
      sidebar: !!document.querySelector('.lab-sidebar')
    };
  });
  console.log(JSON.stringify(r, null, 2));
  await b.close();
})();
