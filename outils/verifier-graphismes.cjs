#!/usr/bin/env node
'use strict';
// Contrôle navigateur ciblé des deux images restaurées et de la constellation.
// Les dimensions décodées (pas naturalWidth, corrigé par srcset) font foi.
const fs = require('node:fs');
const path = require('node:path');
if (process.env.MRSC_BROWSER_NODE_MODULES) {
  process.env.NODE_PATH = process.env.MRSC_BROWSER_NODE_MODULES;
  require('node:module').Module._initPaths();
}
const puppeteer = require('puppeteer-core');
const pkg = require('@sparticuz/chromium');
const chromium = pkg.default || pkg;
const base = process.env.MRSC_TEST_URL || 'http://127.0.0.1:4181/';
const output = process.env.MRSC_GRAPHISMES_JSON || 'docs/rd/audit-graphismes-2026-10-24.json';
const captures = process.env.MRSC_CAPTURES;
const mutation = process.env.MRSC_MUTATION || '';
(async () => {
  const browser = await puppeteer.launch({ executablePath: await chromium.executablePath(), args: chromium.args, headless: true });
  const report = { perimetre: 'Accueil, illustration Apprendre, constellation IA uniquement', navigateur: await browser.version(), mutation, releves: [], erreurs: [] };
  try {
    for (const dpr of (mutation ? [2] : [1, 2])) for (const route of (process.env.MRSC_PAGES ? process.env.MRSC_PAGES.split(',') : mutation ? [mutation === 'ancre' ? 'ia-societe.html' : 'index.html'] : ['index.html', 'apprendre.html', 'ia-societe.html'])) {
      const page = await browser.newPage();
      await page.setViewport({ width: 1440, height: 1000, deviceScaleFactor: dpr });
      await page.goto(new URL(route, base).href, { waitUntil: 'networkidle0' });
      await page.addStyleTag({ content: '* { animation: none !important; transition: none !important; }' });
      const target = route === 'index.html' ? '.home-hero-visual' : route === 'apprendre.html' ? '.english-promo-art' : '.ai-constellation';
      await page.$eval(target, el => el.scrollIntoView({block: 'center'}));
      if (mutation === 'distorsion') await page.addStyleTag({content: '.home-hero-visual img {height: 100px !important; object-fit: fill !important}'});
      if (mutation === 'ancre') await page.addStyleTag({content: '.ai-node-info {left: 40% !important}'});
      if (mutation === 'densite') await page.$eval('body', () => {const s=document.querySelectorAll('.home-hero-visual source');s.forEach(x=>x.remove());const i=document.querySelector('.home-hero-visual img');if(i)i.src='assets/images/accueil-logo-mrsc-3d-800.webp';});
      for (const largeur of (mutation ? [1440] : [320, 360, 390, 768, 1024, 1280, 1440])) {
        await page.setViewport({width: largeur, height: 1000, deviceScaleFactor: dpr});
        for (const texte of (mutation ? [100] : [75, 85, 100, 115, 130])) for (const disposition of (mutation ? ['equilibree'] : ['equilibree', 'lecture', 'vitrine', 'mosaique', 'panorama', 'compacte'])) for (const mode of (mutation ? ['normal'] : ['normal', 'renforce', 'couleurs-forcees'])) {
          await page.emulateMediaFeatures([{name:'forced-colors', value: mode === 'couleurs-forcees' ? 'active' : 'none'}]);
          await page.evaluate(({texte, disposition, mode}) => {
            const r=document.documentElement;
            r.dataset.layout=disposition;
            ['texte-tres-reduit','texte-reduit','texte-agrandi','texte-tres-agrandi','contraste-renforce','espacement-renforce'].forEach(c=>r.classList.remove(c));
            const c={75:'texte-tres-reduit',85:'texte-reduit',115:'texte-agrandi',130:'texte-tres-agrandi'}[texte];if(c)r.classList.add(c);
            if(mode==='renforce')r.classList.add('contraste-renforce','espacement-renforce');
          }, {texte, disposition, mode});
          const mesures=await page.evaluate(async target => {
            const el=document.querySelector(target), erreurs=[];
            const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};};
            const overlap=(a,b)=>Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>1 && Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>1;
            const image=el.querySelector('img');
            if(image) {
              if(!image.checkVisibility())return {masque:true,erreurs};
              await image.decode();
              const src=image.currentSrc;window.sourcesGraphiques ||= {};
              if(!window.sourcesGraphiques[src]) {const bitmap=await createImageBitmap(await (await fetch(src)).blob());window.sourcesGraphiques[src]={w:bitmap.width,h:bitmap.height};bitmap.close();}
              const native=window.sourcesGraphiques[src],r=rect(image),cs=getComputedStyle(image);
              const ratio=r.w/r.h,distorsion=Math.abs(ratio-native.w/native.h);
              if(distorsion>.01)erreurs.push('ratio de boîte différent de la source');
              if(cs.objectFit==='fill' && distorsion>.01)erreurs.push('distorsion');
              const densite=native.w/r.w;
              if(densite+.01<devicePixelRatio)erreurs.push('densité insuffisante');
              if(r.x<-.5||r.x+r.w>innerWidth+.5)erreurs.push('hors écran');
              const f=rect(el);if(r.x<f.x-1||r.x+r.w>f.x+f.w+1)erreurs.push('rognage horizontal');
              return {source:src.split('/').pop(),native,rendu:{w:r.w,h:r.h},densite,distorsion,erreurs};
            }
            const b=rect(el),nodes=[...el.querySelectorAll('.ai-node')],points=[...el.querySelectorAll('circle[r="4"]')],core=rect(el.querySelector('.ai-constellation-core'));
            const ancres=nodes.map((n,i)=>{const r=rect(n),p=rect(points[i]);const ecart=Math.hypot(r.x+r.w/2-p.x-p.w/2,r.y+r.h/2-p.y-p.h/2);if(ecart>2)erreurs.push('ancre '+n.textContent);if(r.x<b.x-1||r.x+r.w>b.x+b.w+1||r.y<b.y-1||r.y+r.h>b.y+b.h+1)erreurs.push('pastille hors cadre '+n.textContent);if(overlap(r,core))erreurs.push('pastille sur cœur '+n.textContent);if(n.scrollWidth>n.clientWidth+1)erreurs.push('texte rogné '+n.textContent);return ecart;});
            for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++)if(overlap(rect(nodes[i]),rect(nodes[j])))erreurs.push('pastilles superposées');
            return {ancres,erreurs};
          },target);
          const ligne={page:route,largeur,dpr,texte,disposition,mode,...mesures};report.releves.push(ligne);
          if(mesures.erreurs.length)report.erreurs.push(ligne);
          if(captures && dpr===2 && texte===130 && disposition==='equilibree' && mode==='normal' && [320,390,1280].includes(largeur)) {
            fs.mkdirSync(captures,{recursive:true});await (await page.$(target)).screenshot({path:path.join(captures,`${route}-${largeur}.png`)});
          }
        }
      }
      fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
      await page.close();console.log(route,dpr,report.releves.length,'relevés;',report.erreurs.length,'échecs');
    }
  } finally {await browser.close();}
  fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  console.log(`${report.releves.length} relevés, ${report.erreurs.length} échecs`);
  process.exitCode=report.erreurs.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=2;});
