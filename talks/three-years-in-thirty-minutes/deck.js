let index=0,step=0;
const all=[...document.querySelectorAll('.slide')];
function fit(){const scale=Math.min(innerWidth/1600,innerHeight/900);const stage=document.querySelector('#stage');stage.style.transform=`scale(${scale})`;stage.style.left=(innerWidth-1600*scale)/2+'px';stage.style.top=(innerHeight-900*scale)/2+'px'}
function show(i){index=Math.max(0,Math.min(all.length-1,i));step=0;all.forEach((s,j)=>s.classList.toggle('active',j===index));all[index].querySelectorAll('.card,.phase').forEach(c=>c.classList.remove('shown'));document.querySelector('#progress').style.width=((index+1)/all.length*100)+'%';document.querySelector('#notes').textContent=data[index].notes;location.hash=String(index+1)}
function next(){const cards=[...all[index].querySelectorAll('.card')];if(step<cards.length){cards[step].classList.add('shown');all[index].querySelector(`.phase[data-phase="${step}"]`)?.classList.add('shown');step++}else show(index+1)}
function previous(){show(index-1)}
function revealAll(){all[index].querySelectorAll('.card,.phase').forEach(c=>c.classList.add('shown'));step=all[index].querySelectorAll('.card').length}
function notes(){document.querySelector('#notes').classList.toggle('visible')}
function motion(){document.body.classList.toggle('motion-off')}
function full(){if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen()}
document.addEventListener('keydown',e=>{if(['ArrowRight',' ','PageDown'].includes(e.key)){e.preventDefault();next()}else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();previous()}else if(e.key.toLowerCase()==='n')notes();else if(e.key.toLowerCase()==='m')motion();else if(e.key.toLowerCase()==='f')full();else if(e.key.toLowerCase()==='a')revealAll();else if(e.key==='Home')show(0);else if(e.key==='End')show(all.length-1)});
addEventListener('resize',fit);fit();show(Number(location.hash.slice(1)||1)-1);
