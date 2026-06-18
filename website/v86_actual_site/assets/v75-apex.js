
(function(){
  document.querySelectorAll('[data-copy]').forEach(function(btn){btn.addEventListener('click',function(){var id=btn.getAttribute('data-copy'),el=document.getElementById(id);if(!el)return;var text=el.innerText||el.textContent;navigator.clipboard&&navigator.clipboard.writeText(text).then(function(){var old=btn.textContent;btn.textContent='Copied';setTimeout(function(){btn.textContent=old},1200)});});});
  var navLinks=document.querySelectorAll('.v75-section-nav a[href^="#"]');navLinks.forEach(function(a){a.addEventListener('click',function(e){var t=document.querySelector(a.getAttribute('href'));if(t){e.preventDefault();t.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}});});
})();
