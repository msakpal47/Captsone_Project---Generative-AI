const apiBase = window.location.origin;
const chat = document.getElementById('chat');
const ingestBtn = document.getElementById('ingestBtn');
const askBtn = document.getElementById('askBtn');
const ingestStatus = document.getElementById('ingestStatus');

function addBubble(text, cls) {
  const el = document.createElement('div');
  el.className = `bubble ${cls}`;
  el.textContent = text;
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
}

ingestBtn.onclick = async () => {
  const path = document.getElementById('pdfPath').value;
  ingestStatus.textContent = 'Ingesting...';
  try {
    const res = await fetch(`${apiBase}/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(path ? path : null),
    });
    let data;
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      data = await res.json();
    } else {
      const txt = await res.text();
      data = { status: res.ok ? 'ok' : 'error', message: txt };
    }
    ingestStatus.textContent = data.status === 'ok' ? `Ready (${data.chunks} chunks)` : (data.message || 'Error');
  } catch (e) {
    ingestStatus.textContent = 'Network error during ingest';
  }
};

async function askOne(q) {
  addBubble(q, 'user');
  const thinking = document.createElement('div');
  thinking.className = 'bubble assistant';
  thinking.textContent = 'Thinking...';
  chat.appendChild(thinking);
  askBtn.disabled = true;
  try {
    const res = await fetch(`${apiBase}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q, session_id: 'web' }),
    });
    let data;
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      data = await res.json();
    } else {
      const txt = await res.text();
      data = { answer: txt || 'Error', sources: [] };
    }
    thinking.remove();
    addBubble(data.answer, 'assistant');
    if (data.sources && data.sources.length) {
      const s = document.createElement('div');
      s.className = 'source assistant';
      s.textContent = `Sources: ${data.sources.map(x => `${x.source}#${x.page}`).join(', ')}`;
      chat.appendChild(s);
    }
  } catch (e) {
    thinking.remove();
    addBubble('Request failed. Please check server is running.', 'assistant');
  } finally {
    askBtn.disabled = false;
  }
}

askBtn.onclick = async () => {
  const raw = document.getElementById('question').value;
  const parts = raw.split(/\r?\n|;/).map(s => s.trim()).filter(Boolean);
  if (!parts.length) return;
  for (const p of parts) {
    // eslint-disable-next-line no-await-in-loop
    await askOne(p);
  }
  document.getElementById('question').value = '';
};
