
(function(){
  "use strict";
  document.documentElement.classList.add("goalos-v86-js");
  function setupNav(){
    var candidates = Array.from(document.querySelectorAll("header nav, .top nav, nav"));
    candidates.forEach(function(nav){
      if(nav.dataset.v86Nav) return;
      var links = Array.from(nav.querySelectorAll("a"));
      if(links.length < 4) return;
      nav.dataset.v86Nav = "1";
      nav.classList.add("v86-nav-panel");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "v86-mobile-menu-button";
      btn.setAttribute("aria-expanded","false");
      btn.textContent = "Menu";
      nav.parentNode.insertBefore(btn, nav);
      btn.addEventListener("click", function(){
        var open = nav.classList.toggle("v86-open");
        btn.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });
  }
  function wrapTables(){
    document.querySelectorAll("table").forEach(function(t){
      if(t.closest(".v86-scroll-table")) return;
      var w = document.createElement("div");
      w.className = "v86-scroll-table";
      t.parentNode.insertBefore(w, t);
      w.appendChild(t);
    });
  }
  function aiCanvas(){
    if(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var c = document.createElement("canvas");
    c.className = "v86-ai-canvas";
    c.setAttribute("aria-hidden","true");
    document.body.prepend(c);
    var ctx = c.getContext("2d"), dpr=1, pts=[];
    function resize(){
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      c.width = Math.floor(window.innerWidth*dpr);
      c.height = Math.floor(window.innerHeight*dpr);
      c.style.width = window.innerWidth+"px";
      c.style.height = window.innerHeight+"px";
      ctx.setTransform(dpr,0,0,dpr,0,0);
      pts = Array.from({length: Math.min(80, Math.max(32, Math.floor(window.innerWidth/18)))}, function(_,i){
        return {x:Math.random()*window.innerWidth,y:Math.random()*window.innerHeight,r:1+Math.random()*2,vx:(Math.random()-.5)*.28,vy:(Math.random()-.5)*.28,h:i%3};
      });
    }
    function draw(){
      ctx.clearRect(0,0,window.innerWidth,window.innerHeight);
      var g=ctx.createRadialGradient(window.innerWidth*.62, window.innerHeight*.35, 20, window.innerWidth*.62, window.innerHeight*.35, Math.max(window.innerWidth,window.innerHeight)*.8);
      g.addColorStop(0,"rgba(122,255,215,.18)");
      g.addColorStop(.35,"rgba(126,200,255,.10)");
      g.addColorStop(1,"rgba(166,141,255,0)");
      ctx.fillStyle=g; ctx.fillRect(0,0,window.innerWidth,window.innerHeight);
      pts.forEach(function(p,idx){
        p.x+=p.vx; p.y+=p.vy;
        if(p.x<0||p.x>window.innerWidth) p.vx*=-1;
        if(p.y<0||p.y>window.innerHeight) p.vy*=-1;
        ctx.beginPath();
        ctx.fillStyle = p.h===0 ? "rgba(122,255,215,.7)" : p.h===1 ? "rgba(126,200,255,.55)" : "rgba(255,224,138,.55)";
        ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill();
        for(var j=idx+1;j<pts.length;j+=9){
          var q=pts[j], dx=p.x-q.x, dy=p.y-q.y, dist=Math.sqrt(dx*dx+dy*dy);
          if(dist<115){
            ctx.strokeStyle="rgba(255,255,255,"+(0.08*(1-dist/115))+")";
            ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y); ctx.stroke();
          }
        }
      });
      requestAnimationFrame(draw);
    }
    resize(); window.addEventListener("resize", resize, {passive:true}); draw();
  }
  function markFigures(){
    document.querySelectorAll("figure, .visual-shell, .diagram-frame, .figure-frame, .proof-card-visual").forEach(function(el){
      el.classList.add("v86-figure-safe");
    });
    document.querySelectorAll("img:not([alt])").forEach(function(img){ img.alt = "GoalOS AGIALPHA visual"; });
  }
  function boot(){ setupNav(); wrapTables(); markFigures(); aiCanvas(); }
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
