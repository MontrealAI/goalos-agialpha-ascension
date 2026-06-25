(()=>{"use strict";const q=(s,c=document)=>c.querySelector(s),qa=(s,c=document)=>[...c.querySelectorAll(s)];
const filters=qa("[data-pub-filter]"),cards=qa("[data-use-category]");
filters.forEach(button=>button.addEventListener("click",()=>{const value=button.dataset.pubFilter;filters.forEach(item=>item.setAttribute("aria-pressed",String(item===button)));cards.forEach(card=>{card.hidden=value!=="All"&&card.dataset.useCategory!==value})}));
qa("[data-copy-citation]").forEach(button=>button.addEventListener("click",async()=>{const target=q(button.dataset.copyCitation);if(!target)return;const value=target.textContent.trim();try{await navigator.clipboard.writeText(value);button.textContent="Citation copied";setTimeout(()=>button.textContent="Copy citation",1800)}catch{button.textContent="Select and copy";target.focus()}}));
})();
