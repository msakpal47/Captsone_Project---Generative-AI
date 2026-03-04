const messages = document.getElementById('messages');
const input = document.getElementById('msgInput');
const send = document.getElementById('sendBtn');
function addMsg(text, who){
  const d = document.createElement('div');
  d.className = `msg ${who}`;
  d.textContent = text;
  messages.appendChild(d);
  messages.scrollTop = messages.scrollHeight;
}
async function onSend(){
  const q = input.value.trim();
  if(!q) return;
  addMsg(q, 'user');
  input.value = '';
  addMsg('...', 'bot');
  try{
    const res = await window.TelecomAPI.chat(q, 4);
    messages.lastChild.textContent = res.answer;
  }catch(e){
    messages.lastChild.textContent = `Error: ${e.message || 'request failed'}`;
  }
}
if(send) send.addEventListener('click', onSend);
if(input) input.addEventListener('keydown', (e)=>{ if(e.key==='Enter') onSend(); });
