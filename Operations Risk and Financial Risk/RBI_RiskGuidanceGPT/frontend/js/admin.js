const API = window.location.origin;
const statsEl = document.getElementById("stats");
const statusEl = document.getElementById("status");
async function load() {
  try{
    const s = await fetch(API + "/status").then(r=>r.json());
    statusEl.textContent = s && s.ready ? "Index ready" : "Index missing";
    const a = await fetch(API + "/admin/stats").then(r=>r.json());
    const q = await fetch(API + "/admin/queries").then(r=>r.json());
    const files = (a.last_index && a.last_index.files) || [];
    const ic = (a.last_index && a.last_index.indexed_chunks) || 0;
    const html = `
      <div class="bubble assistant">
        <div><strong>Indexed Chunks:</strong> ${ic}</div>
        <div style="margin-top:8px;"><strong>Files:</strong><br>${files.map(x=>x).join("<br>")}</div>
        <div style="margin-top:12px;"><strong>Recent Queries:</strong><br>${q.map(x=>`${x.ts} — ${x.question} ${x.category?`(${x.category})`:''}`).slice(0,20).join("<br>")}</div>
      </div>
    `;
    statsEl.innerHTML = html;
  }catch(e){
    statsEl.innerHTML = "<div class='bubble assistant'>Failed to load analytics</div>";
  }
}
load();
