
(function(){
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const reveal = () => document.querySelectorAll('.reveal').forEach(el => {
    const r = el.getBoundingClientRect(); if(r.top < window.innerHeight * .86) el.classList.add('in');
  });
  window.addEventListener('scroll', reveal, {passive:true}); reveal();
  document.querySelectorAll('[data-count]').forEach(el=>{ const target=+el.dataset.count; if(reduce){el.textContent=target; return;} let n=0; const step=Math.max(1,Math.ceil(target/40)); const t=setInterval(()=>{n+=step; if(n>=target){n=target; clearInterval(t);} el.textContent=n;},28); });
  const data={
    buyers:{goal:'Get 3 buyer conversations',proof:'screenshots of outreach + replies + learning notes',metric:'3 conversations booked or 10 honest rejections',next:'write one offer sentence and send 10 messages'},
    career:{goal:'Book 3 serious interviews',proof:'resume version + outreach log + interview confirmations',metric:'3 interviews or 20 targeted applications',next:'rewrite resume for one role and send 5 applications'},
    refund:{goal:'Recover one refund or fix one bill',proof:'bill screenshot + drafted message + support reply',metric:'refund, correction, escalation, or documented decision',next:'upload the bill and draft the clearest support message'},
    time:{goal:'Save 5 hours per week',proof:'before/after task list + automated checklist',metric:'one recurring workflow reduced or delegated',next:'choose one weekly annoyance and turn it into steps'},
    startup:{goal:'Validate one AI-startup wedge',proof:'landing page + 10 demand signals + buyer notes',metric:'3 qualified buyers or 1 paid/pilot signal',next:'publish one narrow offer and ask 20 people'}
  };
  function updateMission(){ const sel=document.getElementById('missionSelect'), out=document.getElementById('missionPreview'); if(!sel||!out) return; const m=data[sel.value]||data.buyers; out.textContent=JSON.stringify({goal:m.goal,success_metric:m.metric,proof_to_collect:m.proof,privacy_boundary:'keep private data out of public proof; publish only safe summary',evidence_docket:['goal','action','artifact','proof','review','next decision'],next_action:m.next,claim_boundary:'experimental mission packet; no guaranteed outcome'}, null, 2); }
  document.getElementById('missionSelect')?.addEventListener('change', updateMission); updateMission();
  const canvas=document.getElementById('proofField'); if(!canvas||reduce) return; const ctx=canvas.getContext('2d'); let w,h,pts=[];
  function resize(){w=canvas.width=window.innerWidth; h=canvas.height=canvas.offsetHeight||window.innerHeight; pts=Array.from({length:Math.min(90,Math.floor(w/18))},()=>({x:Math.random()*w,y:Math.random()*h,vx:(Math.random()-.5)*.35,vy:(Math.random()-.5)*.35,r:Math.random()*1.9+0.6}));}
  function frame(){ctx.clearRect(0,0,w,h); for(const p of pts){p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>w)p.vx*=-1;if(p.y<0||p.y>h)p.vy*=-1;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle='rgba(255,255,255,.72)';ctx.fill();} for(let i=0;i<pts.length;i++){for(let j=i+1;j<pts.length;j++){const a=pts[i],b=pts[j],dx=a.x-b.x,dy=a.y-b.y,d=Math.sqrt(dx*dx+dy*dy); if(d<110){ctx.strokeStyle='rgba(51,198,212,'+(1-d/110)*.22+')';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}}} requestAnimationFrame(frame);} resize(); window.addEventListener('resize',resize); frame();
})();
