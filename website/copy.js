document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',()=>{
  navigator.clipboard.writeText(b.getAttribute('data-copy'));
  const t=b.textContent;b.textContent='copied';setTimeout(()=>b.textContent=t,1200);
}));
