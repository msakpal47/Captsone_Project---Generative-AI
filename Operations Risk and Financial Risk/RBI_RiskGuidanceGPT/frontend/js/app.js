const API_BASE = window.location.origin && window.location.origin.startsWith("http") ? window.location.origin : "http://127.0.0.1:8020";
const askBtn = document.getElementById("askBtn");
const ingestBtn = document.getElementById("ingestBtn");
const questionEl = document.getElementById("question");
const statusEl = document.getElementById("status");
const chatEl = document.getElementById("chat");
let messages = [];
const STORAGE_KEY = "riskguidance_history";
function saveHistory(){
  try{ localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-200))); }catch(_){}
}
function loadHistory(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY);
    if(raw){
      const arr = JSON.parse(raw);
      if(Array.isArray(arr)){ messages = arr; }
    }
  }catch(_){}
}
loadHistory();

async function checkStatus(){
  try{
    const r = await fetch(API_BASE + "/status");
    const j = await r.json();
    if (j && j.ready) {
      const li = j.last_index || {};
      if (typeof li.indexed_chunks === "number" && li.indexed_chunks === 0) {
        statusEl.textContent = "No chunks indexed. Click Rebuild Index.";
      } else {
        statusEl.textContent = "Index ready";
      }
    } else {
      statusEl.textContent = "Index missing. Click Rebuild Index.";
    }
  }catch(e){
    try{
      const r2 = await fetch(API_BASE + "/health");
      const j2 = await r2.json();
      statusEl.textContent = j2 && j2.ok ? "Backend reachable, index unknown" : "Backend not reachable";
    }catch(e2){
      statusEl.textContent = "Backend not reachable";
    }
  }
}

function renderChat(){
  const html = messages.map((m, idx) => {
    const isUser = m.role === "user";
    const bubbleClass = isUser ? "bubble user" : "bubble assistant";
    let sourcesHtml = "";
    if (Array.isArray(m.sources) && m.sources.length) {
      const arr = m.sources.map(s => {
        if (typeof s === "string") return s;
        const src = s.source || "unknown";
        const pg = typeof s.page !== "undefined" ? ` (Page ${s.page})` : "";
        return `Source: ${src}${pg}`;
      });
      sourcesHtml = `<div class="sources"><strong>Sources:</strong><br>${arr.join("<br>")}</div>`;
    }
    const actions = !isUser ? `<div class="actions"><button class="copy-btn" data-idx="${idx}">Copy</button><button class="copy-btn" data-dl="${idx}">Download PDF</button></div>` : "";
    return `<div class="msg ${isUser ? "right" : "left"}">
              <div class="${bubbleClass}">
                <div class="answer">${m.typing ? `<div class="typing"><span></span><span></span><span></span></div>` : escapeHtml(m.text || "")}</div>
                ${sourcesHtml}
                ${actions}
              </div>
            </div>`;
  }).join("");
  chatEl.innerHTML = html;
  chatEl.scrollTop = chatEl.scrollHeight;
  saveHistory();
}

function escapeHtml(str){
  return str.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

async function ask(){
  const q = questionEl.value.trim();
  if(!q) return;
  messages.push({role:"user", text:q});
  renderChat();
  messages.push({role:"assistant", text:"", sources:[], typing:true});
  renderChat();
  askBtn.disabled = true;
  try{
    const url = API_BASE + "/ask-stream?question=" + encodeURIComponent(q) + "&k=4";
    const es = new EventSource(url);
    es.addEventListener("token", (ev) => {
      const cur = messages[messages.length - 1];
      cur.text = (cur.text || "") + (ev.data || "");
      cur.typing = false;
      renderChat();
    });
    es.addEventListener("sources", (ev) => {
      try{
        const srcs = JSON.parse(ev.data || "[]");
        messages[messages.length - 1].sources = Array.isArray(srcs) ? srcs : [];
        renderChat();
      }catch(_){}
    });
    es.addEventListener("end", () => {
      es.close();
      askBtn.disabled = false;
      questionEl.value = "";
      saveHistory();
    });
    es.onerror = async () => {
      try{
        es.close();
        const r = await fetch(API_BASE + "/ask", {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({question: q})
        });
        if(!r.ok){
          const t = await r.text();
          messages[messages.length - 1] = {role:"assistant", text:`Error (${r.status}): ${t}`, sources:[]};
          renderChat();
          askBtn.disabled = false;
          return;
        }
        const j = await r.json();
        messages[messages.length - 1] = {role:"assistant", text:j.answer, sources:Array.isArray(j.sources) ? j.sources : []};
        renderChat();
        questionEl.value = "";
        askBtn.disabled = false;
        saveHistory();
      }catch(e2){
        messages[messages.length - 1] = {role:"assistant", text:"Request failed", sources:[]};
        renderChat();
        askBtn.disabled = false;
      }
    };
  }catch(e){
    messages[messages.length - 1] = {role:"assistant", text:"Request failed", sources:[]};
    renderChat();
    askBtn.disabled = false;
  }
}

async function ingest(){
  statusEl.textContent = "Indexing PDFs...";
  try{
    const r = await fetch(API_BASE + "/ingest", {method:"POST"});
    if(!r.ok){
      const t = await r.text();
      statusEl.textContent = "Ingest failed: " + t;
      return;
    }
    const j = await r.json();
    if (typeof j.indexed_chunks === "number" && j.indexed_chunks > 0) {
      statusEl.textContent = `Indexed chunks: ${j.indexed_chunks}`;
    } else {
      const msg = (j && j.message) ? String(j.message) : "No chunks indexed. Check PDFs";
      statusEl.textContent = msg;
    }
    await checkStatus();
  }catch(e){
    statusEl.textContent = "Ingest failed";
  }
}

askBtn.addEventListener("click", ask);
ingestBtn.addEventListener("click", ingest);
questionEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    ask();
  }
});
questionEl.addEventListener("input", () => {
  questionEl.style.height = "auto";
  questionEl.style.height = Math.min(questionEl.scrollHeight, 280) + "px";
});
chatEl.addEventListener("click", (e) => {
  const btn = e.target.closest(".copy-btn");
  if(!btn) return;
  if (btn.dataset.idx) {
    const i = parseInt(btn.dataset.idx || "-1", 10);
    if (i >= 0 && i < messages.length) {
      const t = messages[i]?.text || "";
      if (t) { try{ navigator.clipboard.writeText(t); }catch(_){} }
    }
    return;
  }
  if (btn.dataset.dl) {
    const i = parseInt(btn.dataset.dl || "-1", 10);
    if (i >= 0 && i < messages.length) {
      const t = messages[i]?.text || "";
      const s = messages[i]?.sources || [];
      const html = `<html><head><meta charset="utf-8"><title>Answer</title></head><body style="font-family:Segoe UI,Roboto,sans-serif; padding:24px;"><h2>Answer</h2><div style="white-space:pre-wrap;line-height:1.6;">${escapeHtml(t)}</div>${Array.isArray(s)&&s.length?`<h3 style="margin-top:16px;">Sources</h3><div>${s.map(x=>typeof x==='string'?x:`Source: ${escapeHtml(x.source||'unknown')}${typeof x.page!=='undefined'?` (Page ${x.page})`:''}`).join('<br>')}</div>`:''}</body></html>`;
      const w = window.open("", "_blank");
      if (w) { w.document.write(html); w.document.close(); w.focus(); w.print(); }
    }
  }
});
if (messages.length === 0) {
  messages.push({role:"assistant", text:"Welcome. Ask your questions about RBI operational and financial risk."});
  renderChat();
}
checkStatus();
