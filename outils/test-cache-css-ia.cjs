#!/usr/bin/env node
'use strict';
// Simule une ancienne réponse CSS conservée sous l'URL non versionnée.
// Ne prétend pas lire le cache du téléphone qui a fourni la capture.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
if (process.env.MRSC_BROWSER_NODE_MODULES) {
  process.env.NODE_PATH = process.env.MRSC_BROWSER_NODE_MODULES;
  require('node:module').Module._initPaths();
}
const puppeteer = require('puppeteer-core');
const pkg = require('@sparticuz/chromium');
const chromium = pkg.default || pkg;
const root = path.resolve(__dirname, '..');
const css = fs.readFileSync(path.join(root, 'assets/css/site.css'), 'utf8');
const version = crypto.createHash('sha256').update(css).digest('hex').slice(0, 16);
const html = fs.readFileSync(path.join(root, 'ia-societe.html'), 'utf8');
// Positions de f3c4ddf, avant la PR 188 ; seules les règles impliquées sont rejouées.
const ancien = process.env.MRSC_ANCIEN_CSS ? fs.readFileSync(process.env.MRSC_ANCIEN_CSS, 'utf8') : css + `
.ai-constellation-core {top:50%; width:142px; height:142px}
.ai-node-work,.ai-node-health {top:20.6%}
.ai-node-info {top:63%; left:12.4%}
.ai-node-services {top:68.6%; left:87.2%}
.ai-node-place {top:86.8%}
@media(max-width:520px){.ai-constellation-core{width:112px;height:112px}.ai-node-info{left:23%}.ai-node-services{left:77%}}
@media(max-width:380px){.ai-node-info{left:26%}.ai-node-services{left:74%}}
`;
(async () => {
  const browser = await puppeteer.launch({executablePath: await chromium.executablePath(), args: chromium.args, headless:true});
  const resultats = [];
  try {
    assert.ok(html.includes(`assets/css/site.css?v=${version}`), 'Version CSS absente ou périmée');
    for (const cas of ['ancienne-url', 'url-versionnee']) {
      const page = await browser.newPage();
      const requetes = [];
      await page.setRequestInterception(true);
      page.on('request', req => {
        const url = new URL(req.url());
        if (url.pathname.endsWith('/ia-societe.html')) {
          const body = cas === 'ancienne-url' ? html.replace(`site.css?v=${version}`, 'site.css') : html;
          return req.respond({status:200, contentType:'text/html', body});
        }
        if (url.pathname.endsWith('/assets/css/site.css')) {
          requetes.push(url.search);
          return req.respond({status:200, contentType:'text/css', body:url.search === `?v=${version}` ? css : ancien});
        }
        return req.continue();
      });
      await page.setViewport({width:390,height:1000,deviceScaleFactor:2});
      await page.goto(new URL('ia-societe.html',process.env.MRSC_TEST_URL || 'http://127.0.0.1:4181/').href,{waitUntil:'networkidle0'});
      await page.addStyleTag({content:'*{animation:none!important;transition:none!important}'});
      for (const largeur of [320,390,768]) for (const disposition of ['equilibree','compacte']) {
        await page.setViewport({width:largeur,height:1000,deviceScaleFactor:2});
        await page.evaluate(disposition => {document.documentElement.dataset.layout=disposition;document.documentElement.classList.add('texte-tres-agrandi');}, disposition);
        const ecarts = await page.evaluate(() => {
          const nodes=[...document.querySelectorAll('.ai-node')];
          const points=[...document.querySelectorAll('.ai-constellation-lines circle[r="4"]')];
          return nodes.map((n,i)=>{const a=n.getBoundingClientRect(),b=points[i].getBoundingClientRect();return Math.hypot(a.x+a.width/2-b.x-b.width/2,a.y+a.height/2-b.y-b.height/2);});
        });
        const maximum=Math.max(...ecarts);
        assert.ok(cas==='ancienne-url' ? maximum>2 : maximum<=2, `${cas} ${largeur} ${disposition} : ${maximum}px`);
        resultats.push({cas,largeur,disposition,texte:130,ecartMax:maximum,requetes:[...requetes]});
        if(process.env.MRSC_CAPTURES && largeur===390 && disposition==='compacte') {
          fs.mkdirSync(process.env.MRSC_CAPTURES,{recursive:true});
          await (await page.$('.ai-visual-column')).screenshot({path:path.join(process.env.MRSC_CAPTURES,`ia-cache-${cas}.png`)});
        }
      }
      await page.close();
    }
    if(process.env.MRSC_CACHE_JSON)fs.writeFileSync(process.env.MRSC_CACHE_JSON,JSON.stringify({version,resultats},null,2)+'\n');
    console.log('12 essais : ancien décalage reproduit, URL versionnée alignée (320/390/768, équilibrée/compacte, 130 %, densité 2).');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
