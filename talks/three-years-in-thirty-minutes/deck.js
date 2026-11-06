let index=0,step=0,motionOff=matchMedia('(prefers-reduced-motion: reduce)').matches;
const all=[...document.querySelectorAll('.slide')];
function loadImages(){document.querySelectorAll('img[data-asset]').forEach(img=>{img.src=assets[motionOff?img.dataset.still:img.dataset.asset]})}
function fit(){const z=Math.min(innerWidth/1600,innerHeight/900),s=document.querySelector('#stage');s.style.transform=`scale(${z})`;s.style.left=(innerWidth-1600*z)/2+'px';s.style.top=(innerHeight-900*z)/2+'px'}
function show(n){index=Math.max(0,Math.min(all.length-1,n));step=0;all.forEach((s,i)=>s.classList.toggle('active',i===index));all[index].querySelectorAll('.reveal').forEach(e=>e.classList.remove('shown'));document.querySelector('#notes').textContent=slides[index].notes;location.hash=index+1}
function next(){const groups=[...new Set([...all[index].querySelectorAll('.reveal')].map(e=>Number(e.dataset.group)))].sort();if(step<groups.length){all[index].querySelectorAll(`[data-group="${groups[step++]}"]`).forEach(e=>e.classList.add('shown'))}else if(index!==13)show(index+1)}
function previous(){show(index-1)}function revealAll(){all[index].querySelectorAll('.reveal').forEach(e=>e.classList.add('shown'));step=99}
function toggleNotes(){document.querySelector('#notes').classList.toggle('visible')}
function toggleMotion(){motionOff=!motionOff;document.body.classList.toggle('motion-off',motionOff);loadImages()}
function appendix(){show(index>=14?13:14)}function full(){if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen()}
addEventListener('keydown',e=>{if(['ArrowRight',' ','PageDown'].includes(e.key)){e.preventDefault();next()}else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();previous()}else if(e.key.toLowerCase()==='a')revealAll();else if(e.key.toLowerCase()==='n')toggleNotes();else if(e.key.toLowerCase()==='m')toggleMotion();else if(e.key.toLowerCase()==='r')appendix();else if(e.key.toLowerCase()==='f')full();else if(e.key==='Home')show(0);else if(e.key==='End')show(13)});
matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',e=>{motionOff=e.matches;document.body.classList.toggle('motion-off',motionOff);loadImages()});
loadImages();document.body.classList.toggle('motion-off',motionOff);addEventListener('resize',fit);fit();show(Number(location.hash.slice(1)||1)-1);
