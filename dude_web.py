from flask import Flask, request, jsonify, render_template_string
import requests, base64, tempfile, os

app = Flask(__name__)
KEY = os.environ.get('GROQ_API_KEY', '')
H = []

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DUDE AI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#050505;color:#fff;font-family:'Raleway',sans-serif;height:100vh;display:flex;flex-direction:column;}
.header{background:#0a0a0a;border-bottom:1px solid #c9a84c44;padding:20px;text-align:center;}
.header h1{color:#c9a84c;font-size:28px;letter-spacing:12px;}
.header p{color:#c9a84c88;font-size:10px;letter-spacing:6px;}
.chat-box{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px;}
.msg-wrap{display:flex;flex-direction:column;gap:4px;}
.msg-wrap.user{align-items:flex-end;}
.msg-wrap.dude{align-items:flex-start;}
.label{font-size:9px;letter-spacing:3px;color:#c9a84c88;padding:0 4px;}
.msg{max-width:82%;padding:14px 18px;font-size:13px;line-height:1.8;}
.user .msg{background:linear-gradient(135deg,#1a1a2e,#16213e);border:1px solid #c9a84c66;border-radius:16px 16px 0 16px;color:#e8e8e8;}
.dude .msg{background:#111;border:1px solid #333;border-radius:16px 16px 16px 0;color:#c9a84c;}
.input-area{background:#0a0a0a;border-top:1px solid #c9a84c33;padding:16px;display:flex;gap:8px;align-items:center;}
.input-area input{flex:1;background:#0d0d0d;border:1px solid #2a2a2a;color:#fff;padding:13px 16px;border-radius:12px;font-size:13px;outline:none;}
.btn-send{background:linear-gradient(135deg,#c9a84c,#a07830);color:#000;border:none;padding:13px 20px;border-radius:12px;font-weight:700;cursor:pointer;}
.btn-icon{background:#0d0d0d;border:1px solid #c9a84c44;color:#c9a84c;padding:13px 14px;border-radius:12px;cursor:pointer;font-size:16px;}
.typing{display:flex;gap:4px;padding:14px 18px;background:#111;border:1px solid #333;border-radius:16px 16px 16px 0;width:fit-content;}
.typing span{width:6px;height:6px;background:#c9a84c;border-radius:50%;animation:bounce 1.2s infinite;}
.typing span:nth-child(2){animation-delay:.2s;}
.typing span:nth-child(3){animation-delay:.4s;}
@keyframes bounce{0%,60%,100%{transform:translateY(0);}30%{transform:translateY(-8px);}}
</style>
</head>
<body>
<div class="header">
<h1>DUDE</h1>
<p>PERSONAL AI FRIEND</p>
</div>
<div class="chat-box" id="chat">
<div class="msg-wrap dude">
<div class="label">DUDE</div>
<div class="msg">Yo! Gue Dude, AI lo yang siap bantu kapanpun. Lo bisa chat, kirim voice note, atau kirim foto buat gue analisis!</div>
</div>
</div>
<div class="input-area">
<button class="btn-icon" id="btnVn" onclick="toggleVN()">🎤</button>
<button class="btn-icon" onclick="document.getElementById('fileInput').click()">📷</button>
<input type="file" id="fileInput" accept="image/*" onchange="selectPhoto(this)" style="display:none">
<input type="text" id="inp" placeholder="Ketik pesan..." onkeypress="if(event.key==='Enter')send()">
<button class="btn-send" onclick="send()">KIRIM</button>
</div>
<script>
let mediaRec,audioChunks=[],isRec=false,selectedPhoto=null,selectedPhotoB64=null;
function selectPhoto(input){
const file=input.files[0];
if(!file)return;
const reader=new FileReader();
reader.onload=e=>{
selectedPhotoB64=e.target.result.split(',')[1];
selectedPhoto=file.name;
addMsg('user','📷 '+file.name);
};
reader.readAsDataURL(file);
input.value='';
}
async function send(){
const inp=document.getElementById('inp');
const msg=inp.value.trim();
if(!msg&&!selectedPhotoB64)return;
inp.value='';
if(selectedPhotoB64){
const photoB64=selectedPhotoB64;
const question=msg||'Jelaskan isi foto ini secara detail';
selectedPhoto=null;selectedPhotoB64=null;
showTyping();
const res=await fetch('/foto',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:photoB64,question})});
const data=await res.json();
hideTyping();
addMsg('dude',data.reply);
}else{
addMsg('user',msg);
showTyping();
const res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({msg})});
const data=await res.json();
hideTyping();
addMsg('dude',data.reply);
}
}
async function toggleVN(){
if(!isRec)await startRec();else stopRec();
}
async function startRec(){
try{
const stream=await navigator.mediaDevices.getUserMedia({audio:true});
mediaRec=new MediaRecorder(stream);
audioChunks=[];
mediaRec.ondataavailable=e=>{if(e.data.size>0)audioChunks.push(e.data);};
mediaRec.onstop=async()=>{
stream.getTracks().forEach(t=>t.stop());
const blob=new Blob(audioChunks,{type:'audio/webm'});
const reader=new FileReader();
reader.onload=async e=>{
const b64=e.target.result.split(',')[1];
addMsg('user','🎤 Voice note...');
showTyping();
try{
const res=await fetch('/vn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({audio:b64})});
const data=await res.json();
hideTyping();
if(data.transcript)addMsg('user','🎤 "'+data.transcript+'"');
addMsg('dude',data.reply);
}catch(e){hideTyping();addMsg('dude','Gagal proses VN!');}
};
reader.readAsDataURL(blob);
};
mediaRec.start(100);
isRec=true;
document.getElementById('btnVn').innerText='⏹️';
}catch(e){alert('Izinkan akses mikrofon!');}}
function stopRec(){if(mediaRec&&mediaRec.state!=='inactive')mediaRec.stop();isRec=false;document.getElementById('btnVn').innerText='🎤';}
function addMsg(who,text){
const chat=document.getElementById('chat');
const label=who==='user'?'LO':'DUDE';
chat.innerHTML+=`<div class="msg-wrap ${who}"><div class="label">${label}</div><div class="msg">${text.replace(/\\n/g,'<br>')}</div></div>`;
chat.scrollTop=chat.scrollHeight;
}
function showTyping(){
const chat=document.getElementById('chat');
chat.innerHTML+=`<div class="msg-wrap dude" id="typing"><div class="label">DUDE</div><div class="typing"><span></span><span></span><span></span></div></div>`;
chat.scrollTop=chat.scrollHeight;
}
function hideTyping(){document.getElementById('typing')?.remove();}
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
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":"Kamu adalah Dude, AI gaul yang cerdas. Jawab pakai bahasa lu gua, santai."}]+H[-20:]}, timeout=60)
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
            json={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"system","content":"Kamu adalah Dude, AI gaul yang cerdas."},{"role":"user","content":[{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img_b64}"}},{"type":"text","text":question}]}]}, timeout=60)
        r.raise_for_status()
        rep = r.json()["choices"][0]["message"]["content"]
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
                data={"model":"whisper-large-v3","language":"id"}, timeout=60)
        os.unlink(tmp_path)
        transcript = r.json().get("text","") if r.status_code==200 else ""
        if transcript:
            H.append({"role":"user","content":transcript})
            r2 = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},
                json={"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":"Kamu adalah Dude, AI gaul yang cerdas."}]+H[-20:]}, timeout=60)
            rep = r2.json()["choices"][0]["message"]["content"]
            H.append({"role":"assistant","content":rep})
            return jsonify({"transcript":transcript,"reply":rep})
        else:
            return jsonify({"reply":"Gue ga denger nih!"})
    except Exception as e:
        return jsonify({"reply":f"Error VN: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
