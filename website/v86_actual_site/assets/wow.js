
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.revealer').forEach((el, i) => { if(reduce){ el.classList.add('in'); return; } });
  if(!reduce && 'IntersectionObserver' in window){
    const io = new IntersectionObserver((entries)=>entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }}),{threshold:.12});
    document.querySelectorAll('.revealer').forEach(el=>io.observe(el));
  } else { document.querySelectorAll('.revealer').forEach(el=>el.classList.add('in')); }
  const counters = document.querySelectorAll('[data-count]');
  counters.forEach(el=>{ const target = parseInt(el.getAttribute('data-count')||'0',10); if(reduce){el.textContent=target;return;} let n=0; const steps=48; const timer=setInterval(()=>{ n++; el.textContent=Math.round(target*n/steps); if(n>=steps) clearInterval(timer); },22); });
  const preview = document.getElementById('missionPreview');
  const presets = {
    buyers: {goal:'Get 3 buyer conversations for one tiny offer', metric:'3 real replies or booked conversations', proof:['offer draft','outreach list','reply screenshots','weekly decision note'], next:'Send 5 thoughtful messages today.'},
    career: {goal:'Book 3 serious interviews or improve one portfolio project', metric:'3 booked conversations or one published artifact', proof:['resume/portfolio before-after','outreach draft','reply screenshots','interview notes'], next:'Create one focused outreach message.'},
    refund: {goal:'Recover one refund, fix one bill, or resolve one support issue', metric:'reply, refund, correction, or escalation path', proof:['bill screenshot','support message draft','sent receipt','outcome note'], next:'Draft the cleanest support message.'},
    time: {goal:'Save 5 hours/week with one recurring workflow', metric:'documented time saved and reusable checklist', proof:['before workflow','new template','time estimate','weekly review'], next:'Pick one recurring annoyance.'},
    startup: {goal:'Validate one AI-startup wedge', metric:'10 demand signals or 3 buyer conversations', proof:['problem thesis','landing page','conversation notes','pricing test'], next:'Write the smallest offer page.'}
  };
  function renderMission(key){ if(!preview) return; const p = presets[key] || presets.buyers; preview.textContent = JSON.stringify({ mission_type:'GoalOS Autopilot Mission', goal:p.goal, success_metric:p.metric, evidence_to_collect:p.proof, risk_tier:'low/public-safe unless personal data is included', AGIALPHA_use:'Useful when coordinating contributors, reviewers, credentials, settlement readiness, or institutional memory.', next_action:p.next, claim_boundary:'This is a mission plan, not a guaranteed outcome.' }, null, 2); }
  document.querySelectorAll('[data-preset]').forEach(btn=>{btn.addEventListener('click',()=>{document.querySelectorAll('[data-preset]').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); renderMission(btn.dataset.preset);});});
  renderMission('buyers');
  const canvas = document.getElementById('proofField');
  if(canvas && !reduce){
    const ctx = canvas.getContext('2d'); let w=0,h=0,pts=[];
    const resize=()=>{w=canvas.width=canvas.offsetWidth*devicePixelRatio;h=canvas.height=canvas.offsetHeight*devicePixelRatio;pts=Array.from({length:58},()=>({x:Math.random()*w,y:Math.random()*h,vx:(Math.random()-.5)*.35*devicePixelRatio,vy:(Math.random()-.5)*.35*devicePixelRatio,r:(1+Math.random()*2)*devicePixelRatio}));};
    resize(); addEventListener('resize',resize);
    const tick=()=>{ctx.clearRect(0,0,w,h); for(const p of pts){p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>w)p.vx*=-1;if(p.y<0||p.y>h)p.vy*=-1;} for(let i=0;i<pts.length;i++){for(let j=i+1;j<pts.length;j++){const a=pts[i],b=pts[j],dx=a.x-b.x,dy=a.y-b.y,d=Math.hypot(dx,dy); if(d<150*devicePixelRatio){ctx.globalAlpha=(1-d/(150*devicePixelRatio))*.38; ctx.strokeStyle='#7ee9ff'; ctx.lineWidth=1*devicePixelRatio; ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();}}} ctx.globalAlpha=.9; for(const p of pts){ctx.fillStyle='#ffd66e';ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();} requestAnimationFrame(tick);}; tick();
  }
})();
