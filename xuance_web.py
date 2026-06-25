#!/usr/bin/env python3
import json,os,sys,secrets,time,subprocess
from http.server import HTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from datetime import datetime,timedelta
sys.path.insert(0,"/root")
import xuance
PORT=28081
sessions={}

def sh(cmd):
    return subprocess.run(cmd,shell=True,capture_output=True,text=True).stdout.strip()

def getp():
 f="/root/xuance_web_pass.json"
 if os.path.exists(f):return json.load(open(f)).get("pass","admin")
 return "admin"

def cks(c):
 t=""
 if c:
  for x in c.split(";"):
   x=x.strip()
   if x.startswith("xuance_token="):t=x.split("=",1)[1]
 if t in sessions and sessions[t]>time.time()-3600:
  sessions[t]=time.time();return True
 return False

CSS="body{font-family:system-ui,sans-serif;background:#0a0e13;color:#b4bcc6;margin:0;padding:0}.nav{background:#11161c;border-bottom:1px solid #1e242c;padding:12px 24px;display:flex;align-items:center;gap:20px}.nav h1{font-size:16px;color:#e8ecf1;margin:0}.nav a{color:#3b82f6;text-decoration:none;font-size:13px}.nav a:hover{text-decoration:underline}.main{padding:24px;max-width:1100px;margin:0 auto}.card{background:#11161c;border:1px solid #1e242c;border-radius:12px;padding:20px;margin-bottom:16px}.card h2{color:#e8ecf1;font-size:16px;margin:0 0 12px 0}.statgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}.stat{background:#11161c;border:1px solid #1e242c;border-radius:10px;padding:16px;text-align:center}.stat .num{font-size:26px;font-weight:700;color:#e8ecf1}.stat .lbl{font-size:11px;color:#5a6270;margin-top:4px;text-transform:uppercase}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:10px 14px;text-align:left;border-bottom:1px solid #1e242c}th{color:#5a6270;font-weight:500;font-size:11px;text-transform:uppercase}tr:hover{background:#161b22}input{background:#0a0e13;border:1px solid #1e242c;padding:10px 14px;border-radius:8px;color:#b4bcc6;font-size:13px;margin:4px}input:focus{outline:none;border-color:#3b82f6}.btn{background:#3b82f6;color:#fff;border:none;padding:10px 18px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:500}.btn:hover{opacity:0.85}.btn-danger{background:#ef4444}.btn-green{background:#10b981}.btn-purple{background:#8b5cf6}.btn-orange{background:#f59e0b;color:#000}.btn-ghost{background:transparent;color:#3b82f6;border:1px solid #3b82f644}.btn-sm{padding:5px 10px;font-size:11px}.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);z-index:100;justify-content:center;align-items:center}.modal.show{display:flex}.modal-box{background:#11161c;border:1px solid #1e242c;border-radius:16px;padding:24px;min-width:300px;max-width:500px}.modal-box h3{color:#e8ecf1;margin:0 0 12px 0}.qrcode{margin:12px auto;background:#fff;padding:12px;border-radius:12px;display:inline-block}.copied{color:#10b981;font-size:12px;margin-left:8px;opacity:0;transition:opacity .2s}.copied.show{opacity:1}"

class H(BaseHTTPRequestHandler):
 def log_message(s,*a):pass
 def _h(s,b):
  s.send_response(200);s.send_header("Content-Type","text/html;charset=utf-8");s.end_headers();s.wfile.write(b.encode())
 def _j(s,d):
  s.send_response(200);s.send_header("Content-Type","application/json");s.end_headers();s.wfile.write(json.dumps(d).encode())
 def _b(s):
  n=int(s.headers.get("Content-Length",0));return s.rfile.read(n).decode()if n else""

 def do_GET(s):
  p=urlparse(s.path).path;c=s.headers.get("Cookie","")
  if p=="/login":
   if cks(c):s.send_response(302);s.send_header("Location","/");s.end_headers()
   else:s._h(LOG)
   return
  if not cks(c):s.send_response(302);s.send_header("Location","/login");s.end_headers();return
  if p in("/","/dashboard"):
   xuance.load_server_config();d=xuance.load_db();d=xuance.update_traffic(d);xuance.save_db(d)
   act=[u for u in d["users"]if u.get("active",True)]
   tot=sum(u["limit_gb"]for u in act);wu=sum(u["used_bytes"]for u in act)/1073741824
   rows="".join("<tr><td>"+u["name"]+"</td><td>"+f"{u['used_bytes']/1073741824:.1f}GB</td><td>"+f"{u['limit_gb']:.0f}GB</td><td>"+u.get("expiry_date","?")+"</td></tr>"for u in act)
   mem=sh("free -h|grep Mem|awk '{print $3 FS $2}' FS=/")
   disk=sh("df -h /|tail -1|awk '{print $3 FS $2}' FS=/")
   upt=sh("uptime -p").replace("up ","")
   load=sh("uptime|grep -oP 'load average: .*'").replace("load average: ","")
   h="<!DOCTYPE html><html><head><meta charset=UTF-8><title>XuanCe</title><style>"+CSS+"</style></head><body><div class=nav><h1>XuanCe Panel</h1><a href=/>Dashboard</a><a href=/users>Users</a></div><div class=main>"
   h+="<h2 style=color:#e8ecf1>Dashboard</h2>"
   h+="<div class=statgrid>"
   h+="<div class=stat><div class=num>"+str(len(act))+"</div><div class=lbl>Users</div></div>"
   h+="<div class=stat><div class=num>"+f"{wu:.1f}GB</div><div class=lbl>Used</div></div>"
   h+="<div class=stat><div class=num>"+f"{tot:.0f}GB</div><div class=lbl>Limit</div></div>"
   h+="<div class=stat><div class=num>"+(f"{wu/tot*100:.1f}%"if tot>0 else"-")+"</div><div class=lbl>Usage</div></div>"
   h+="</div>"
   h+="<div class=card><h2>System</h2><table><tr><td>Uptime</td><td style=color:#e8ecf1>"+upt+"</td></tr><tr><td>Load</td><td style=color:#e8ecf1>"+load+"</td></tr><tr><td>Memory</td><td style=color:#e8ecf1>"+mem+"</td></tr><tr><td>Disk</td><td style=color:#e8ecf1>"+disk+"</td></tr></table></div>"
   h+="<div class=card><h2>Users</h2><table><tr><th>Name</th><th>Used</th><th>Limit</th><th>Expiry</th></tr>"+rows+"</table></div>"
   h+="</div></body></html>"
   s._h(h);return
  if p=="/users":
   xuance.load_server_config();d=xuance.load_db();d=xuance.update_traffic(d)
   act=[u for u in d["users"]if u.get("active",True)]
   sub_host="YOUR_SERVER_IP:28080"
   rows="".join("<tr><td>"+str(i+1)+"</td><td style=color:#e8ecf1>"+u["name"]+"</td><td>"+f"{u['used_bytes']/1073741824:.1f}GB</td><td>"+f"{u['limit_gb']:.0f}GB</td><td>"+u.get("expiry_date","?")+"</td><td><button onclick=rech("+str(i)+",'"+u['name']+"') class='btn btn-green btn-sm'>Recharge</button> <button onclick=showQR('"+u['name']+"') class='btn btn-purple btn-sm'>QR</button> <button onclick=showSub('"+u['name']+"') class='btn btn-orange btn-sm'>Sub</button> <button onclick=del("+str(i)+",'"+u['name']+"') class='btn btn-danger btn-sm'>Del</button></td></tr>"for i,u in enumerate(act))
   h="<!DOCTYPE html><html><head><meta charset=UTF-8><title>Users - XuanCe</title><style>"+CSS+"</style></head><body><div class=nav><h1>XuanCe Panel</h1><a href=/>Dashboard</a><a href=/users style=color:#e8ecf1>Users</a><button onclick=checkAll() class='btn btn-sm' style=margin-left:auto>Check All</button></div><div class=main>"
   h+="<h2 style=color:#e8ecf1>Users</h2>"
   h+="<div class=card><h2>Add User</h2><input id=n placeholder=Name><input id=g placeholder=GB type=number value=100><input id=d placeholder=Days type=number value=30><button class=btn onclick=add()>Add</button></div>"
   h+="<div class=card><h2>Active ("+str(len(act))+")</h2><table><tr><th>#</th><th>Name</th><th>Used</th><th>Limit</th><th>Expiry</th><th>Actions</th></tr>"+rows+"</table></div>"
   h+="<div class=modal id=rechModal><div class=modal-box><h3>Recharge: <span id=rechName></span></h3><input id=rechGB placeholder=GB type=number value=200><input id=rechDays placeholder=Days type=number value=30><br><button class=btn onclick=doRech()>Confirm</button> <button class='btn btn-ghost' onclick=document.getElementById('rechModal').classList.remove('show')>Cancel</button></div></div>"
   h+="<div class=modal id=qrModal><div class=modal-box style=text-align:center><h3 id=qrTitle></h3><div id=qrCode></div><br><button class='btn btn-ghost' onclick=document.getElementById('qrModal').classList.remove('show')>Close</button></div></div>"
   h+="<div class=modal id=subModal><div class=modal-box><h3>Subscription: <span id=subName></span></h3><p style=font-size:12px;color:#5a6270>Sub Host: "+sub_host+"</p><p style=color:#10b981;font-size:12px;cursor:pointer id=subClash onclick=copyText(this.textContent)>loading...</p><p style=color:#f59e0b;font-size:12px;cursor:pointer id=subSingbox onclick=copyText(this.textContent)>loading...</p><br><button class='btn btn-ghost' onclick=document.getElementById('subModal').classList.remove('show')>Close</button></div></div>"
   h+="</div><script src='https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js'></script><script>"
   h+="var rechIdx=0;var subHost='"+sub_host+"';"
   h+="async function add(){var b=JSON.stringify({name:document.getElementById('n').value,gb:parseFloat(document.getElementById('g').value),days:parseInt(document.getElementById('d').value)});var r=await fetch('/api/add',{method:'POST',body:b});var j=await r.json();alert(j.ok||j.error);location.reload()}"
   h+="async function del(i,n){if(!confirm('Delete '+n+'?'))return;var r=await fetch('/api/del',{method:'POST',body:JSON.stringify({idx:i})});var j=await r.json();alert(j.ok||j.error);location.reload()}"
   h+="function rech(i,n){rechIdx=i;document.getElementById('rechName').textContent=n;document.getElementById('rechModal').classList.add('show')}"
   h+="async function doRech(){var gb=parseFloat(document.getElementById('rechGB').value);var days=parseInt(document.getElementById('rechDays').value);var r=await fetch('/api/recharge',{method:'POST',body:JSON.stringify({idx:rechIdx,gb:gb,days:days})});var j=await r.json();alert(j.ok||j.error);document.getElementById('rechModal').classList.remove('show');location.reload()}"
   h+="async function checkAll(){var r=await fetch('/api/check',{method:'POST',body:'{}'});var j=await r.json();alert(j.ok||j.error);location.reload()}"
   h+="async function showQR(name){document.getElementById('qrTitle').textContent=name;var r=await fetch('/api/link?name='+encodeURIComponent(name));var j=await r.json();document.getElementById('qrCode').innerHTML='';if(j.link){new QRCode(document.getElementById('qrCode'),{text:j.link,width:220,height:220,colorDark:'#000',colorLight:'#fff'})}else{document.getElementById('qrCode').textContent='Error'}document.getElementById('qrModal').classList.add('show')}"
   h+="async function showSub(name){document.getElementById('subName').textContent=name;var cl='http://'+subHost+'/sub/'+encodeURIComponent(name)+'?format=clash';var sb='http://'+subHost+'/sub/'+encodeURIComponent(name)+'?format=singbox';document.getElementById('subClash').textContent=cl;document.getElementById('subSingbox').textContent=sb;document.getElementById('subModal').classList.add('show')}"
   h+="function copyText(t){navigator.clipboard.writeText(t).then(function(){alert('Copied!')})}"
   h+="</script></body></html>"
   s._h(h);return
  if p=="/api/link":
   name=parse_qs(urlparse(s.path).query).get("name",[""])[0]
   xuance.load_server_config();d=xuance.load_db()
   for u in d["users"]:
    if u["name"]==name:
     s._j({"link":xuance.make_link(u["uuid"],u["name"])});return
   s._j({"error":"Not found"})
   return
  s.send_response(404);s.end_headers()

 def do_POST(s):
  p=urlparse(s.path).path;c=s.headers.get("Cookie","")
  if p=="/login":
   b=s._b();pw=parse_qs(b).get("pass",[""])[0]
   if pw==getp():
    tok=secrets.token_hex(32);sessions[tok]=time.time()
    s.send_response(302);s.send_header("Set-Cookie","xuance_token="+tok+";Path=/;HttpOnly");s.send_header("Location","/");s.end_headers()
   else:s._h(LOG.replace("{error}","Wrong password"))
   return
  if not cks(c):s.send_response(403);s.end_headers();return
  r=json.loads(s._b())
  if p=="/api/add":
   n=r.get("name","").strip();gb=r.get("gb",0);days=r.get("days",30)
   if not n or gb<=0:s._j({"error":"Name+GB required"});return
   xuance.load_server_config();d=xuance.load_db();uid=xuance.run("cat /proc/sys/kernel/random/uuid")
   xc=json.load(open(xuance.CONF));xc["inbounds"][1]["settings"]["clients"].append({"id":uid,"email":n,"flow":"xtls-rprx-vision","level":0})
   json.dump(xc,open(xuance.CONF,"w"),indent=2)
   d["users"].append({"uuid":uid,"name":n,"limit_gb":float(gb),"used_bytes":0,"reg_date":datetime.now().strftime("%Y-%m-%d"),"expiry_date":(datetime.now()+timedelta(days=int(days))).strftime("%Y-%m-%d"),"active":True})
   xuance.save_db(d);xuance.run("systemctl restart xray 2>/dev/null");s._j({"ok":"Added "+n});return
  if p=="/api/del":
   i=r.get("idx",-1);d=xuance.load_db();act=[u for u in d["users"]if u.get("active",True)]
   if i<0 or i>=len(act):s._j({"error":"Bad index"});return
   t=act[i];xc=json.load(open(xuance.CONF))
   xc["inbounds"][1]["settings"]["clients"]=[c for c in xc["inbounds"][1]["settings"]["clients"]if c["id"]!=t["uuid"]]
   json.dump(xc,open(xuance.CONF,"w"),indent=2);d["users"]=[u for u in d["users"]if u["uuid"]!=t["uuid"]]
   xuance.save_db(d);xuance.run("systemctl restart xray 2>/dev/null");s._j({"ok":"Deleted "+t['name']});return
  if p=="/api/recharge":
   i=r.get("idx",-1);gb=r.get("gb",0);days=r.get("days",30)
   d=xuance.load_db();act=[u for u in d["users"]if u.get("active",True)]
   if i<0 or i>=len(act):s._j({"error":"Bad index"});return
   t=next((u for u in d["users"]if u["uuid"]==act[i]["uuid"]),None)
   if not t:s._j({"error":"Not found"});return
   t["used_bytes"]=0;t["limit_gb"]=float(gb)
   t["expiry_date"]=(datetime.now()+timedelta(days=int(days))).strftime("%Y-%m-%d")
   xuance.save_db(d);s._j({"ok":"Recharged "+t["name"]+" "+str(gb)+"GB/"+str(days)+"d"});return
  if p=="/api/check":
   d=xuance.load_db();d=xuance.update_traffic(d)
   xc=json.load(open(xuance.CONF));clients=xc["inbounds"][1]["settings"]["clients"]
   changed=False;msgs=[]
   for u in d["users"][:]:
    if not u.get("active",True):continue
    reason=None
    if u["used_bytes"]/1073741824>=u["limit_gb"]:reason="Over limit"
    try:
     if datetime.strptime(u["expiry_date"],"%Y-%m-%d")<datetime.now():reason="Expired"
    except:pass
    if reason:
     clients=[c for c in clients if c["id"]!=u["uuid"]]
     u["active"]=False;msgs.append(reason+": "+u["name"]);changed=True
   if changed:
    xc["inbounds"][1]["settings"]["clients"]=clients
    json.dump(xc,open(xuance.CONF,"w"),indent=2);xuance.save_db(d)
    xuance.run("systemctl restart xray 2>/dev/null")
    s._j({"ok":"Checked: "+", ".join(msgs)})
   else:s._j({"ok":"All users OK"})
   return
  s.send_response(404);s.end_headers()

LOG="""<!DOCTYPE html><html><head><meta charset=UTF-8><title>XuanCe Login</title><style>body{font-family:system-ui,sans-serif;background:#0a0e13;display:flex;justify-content:center;align-items:center;min-height:100vh;color:#b4bcc6;margin:0}.box{background:#11161c;padding:40px;border-radius:16px;width:90%;max-width:360px;border:1px solid #1e242c;text-align:center}.box h1{font-size:22px;color:#e8ecf1;margin-bottom:8px}.box p{font-size:13px;color:#5a6270;margin-bottom:24px}input{width:100%;padding:12px 16px;margin:8px 0;background:#0a0e13;border:1px solid #1e242c;border-radius:8px;color:#e8ecf1;font-size:14px;outline:none;box-sizing:border-box}input:focus{border-color:#3b82f6}.btn{width:100%;padding:12px;background:#3b82f6;color:#fff;border:none;border-radius:8px;font-size:14px;cursor:pointer;font-weight:600;margin-top:12px}.btn:hover{background:#2563eb}.err{color:#ef4444;font-size:13px;margin-top:8px}</style></head><body><div class=box><h1>XuanCe Panel</h1><p>Proxy Management System</p><form method=post action=/login><input type=password name=pass placeholder=Password autofocus><button class=btn type=submit>Login</button></form><div class=err>{error}</div></div></body></html>"""

if __name__=="__main__":
 print("XuanCe Web:"+str(PORT))
 HTTPServer(("0.0.0.0",PORT),H).serve_forever()

