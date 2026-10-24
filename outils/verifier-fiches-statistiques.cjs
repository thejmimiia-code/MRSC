#!/usr/bin/env node
'use strict';
// Passe ciblée : géométrie des deux fiches, corrections ouvertes et texte agrandi.
const fs=require('node:fs'),path=require('node:path');
if(process.env.MRSC_BROWSER_NODE_MODULES){process.env.NODE_PATH=process.env.MRSC_BROWSER_NODE_MODULES;require('node:module').Module._initPaths();}
const puppeteer=require('puppeteer-core'),pkg=require('@sparticuz/chromium'),chromium=pkg.default||pkg;
(async()=>{
 const browser=await puppeteer.launch({executablePath:await chromium.executablePath(),args:chromium.args,headless:true});
 const releves=[];
 try{
  for(const id of ['maths-moyenne','maths-moyenne-mediane']){
   const page=await browser.newPage();
   await page.goto(new URL(`apprendre/fiches/${id}.html`,process.env.MRSC_TEST_URL||'http://127.0.0.1:4181/').href,{waitUntil:'networkidle0'});
   await page.addStyleTag({content:'*{animation:none!important;transition:none!important}'});
   await page.evaluate(()=>document.querySelectorAll('main details').forEach(el=>el.open=true));
   for(const largeur of [320,390,768,1280])for(const texte of [100,115,130])for(const disposition of ['equilibree','lecture','vitrine','mosaique','panorama','compacte'])for(const renforce of [false,true]){
    await page.setViewport({width:largeur,height:900,deviceScaleFactor:2});
    await page.evaluate(({texte,disposition,renforce})=>{const r=document.documentElement;r.dataset.layout=disposition;r.classList.toggle('texte-agrandi',texte===115);r.classList.toggle('texte-tres-agrandi',texte===130);r.classList.toggle('contraste-renforce',renforce);r.classList.toggle('espacement-renforce',renforce);},{texte,disposition,renforce});
    const erreurs=await page.evaluate(()=>{
     const erreurs=[];
     for(const el of document.querySelectorAll('main *')){
      if(!el.checkVisibility({checkVisibilityCSS:true})||el.closest('.visually-hidden,.sr-only'))continue;
      const r=el.getBoundingClientRect();
      if(r.width&& (r.left < -1||r.right>innerWidth+1))erreurs.push(el.tagName+' hors écran');
      if(el.clientWidth && el.scrollWidth>el.clientWidth+1 && ['hidden','clip'].includes(getComputedStyle(el).overflowX))erreurs.push(el.tagName+' contenu rogné');
     }
     if(!document.querySelector('main').textContent.includes('Prototype à relire'))erreurs.push('statut absent');
     return [...new Set(erreurs)];
    });
    releves.push({id,largeur,texte,disposition,renforce,erreurs});
   }
   await page.close();
  }
 }finally{await browser.close();}
 const erreurs=releves.filter(x=>x.erreurs.length);
 const sortie=process.env.MRSC_FICHES_JSON||'docs/rd/audit-fiches-statistiques-2026-10-24.json';fs.mkdirSync(path.dirname(sortie),{recursive:true});fs.writeFileSync(sortie,JSON.stringify({perimetre:'Deux fiches, main seulement, aide/correction ouvertes, densité 2. Géométrie et présence du statut ; ni lecteur d’écran ni compréhension.',releves,erreurs},null,2)+'\n');
 console.log(`${releves.length} relevés, ${erreurs.length} échecs`);process.exitCode=erreurs.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=2;});
