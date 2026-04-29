from flask import Flask, request, jsonify, render_template_string
import requests, base64, tempfile, os

app = Flask(__name__)
KEY = "YOUR_API_KEY"
H = []

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dude AI</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Raleway:wght@300;400;500&display=swap');
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#050505;color:#fff;font-family:'Raleway',sans-serif;height:100vh;display:flex;flex-direction:column;}
.header{background:#0a0a0a;border-bottom:1px solid #c9a84c44;padding:20px;text-align:center;}
.header h1{font-family:'Cinzel',serif;color:#c9a84c;font-size:28px;letter-spacing:12px;text-shadow:0 0 20px #c9a84c66;}
.header p{color:#c9a84c88;font-size:10px;letter-spacing:6px;margin-top:6px;}
.status{display:inline-flex;align-items:center;gap:6px;margin-top:8px;font-size:11px;color:#888;}
.status-dot{width:6px;height:6px;background:#4caf50;border-radius:50%;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.5;}}
.chat-box{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px;}
.msg-wrap{display:flex;flex-direction:column;gap:4px;}
.msg-wrap.user{align-items:flex-end;}
.msg-wrap.dude{align-items:flex-start;}
.label{font-size:9px;letter-spacing:3px;color:#c9a84c88;padding:0 4px;}
.msg{max-width:82%;padding:14px 18px;font-size:13px;line-height:1.8;}
.user .msg{background:linear-gradient(135deg,#1a1a2e,#16213e);border:1px solid #c9a84c66;border-radius:16px 16px 0 16px;color:#e8e8e8;}
.dude .msg{background:#111;border:1px solid #333;border-radius:16px 16px 16px 0;color:#c9a84c;}
.msg img{max-width:100%;border-radius:8px;margin-bottom:8px;}
.typing{display:flex;gap:4px;padding:14px 18px;background:#111;border:1px solid #333;border-radius:16px 16px 16px 0;width:fit-content;}
.typing span{width:6px;height:6px;background:#c9a84c;border-radius:50%;animation:bounce 1.2s infinite;}
.typing span:nth-child(2){animation-delay:.2s;}
.typing span:nth-child(3){animation-delay:.4s;}
@keyframes bounce{0%,60%,100%{transform:translateY(0);}30%{transform:translateY(-8px);}}
.input-area{background:#0a0a0a;border-top:1px solid #c9a84c33;padding:16px;display:flex;gap:8px;align-items:center;}
.input-area input[type=text]{flex:1;background:#0d0d0d;border:1px solid #2a2a2a;color:#fff;padding:13px 16px;border-radius:12px;font-family:'Raleway',sans-serif;font-size:13px;outline:none;}
.input-area input[type=text]:focus{border-color:#c9a84c66;}
.btn-send{background:linear-gradient(135deg,#c9a84c,#a07830);color:#000;border:none;padding:13px 20px;border-radius:12px;font-weight:700;cursor:pointer;letter-spacing:2px;font-size:12px;}
.btn-icon{background:#0d0d0d;border:1px solid #c9a84c44;color:#c9a84c;padding:13px 14px;border-radius:12px;cursor:pointer;font-size:16px;transition:all .3s;}
.btn-icon:hover{background:#c9a84c22;}
.btn-icon.recording{background:#c9a84c22;border-color:#c9a84c;animation:glow 1s infinite alternate;}
@keyframes glow{from{box-shadow:0 0 5px #c9a84c44;}to{box-shadow:0 0 15px #c9a84c88;}}
.preview-area{background:#0a0a0a;border-top:1px solid #c9a84c22;padding:10px 16px;display:none;align-items:center;gap:10px;}
.preview-area img{width:50px;height:50px;object-fit:cover;border-radius:8px;border:1px solid #c9a84c44;}
.preview-area span{font-size:12px;color:#c9a84c88;flex:1;}
.preview-area button{background:none;border:none;color:#c9a84c;font-size:18px;cursor:pointer;}
#fileInput{display:none;}
::-webkit-scrollbar{width:3px;}
::-webkit-scrollbar-thumb{background:#c9a84c44;border-radius:2px;}
</style>
</head>
<body>

<div id='lockScreen' style='position:fixed;top:0;left:0;width:100%;height:100%;background:#050505;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:999;padding:40px;'>
  <h2 style="font-family:'Cinzel',serif;color:#c9a84c;font-size:24px;letter-spacing:8px;margin-bottom:8px;">DUDE AI</h2>
  <p style='color:#888;font-size:11px;letter-spacing:4px;margin-bottom:40px;'>ENTER PASSWORD</p>
  <input type='password' id='passInput' placeholder='Password...' style='background:#0d0d0d;border:1px solid #c9a84c44;color:#fff;padding:16px 20px;border-radius:12px;font-size:16px;outline:none;width:100%;max-width:300px;text-align:center;margin-bottom:16px;' onkeypress="if(event.key==='Enter')checkPass()">
  <button onclick='checkPass()' style='background:linear-gradient(135deg,#c9a84c,#a07830);color:#000;border:none;padding:14px 40px;border-radius:12px;font-weight:700;cursor:pointer;font-size:14px;letter-spacing:3px;width:100%;max-width:300px;'>MASUK</button>
  <p id='passErr' style='color:#ff4444;font-size:12px;margin-top:16px;display:none;'>Password salah!</p>
</div>
<div class="header">
  <h1>DUDE</h1>
  <p>PERSONAL AI FRIEND</p>
  <div class="status"><span class="status-dot"></span> ONLINE</div>
</div>
<div class="chat-box" id="chat">
  <div class="msg-wrap dude">
    <div class="label">DUDE</div>
    <div class="msg">Yo! Gue Dude, AI lo yang siap bantu kapanpun. Lo bisa chat, kirim voice note, atau kirim foto buat gue analisis! 🔥</div>
  </div>
</div>
<div class="preview-area" id="previewArea">
  <img id="previewImg" src="" alt="preview">
  <span id="previewName">foto.jpg</span>
  <button onclick="clearPhoto()">✕</button>
</div>
<div class="input-area">
  <button class="btn-icon" id="btnVn" onclick="toggleVN()">🎤</button>
  <button class="btn-icon" onclick="document.getElementById('fileInput').click()">📷</button>
  <input type="file" id="fileInput" accept="image/*" onchange="selectPhoto(this)">
  <input type="text" id="inp" placeholder="Ketik pesan..." onkeypress="if(event.key==='Enter')send()">
  <button class="btn-send" onclick="send()">KIRIM</button>
</div>
<script>
let mediaRec, audioChunks=[], isRec=false, selectedPhoto=null, selectedPhotoB64=null;

function selectPhoto(input){
  const file = input.files[0];
  if(!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    selectedPhotoB64 = e.target.result.split(',')[1];
    selectedPhoto = file.name;
    document.getElementById('previewImg').src = e.target.result;
    document.getElementById('previewName').innerText = file.name;
    document.getElementById('previewArea').style.display = 'flex';
  };
  reader.readAsDataURL(file);
  input.value='';
}

function clearPhoto(){
  selectedPhoto=null; selectedPhotoB64=null;
  document.getElementById('previewArea').style.display='none';
}

async function send(){
  const inp = document.getElementById('inp');
  const msg = inp.value.trim();
  if(!msg && !selectedPhotoB64) return;
  inp.value='';

  if(selectedPhotoB64){
    const imgSrc = document.getElementById('previewImg').src;
    addMsgHTML('user', `<img src="${imgSrc}"><br>${msg||'Analisis foto ini'}`);
    const photoB64 = selectedPhotoB64;
    const question = msg || 'Jelaskan isi foto ini secara detail';
    clearPhoto();
    showTyping();
    const res = await fetch('/foto', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image:photoB64, question})});
    const data = await res.json();
    hideTyping();
    addMsg('dude', data.reply);
  } else {
    addMsg('user', msg);
    showTyping();
    const res = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({msg})});
    const data = await res.json();
    hideTyping();
    addMsg('dude', data.reply);
  }
}

async function toggleVN(){
  if(!isRec) await startRec(); else stopRec();
}

async function startRec(){
  try{
    const stream = await navigator.mediaDevices.getUserMedia({audio:true});
    mediaRec = new MediaRecorder(stream);
    audioChunks=[];
    mediaRec.ondataavailable=e=>{if(e.data.size>0)audioChunks.push(e.data);}
    mediaRec.onstop=async()=>{
      stream.getTracks().forEach(t=>t.stop());
      const blob=new Blob(audioChunks,{type:'audio/webm'});
      const reader=new FileReader();
      reader.onload=async()=>{
        const b64=reader.result.split(',')[1];
        addMsg('user','🎤 Voice note...');
        showTyping();
        try{
          const res=await fetch('/vn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({audio:b64})});
          const data=await res.json();
          hideTyping();
          if(data.transcript) addMsg('user','🎙 "'+data.transcript+'"');
          addMsg('dude',data.reply); speak(data.reply);
        }catch(e){hideTyping();addMsg('dude','Gagal proses VN, coba lagi!');}
      };
      reader.readAsDataURL(blob);
    };
    mediaRec.start(100);
    isRec=true;
    document.getElementById('btnVn').classList.add('recording');
    document.getElementById('btnVn').innerText='⏹';
  }catch(e){alert('Izinkan akses mikrofon!');}
}

function stopRec(){
  if(mediaRec&&mediaRec.state!=='inactive') mediaRec.stop();
  isRec=false;
  document.getElementById('btnVn').classList.remove('recording');
  document.getElementById('btnVn').innerText='🎤';
}

function addMsg(who, text){
  const chat=document.getElementById('chat');
  const label=who==='user'?'LO':'DUDE';
  chat.innerHTML+=`<div class="msg-wrap ${who}"><div class="label">${label}</div><div class="msg">${text.replace(/\\n/g,'<br>')}</div></div>`;
  chat.scrollTop=chat.scrollHeight;
}

function addMsgHTML(who, html){
  const chat=document.getElementById('chat');
  const label=who==='user'?'LO':'DUDE';
  chat.innerHTML+=`<div class="msg-wrap ${who}"><div class="label">${label}</div><div class="msg">${html}</div></div>`;
  chat.scrollTop=chat.scrollHeight;
}

function showTyping(){
  const chat=document.getElementById('chat');
  chat.innerHTML+=`<div class="msg-wrap dude" id="typing"><div class="label">DUDE</div><div class="typing"><span></span><span></span><span></span></div></div>`;
  chat.scrollTop=chat.scrollHeight;
}

function hideTyping(){document.getElementById('typing')?.remove();}

function speak(text){
  if('speechSynthesis' in window){
    window.speechSynthesis.cancel();
    const u=new SpeechSynthesisUtterance(text);
    u.lang='id-ID';
    u.rate=1;
    u.pitch=1;
    window.speechSynthesis.speak(u);
  }
}
</script>

<script>
var PASS = '1234';
function checkPass(){
  var p = document.getElementById('passInput').value;
  if(p === PASS){
    document.getElementById('lockScreen').style.display='none';
    localStorage.setItem('dudeAuth','yes');
  } else {
    document.getElementById('passErr').style.display='block';
    document.getElementById('passInput').value='';
  }
}
window.addEventListener('load', function(){
  if(localStorage.getItem('dudeAuth')==='yes'){
    document.getElementById('lockScreen').style.display='none';
  }
});
</script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    global H
    msg = request.json.get('msg','')
    H.append({"role":"user","content":msg})
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[
                {"role":"system","content":"Kamu adalah Dude, AI gaul yang cerdas. Jawab pakai bahasa lu gua, santai."}
            ]+H[-20:]}, timeout=60)
        r.raise_for_status()
        rep = r.json()["choices"][0]["message"]["content"]
        H.append({"role":"assistant","content":rep})
        return jsonify({"reply":rep})
    except Exception as e:
        H.pop()
        return jsonify({"reply":f"Error: {str(e)}"})

@app.route('/foto', methods=['POST'])
def foto():
    global H
    try:
        img_b64 = request.json.get('image','')
        question = request.json.get('question','Jelaskan isi foto ini')
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},
            json={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[
                {"role":"system","content":"Kamu adalah Dude, AI gaul yang cerdas. Jawab pakai bahasa lu gua, santai."},
                {"role":"user","content":[
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img_b64}"}},
                    {"type":"text","text":question}
                ]}
            ]}, timeout=60)
        r.raise_for_status()
        rep = r.json()["choices"][0]["message"]["content"]
        H.append({"role":"assistant","content":rep})
        return jsonify({"reply":rep})
    except Exception as e:
        return jsonify({"reply":f"Error foto: {str(e)}"})

@app.route('/vn', methods=['POST'])
def vn():
    global H
    try:
        audio_b64 = request.json.get('audio','')
        audio_bytes = base64.b64decode(audio_b64)
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        with open(tmp_path, 'rb') as f:
            r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization":f"Bearer {KEY}"},
                files={"file":("audio.webm", f, "audio/webm")},
                data={"model":"whisper-large-v3","language":"id"},
                timeout=60)
        os.unlink(tmp_path)
        transcript = r.json().get("text","") if r.status_code==200 else ""
        if transcript:
            H.append({"role":"user","content":transcript})
            r2 = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},
                json={"model":"llama-3.3-70b-versatile","messages":[
                    {"role":"system","content":"Kamu adalah Dude, AI gaul yang cerdas. Jawab pakai bahasa lu gua, santai."}
                ]+H[-20:]}, timeout=60)
            rep = r2.json()["choices"][0]["message"]["content"]
            H.append({"role":"assistant","content":rep})
            return jsonify({"transcript":transcript,"reply":rep})
        else:
            return jsonify({"reply":"Gue ga denger nih, coba ngomong lagi!"})
    except Exception as e:
        return jsonify({"reply":f"Error VN: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
