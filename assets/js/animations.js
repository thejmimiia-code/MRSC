'use strict';
(() => {
 const root=document.querySelector('.animation-lab');
 const play=document.getElementById('lab-play'),still=document.getElementById('lab-static'),angle=document.getElementById('lab-angle'),strength=document.getElementById('lab-strength'),status=document.getElementById('lab-status'),scene=document.getElementById('lab-scene');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let running=false,frame=0,start=0;
 const blocked=()=>still.checked||reduced.matches||Number(strength.value)===0;
 function view(v){root.style.setProperty('--view',blocked()?0:v*Number(strength.value)/100);}
 function tick(t){if(!start)start=t;view(Math.sin((t-start)/2400)*.7);frame=requestAnimationFrame(tick);}
 function update(){cancelAnimationFrame(frame);root.classList.toggle('lab-running',running&&!blocked());root.classList.toggle('lab-paused',document.hidden);play.setAttribute('aria-pressed',String(running&&!blocked()));play.textContent=running&&!blocked()?'Mettre en pause':'Lancer les animations';play.disabled=blocked();status.textContent=Number(strength.value)===0?'Intensité nulle : effets désactivés.':reduced.matches?'Mouvement réduit du système : effets désactivés.':still.checked?'Mode immobile : effets désactivés.':document.hidden?'Lecture suspendue : onglet masqué.':running?'Animations en cours. Vous pouvez mettre en pause à tout moment.':'Animations en pause. Le point de vue reste réglable.';if(running&&!blocked()&&!document.hidden){start=0;frame=requestAnimationFrame(tick);}else view(Number(angle.value)/100);}
 play.addEventListener('click',()=>{running=!running;update();});still.addEventListener('change',()=>{running=false;update();});reduced.addEventListener('change',()=>{running=false;update();});document.addEventListener('visibilitychange',update);
 strength.addEventListener('input',()=>{root.style.setProperty('--strength',strength.value/100);document.getElementById('lab-value').textContent=strength.value+' %';update();});
 angle.addEventListener('input',()=>{running=false;update();});scene.addEventListener('pointermove',e=>{if(e.pointerType!=='mouse'||running||blocked())return;const b=scene.getBoundingClientRect();angle.value=Math.round(((e.clientX-b.left)/b.width*2-1)*100);view(angle.value/100);});scene.addEventListener('pointerleave',()=>{if(!running){angle.value=0;view(0);}});
 document.getElementById('lab-reset').addEventListener('click',()=>{running=false;still.checked=false;angle.value=0;strength.value=50;root.style.setProperty('--strength',.5);document.getElementById('lab-value').textContent='50 %';update();});update();
})();
