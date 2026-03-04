window.TelecomAPI = (function(){
  const isHttp = typeof location !== 'undefined' && /^https?:/.test(location.protocol);
  const BASE = isHttp ? location.origin : 'http://localhost:8000';
  async function ingest(){
    const r = await fetch(`${BASE}/api/ingest`, {method:'POST'});
    if(!r.ok) throw new Error('ingest failed');
    return r.json();
  }
  async function chat(message, top_k){
    const r = await fetch(`${BASE}/api/chat`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message, top_k})
    });
    if(!r.ok){
      let t;
      try { t = await r.text(); } catch {}
      throw new Error(`HTTP ${r.status} ${r.statusText}${t ? ` - ${t}` : ''}`);
    }
    return r.json();
  }
  return {ingest, chat};
}());
