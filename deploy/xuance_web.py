#!/usr/bin/env python3
import json, os, subprocess, uuid as uuid_mod
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB = "/root/xuance_users.json"
CFG = "/root/xuance_config.json"
XCF = "/etc/v2ray-agent/xray/config.json"
ADMIN_PASS = "admin123456"
PORT = 8318
SESS = {}

def ld():
    return json.load(open(DB)) if os.path.exists(DB) else {"version":4,"users":[]}
def sd(d): json.dump(d,open(DB,"w"),indent=2)
def lc(): return json.load(open(CFG))
def gb(b): return round(b/1073741824,2)
def ml(uid,name):
    c=lc()
    return "vless://"+uid+"@"+c["host"]+":"+c["port"]+"?type=tcp&security=reality&flow="+c.get("flow","xtls-rprx-vision")+"&fp=chrome&pbk="+c["pbk"]+"&sni="+c["sni"]+"&sid="+c["sid"]+"#"+name
def xa(uid,name):
    xc=json.load(open(XCF));f=lc().get("flow","xtls-rprx-vision")
    cl=xc["inbounds"][1]["settings"]["clients"]
    cl[:]=[c for c in cl if c["id"]!=uid]
    cl.append({"id":uid,"email":name,"flow":f})
    json.dump(xc,open(XCF,"w"),indent=2)
    subprocess.run("systemctl restart xray 2>/dev/null",shell=True)
def xd(uid):
    xc=json.load(open(XCF))
    xc["inbounds"][1]["settings"]["clients"][:]=[c for c in xc["inbounds"][1]["settings"]["clients"] if c["id"]!=uid]
    json.dump(xc,open(XCF,"w"),indent=2)
    subprocess.run("systemctl restart xray 2>/dev/null",shell=True)

A = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XuanCe Admin</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0f172a;color:#e2e8f0;font-family:-apple-system,system-ui,sans-serif;padding:20px}
h1{color:#38bdf8;margin-bottom:20px;font-size:22px}
.card{background:#1e293b;border-radius:12px;padding:20px;margin-bottom:20px}
.card h2{color:#94a3b8;margin-bottom:15px;font-size:15px}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end}
.fg{display:flex;flex-direction:column;gap:4px}
.fg label{font-size:12px;color:#64748b}
.fg input,.fg select{padding:8px 12px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:13px;width:120px}
.btn{padding:7px 16px;border-radius:8px;border:none;cursor:pointer;font-size:13px;font-weight:600}
.btn-add{background:#10b981;color:#fff}.btn-add:hover{background:#059669}
.btn-del{background:#ef4444;color:#fff;padding:4px 12px;font-size:11px}.btn-del:hover{background:#dc2626}
.btn-edit{background:#f59e0b;color:#000;padding:4px 12px;font-size:11px;margin-right:4px}.btn-edit:hover{background:#d97706}
.btn-cancel{background:#334155;color:#e2e8f0}
.btn-quick{color:#fff;padding:4px 10px;font-size:11px;margin:0 3px}
.btn-q1{background:#6366f1}.btn-q2{background:#8b5cf6}
table{width:100%;border-collapse:collapse;margin-top:10px}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #1e293b;font-size:13px}
th{color:#64748b;font-weight:600}
tr.sub{background:#1a2236}
tr.sub td:first-child{padding-left:28px}
.msg{padding:10px;border-radius:8px;margin:10px 0;display:none;font-size:13px}
.msg-ok{background:#064e3b;color:#6ee7b7}.msg-err{background:#7f1d1d;color:#fca5a5}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);z-index:100;justify-content:center;align-items:center}
.modal.show{display:flex}
.modal-box{background:#1e293b;border-radius:12px;padding:24px;width:400px;max-width:90%}
.modal-box h3{color:#38bdf8;margin-bottom:16px}
.modal-box label{font-size:12px;color:#64748b;display:block;margin-bottom:4px;margin-top:10px}
.modal-box input,.modal-box select{width:100%;padding:8px 12px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:13px}
.modal-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}
</style></head><body>
<h1>\u7384\u7b56 Web \u7ba1\u7406\u9762\u677f</h1>

<div class="card">
<h2>+ \u6dfb\u52a0\u4e3b\u8d26\u6237</h2>
<div class="row">
<div class="fg"><label>\u8d26\u6237\u540d</label><input id="f_name" placeholder="VIP001" required></div>
<div class="fg"><label>\u767b\u5f55\u7528\u6237\u540d</label><input id="f_user" required></div>
<div class="fg"><label>\u767b\u5f55\u5bc6\u7801</label><input id="f_pass" type="password" required></div>
<div class="fg"><label>\u6d41\u91cf(GB)</label><input id="f_limit" type="number" value="100" min="1" required></div>
<div class="fg"><label>\u6709\u6548\u671f(\u5929)</label><input id="f_days" type="number" value="30" min="1" required></div>
<button class="btn btn-add" id="btn_add">\u6dfb\u52a0</button>
</div>
<div class="msg" id="msg"></div>
</div>

<div class="card">
<h2>\u5168\u90e8\u8d26\u6237</h2>
<table><thead><tr><th>\u540d\u79f0</th><th>\u7c7b\u578b</th><th>\u9650\u989d</th><th>\u5df2\u7528</th><th>\u5230\u671f</th><th>\u72b6\u6001</th><th>\u5e26\u5bbd</th><th>\u64cd\u4f5c</th></tr></thead>
<tbody id="tbody">{ROWS}</tbody></table>
</div>

<div class="modal" id="edit_modal">
<div class="modal-box">
<h3>\u7f16\u8f91\u8d26\u6237</h3>
<input type="hidden" id="edit_uuid">
<label>\u8d26\u6237\u540d</label><input id="edit_name" readonly style="color:#64748b">
<label>\u6d41\u91cf(GB)</label><input id="edit_limit" type="number" min="1">
<label>\u65b0\u5bc6\u7801(\u7559\u7a7a\u4e0d\u6539)</label><input id="edit_pass" type="password">
<label>\u5230\u671f\u65e5\u671f</label><input id="edit_expiry" type="text">
<label>\u72b6\u6001</label><select id="edit_active"><option value="1">\u6b63\u5e38</option><option value="0">\u505c\u7528</option></select>
<div class="modal-actions">
<button class="btn btn-cancel" onclick="closeModal()">\u53d6\u6d88</button>
<button class="btn btn-add" id="btn_save">\u4fdd\u5b58</button>
</div>
</div></div>

<script>
function showMsg(t,c){var m=document.getElementById("msg");m.style.display="block";m.className="msg msg-"+c;m.textContent=t}
async function addUser(){
 var es=["f_name","f_user","f_pass","f_limit","f_days"];
 for(var i=0;i<es.length;i++){var v=document.getElementById(es[i]).value.trim();if(!v){showMsg("\u8bf7\u586b\u5199\u6240\u6709\u5b57\u6bb5","err");return}}
 var fd=new FormData();
 fd.set("name",document.getElementById("f_name").value.trim());
 fd.set("web_user",document.getElementById("f_user").value.trim());
 fd.set("web_pass",document.getElementById("f_pass").value.trim());
 fd.set("limit_gb",document.getElementById("f_limit").value);
 fd.set("expiry_days",document.getElementById("f_days").value);
 var r=await fetch("/api/admin/add",{method:"POST",body:new URLSearchParams(fd)});
 var j=await r.json();
 if(j.ok){showMsg("\u5df2\u6dfb\u52a0: "+j.name,"ok");setTimeout(function(){location.reload()},600)}
 else showMsg(j.error||"\u5931\u8d25","err");
}
function delUser(uid){if(!confirm("\u786e\u8ba4\u5220\u9664?"))return;fetch("/api/admin/delete",{method:"POST",body:new URLSearchParams({uuid:uid})}).then(function(r){return r.json()}).then(function(j){if(j.ok)location.reload();else alert("\u5931\u8d25")})}
function editUser(uid,name,lim,exp,act,pw){
 document.getElementById("edit_uuid").value=uid;
 document.getElementById("edit_name").value=name;
 document.getElementById("edit_limit").value=lim;
 document.getElementById("edit_expiry").value=exp;
 document.getElementById("edit_active").value=act?"1":"0";
 document.getElementById("edit_pass").value="";
 document.getElementById("edit_modal").classList.add("show");
}
function closeModal(){document.getElementById("edit_modal").classList.remove("show")}
async function saveEdit(){
 var fd=new FormData();
 fd.set("uuid",document.getElementById("edit_uuid").value);
 fd.set("limit_gb",document.getElementById("edit_limit").value);
 fd.set("expiry",document.getElementById("edit_expiry").value);
 fd.set("active",document.getElementById("edit_active").value);
 var pw=document.getElementById("edit_pass").value.trim();
 if(pw)fd.set("web_pass",pw);
 var r=await fetch("/api/admin/edit",{method:"POST",body:new URLSearchParams(fd)});
 var j=await r.json();
 if(j.ok){closeModal();location.reload()}
 else alert(j.error||"\u5931\u8d25");
}
document.getElementById("btn_add").onclick=addUser;
document.getElementById("btn_save").onclick=saveEdit;
document.addEventListener("keydown",function(e){if(e.key=="Escape")closeModal()});
// Quick action buttons
(function initQuickBtns(){
 var rows=document.querySelectorAll("#tbody tr:not(.sub)");
 for(var i=0;i<rows.length;i++){
  var td=rows[i].querySelector("td:last-child");
  if(!td)continue;
  var eb=td.querySelector(".btn-edit");
  if(!eb)continue;
  var m=eb.getAttribute("onclick").match(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/);
  if(!m)continue;
  var uid=m[0];
  var b1=document.createElement("button");
  b1.className="btn btn-quick btn-q1";b1.textContent="\u51451TB";
  b1.onclick=function(u){return function(){quickAct(u,"add_tb")}}(uid);
  var b2=document.createElement("button");
  b2.className="btn btn-quick btn-q2";b2.textContent="\u7eed1\u6708";
  b2.onclick=function(u){return function(){quickAct(u,"renew")}}(uid);
  td.insertBefore(b2,eb);td.insertBefore(b1,eb);
 }
 async function quickAct(uid,act){
  var fd=new FormData();fd.set("uuid",uid);fd.set("action",act);
  var r=await fetch("/api/admin/quick",{method:"POST",body:new URLSearchParams(fd)});
  var j=await r.json();if(j.ok)location.reload();else alert("fail");
 }
})();
</script></body></html>"""

U = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>User Panel</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0f172a;color:#e2e8f0;font-family:-apple-system,system-ui,sans-serif;padding:20px;max-width:800px;margin:0 auto}
h1{color:#38bdf8;margin-bottom:20px;font-size:20px}
.card{background:#1e293b;border-radius:12px;padding:20px;margin-bottom:15px}
.card h2{color:#94a3b8;margin-bottom:12px;font-size:14px}
.sr{display:flex;gap:15px;flex-wrap:wrap}
.st{background:#0f172a;border-radius:8px;padding:12px 16px;flex:1;min-width:110px}
.st .lbl{font-size:11px;color:#64748b}
.st .val{font-size:18px;font-weight:700;color:#38bdf8}
.bar-bg{background:#334155;border-radius:4px;height:8px;margin-top:8px;overflow:hidden}
.bar-fg{background:#10b981;height:100%;border-radius:4px}
table{width:100%;border-collapse:collapse;margin-top:10px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid #1e293b;font-size:13px}
th{color:#64748b;font-weight:600}
.btn{padding:6px 16px;border-radius:6px;border:none;cursor:pointer;font-size:12px;font-weight:600}
.btn-add{background:#10b981;color:#fff}
.btn-del{background:#ef4444;color:#fff;padding:3px 10px;font-size:11px}
.btn-qr{background:#8b5cf6;color:#fff;padding:3px 10px;font-size:11px}
.fr{display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-top:10px}
input{padding:7px 10px;border-radius:6px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:13px;width:110px}
.msg{padding:8px;border-radius:6px;margin:8px 0;display:none;font-size:12px}
.msg-ok{background:#064e3b;color:#6ee7b7}.msg-err{background:#7f1d1d;color:#fca5a5}
.lb{background:#0f172a;border-radius:6px;padding:6px 8px;font-size:11px;word-break:break-all;color:#94a3b8;margin-top:2px;max-width:400px;overflow-wrap:break-word;cursor:pointer}
.hidden{display:none}
.qp{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.75);display:flex;justify-content:center;align-items:center;z-index:100}
.qp img{max-width:320px;border-radius:12px;background:#fff;padding:10px}.badge-off{background:#7f1d1d;color:#fca5a5;font-size:10px;padding:1px 6px;border-radius:4px;margin-left:6px}
.btn-topup{background:#10b981;color:#fff;padding:3px 10px;font-size:11px;margin-left:4px}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);z-index:200;justify-content:center;align-items:center}
.modal.show{display:flex}
.modal-box{background:#1e293b;border-radius:12px;padding:24px;width:400px;max-width:90%}
.modal-box h3{color:#38bdf8;margin-bottom:16px}
.modal-box input{width:100%;padding:8px 12px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:13px}
.hidden{display:none}
</style></head><body>
<h1>\u7528\u6237\u9762\u677f</h1>

<div id="login_box" class="card">
<h2>\u767b\u5f55</h2>
<div class="fr">
<input id="l_user" placeholder="\u7528\u6237\u540d">
<input id="l_pass" type="password" placeholder="\u5bc6\u7801">
<button class="btn btn-add" id="btn_login">\u767b\u5f55</button>
</div>
<div class="msg" id="login_msg"></div>
</div>

<div id="dash" class="hidden">
<div class="card">
<h2>\u4e3b\u8d26\u6237: <span id="mn">-</span></h2>
<div class="sr">
<div class="st"><div class="lbl">\u603b\u9650\u989d</div><div class="val" id="ml">0 GB</div></div>
<div class="st"><div class="lbl">\u5df2\u7528</div><div class="val" id="mu">0 GB</div></div>
<div class="st"><div class="lbl">\u5269\u4f59</div><div class="val" id="mr">0 GB</div></div>
<div class="st"><div class="lbl">\u5230\u671f</div><div class="val" id="me" style="font-size:13px">-</div></div>
</div>
<div class="bar-bg"><div class="bar-fg" id="mb" style="width:0%"></div></div>
<div style="margin-top:12px;display:flex;gap:8px;align-items:center">
<span id="mlink" style="font-size:11px;color:#64748b;word-break:break-all;flex:1"></span>
<button class="btn btn-qr" id="btn_mqr">QR</button>
</div>
</div>

<div class="card">
<h2>\u5b50\u8d26\u6237</h2>
<table><thead><tr><th>\u540d\u79f0</th><th>\u9650\u989d</th><th>\u5df2\u7528</th><th>\u94fe\u63a5</th><th>\u64cd\u4f5c</th></tr></thead>
<tbody id="stb"></tbody></table>

<h2 style="margin-top:15px">+ \u65b0\u5efa\u5b50\u8d26\u6237</h2>
<div class="fr">
<input id="sn" placeholder="\u540d\u79f0">
<input id="sl" type="number" value="10" min="1" placeholder="\u6d41\u91cfGB">
<button class="btn btn-add" id="btn_asub">\u6dfb\u52a0</button>
</div>
<div class="msg" id="sm"></div>
</div>
</div>

<div id="topup_modal" class="modal">
  <div class="modal-box">
   <h3>\u5b50\u8d26\u6237\u52a0\u91cf</h3>
   <p style="color:#94a3b8;margin-bottom:8px">\u5b50\u8d26\u6237: <span id="tu_name"></span></p>
   <p style="color:#94a3b8;margin-bottom:12px">\u5f53\u524d\u6d41\u91cf: <span id="tu_cur"></span> GB</p>
   <input type="hidden" id="tu_uid"/>
   <input type="number" id="tu_amt" placeholder="\u8f93\u5165 GB" step="1" min="1"/>
   <button class="btn btn-topup" id="btn_topup_ok">确认加量</button>
   <button class="btn btn-del" id="btn_topup_cancel">取消</button>
  </div>
</div>
<div class="qp hidden" id="qp" onclick="this.classList.add('hidden')"><img id="qi"></div>

<script>
var token="";
document.getElementById("btn_login").onclick=async function(){
 var fd=new FormData();
 fd.set("web_user",document.getElementById("l_user").value.trim());
 fd.set("web_pass",document.getElementById("l_pass").value.trim());
 var r=await fetch("/api/user/login",{method:"POST",body:new URLSearchParams(fd)});
 var j=await r.json();
 var m=document.getElementById("login_msg");m.style.display="block";
 if(j.ok){token=j.token;document.getElementById("login_box").classList.add("hidden");document.getElementById("dash").classList.remove("hidden");load()}
 else{m.className="msg msg-err";m.textContent=j.error||"\u767b\u5f55\u5931\u8d25"}
};
async function load(){
 var r=await fetch("/api/user/stats?token="+token);var j=await r.json();
 if(j.error){alert(j.error);return}
 document.getElementById("mn").textContent=j.main.name;
 document.getElementById("ml").textContent=j.main.limit_gb+" GB";
 document.getElementById("mu").textContent=j.main.total_used_gb+" GB";
 document.getElementById("mr").textContent=j.remaining+" GB";
 document.getElementById("me").textContent=j.main.expiry;document.getElementById("mlink").textContent=j.main.link;document.getElementById("btn_mqr").onclick=function(){showQR(j.main.link)};document.getElementById("mlink").textContent=j.main.link;document.getElementById("btn_mqr").onclick=function(){showQR(j.main.link)};
 var p=Math.min(100,j.main.limit_gb>0?j.main.total_used_gb/j.main.limit_gb*100:0);
 document.getElementById("mb").style.width=p+"%";
 if(p>80)document.getElementById("mb").style.background="#f59e0b";
 if(p>95)document.getElementById("mb").style.background="#ef4444";
 var tb=document.getElementById("stb");tb.innerHTML="";
 if(!j.subs.length){tb.innerHTML="<tr><td colspan=5 style=color:#64748b>\u6682\u65e0\u5b50\u8d26\u6237</td></tr>"}
 for(var i=0;i<j.subs.length;i++){
  var s=j.subs[i];
  var tr=document.createElement("tr");
  var p2=s.limit_gb>0?Math.round(s.used_gb/s.limit_gb*100):0;
  var esc=s.link.replace(/'/g,"%27");
  var sb=s.active?"":" <span class=badge-off>已停用</span>";
  tr.innerHTML="<td>"+s.name+sb+"</td><td>"+s.limit_gb+"GB</td><td>"+s.used_gb+"GB ("+p2+"%)</td>"+
   "<td><div class=lb>"+s.link+"</div></td>"+
   "<td><button class=btn-topup data-uuid="+s.uuid+" data-name="+s.name+" data-limit="+s.limit_gb+">加量</button> "+
   "<button class=btn-qr data-link="+esc+">QR</button> "+
   "<button class=btn-del data-uuid="+s.uuid+">删除</button></td>";
tb.appendChild(tr);
 }
 var ls=tb.querySelectorAll(".lb");
 for(var i2=0;i2<ls.length;i2++){ls[i2].onclick=function(){navigator.clipboard.writeText(this.textContent);this.style.color="#10b981";setTimeout(function(){this.style.color="#94a3b8"}.bind(this),1000)};ls[i2].title="Click to copy"};
 var ls=tb.querySelectorAll(".lb");
 for(var i2=0;i2<ls.length;i2++){ls[i2].onclick=function(){navigator.clipboard.writeText(this.textContent);this.style.color="#10b981";setTimeout(function(){this.style.color="#94a3b8"}.bind(this),1000)};ls[i2].title="Click to copy"};
 var qs=tb.querySelectorAll(".btn-qr");
 for(var k=0;k<qs.length;k++){qs[k].onclick=function(){showQR(this.dataset.link)}}
 var ds=tb.querySelectorAll(".btn-del");
 for(var l=0;l<ds.length;l++){ds[l].onclick=async function(){
  if(!confirm("\u786e\u8ba4\u5220\u9664?"))return;
  var fd=new FormData();fd.set("token",token);fd.set("uuid",this.dataset.uuid);
  var r=await fetch("/api/user/delete_sub",{method:"POST",body:new URLSearchParams(fd)});
  var j=await r.json();if(j.ok)load();else alert(j.error);
 }}
 var ts=tb.querySelectorAll(".btn-topup");
 for(var t=0;t<ts.length;t++){ts[t].onclick=function(){
  document.getElementById("tu_uid").value=this.dataset.uuid;
  document.getElementById("tu_name").textContent=this.dataset.name;
  document.getElementById("tu_cur").textContent=this.dataset.limit;
  document.getElementById("tu_amt").value="";
  document.getElementById("topup_modal").classList.add("show");
 }}
}
function showQR(link){
 document.getElementById("qi").src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data="+encodeURIComponent(link);
 document.getElementById("qp").classList.remove("hidden");
}
document.getElementById("btn_asub").onclick=async function(){
 var nm=document.getElementById("sn").value.trim();
 var lm=document.getElementById("sl").value;
 if(!nm||!lm){return}
 var fd=new FormData();fd.set("token",token);fd.set("name",nm);fd.set("limit_gb",lm);
 var r=await fetch("/api/user/add_sub",{method:"POST",body:new URLSearchParams(fd)});
 var j=await r.json();var m=document.getElementById("sm");m.style.display="block";
 if(j.ok){m.className="msg msg-ok";m.textContent="\u5df2\u521b\u5efa: "+j.name;document.getElementById("sn").value="";load()}
 else{m.className="msg msg-err";m.textContent=j.error}
};

document.getElementById("btn_topup_cancel").onclick=function(){
  document.getElementById("topup_modal").classList.remove("show");
};
document.getElementById("btn_topup_ok").onclick=async function(){
  var amt=parseInt(document.getElementById("tu_amt").value);
  if(!amt||amt<=0){alert("\u8bf7\u8f93\u5165\u6709\u6548\u7684\u6d41\u91cf\u503c");return}
  var fd=new FormData();
  fd.set("token",token);
  fd.set("uuid",document.getElementById("tu_uid").value);
  fd.set("amount_gb",amt);
  var r=await fetch("/api/user/sub_topup",{method:"POST",body:new URLSearchParams(fd)});
  var j=await r.json();
  if(j.ok){document.getElementById("topup_modal").classList.remove("show");load()}
  else alert(j.error||"\u52a0\u91cf\u5931\u8d25");
};
</script></body></html>"""

LOGIN_PAGE="""<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XuanCe Login</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0f172a;color:#e2e8f0;font-family:-apple-system,system-ui,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh}
.box{background:#1e293b;border-radius:16px;padding:40px;width:360px;text-align:center}
h1{color:#38bdf8;font-size:22px;margin-bottom:8px}
.sub{color:#64748b;font-size:13px;margin-bottom:24px}
input{width:100%;padding:10px 14px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:14px;margin-bottom:12px}
.btn{width:100%;padding:10px;border-radius:8px;border:none;background:#10b981;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
.btn:hover{background:#059669}
.msg{font-size:12px;margin-top:12px;color:#fca5a5;display:none}
</style></head><body>
<div class="box">
<h1>XuanCe Admin</h1>
<p class="sub">Please enter admin password</p>
<form method="POST" action="/admin">
<input type="password" name="pass" placeholder="Password" required autofocus>
<button type="submit" class="btn">Login</button>
</form>
<p class="msg" id="m">Wrong password</p>
</div>
<script>
var p=new URLSearchParams(location.search);
if(p.get('e')=='1')document.getElementById('m').style.display='block';
</script>
</body></html>"""

class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _send(self,b,c=200,ct="text/html; charset=utf-8"):
        self.send_response(c);self.send_header("Content-Type",ct);self.end_headers()
        self.wfile.write(b.encode() if isinstance(b,str) else b)
    def _json(self,d,c=200): self._send(json.dumps(d,ensure_ascii=False),c,"application/json")
    def _body(self):
        n=int(self.headers.get("Content-Length",0));return parse_qs(self.rfile.read(n).decode())

    def do_GET(self):
        p=urlparse(self.path);qs=parse_qs(p.query)
        if p.path in ("/","/admin"):
            if SESS.get("admin_"+qs.get("sid",[""])[0])!="ok": self._send(LOGIN_PAGE,200);return
            data=ld()
            rows=""
            mains=sorted([u for u in data["users"] if not u.get("parent_uuid")],key=lambda x:x["name"])
            submap={}
            for u in data["users"]:
                pu=u.get("parent_uuid")
                if pu: submap.setdefault(pu,[]).append(u)
            for u in mains:
                sub_total = sum(s.get("used_bytes",0) for s in submap.get(u["uuid"],[])); use=gb(u.get("used_bytes",0)+sub_total); lim=u["limit_gb"];pct=round(use/lim*100,1) if lim>0 else 0
                act=u.get("active",True);st="\u6b63\u5e38" if act else "\u505c\u7528"
                exp=u.get("expiry_date","?")
                bw=str(u.get("bandwidth_mbps",30))
                rows+="<tr><td>"+u["name"]+"</td><td>\u4e3b</td><td>"+str(lim)+"GB</td><td>"+str(use)+"GB ("+str(pct)+"%)</td><td>"+exp+"</td><td>"+st+"</td><td>"+bw+"M</td><td><button class='btn btn-edit' onclick='editUser(\""+u["uuid"]+"\",\""+u["name"]+"\","+str(lim)+",\""+exp+"\","+str(int(act))+",\""+u.get("web_pass","")+"\")'>\u7f16\u8f91</button><button class='btn btn-del' onclick='delUser(\""+u["uuid"]+"\")'>\u5220\u9664</button></td></tr>"
                for s in sorted(submap.get(u["uuid"],[]),key=lambda x:x["name"]):
                    su=gb(s.get("used_bytes",0));sl=s["limit_gb"];sp=round(su/sl*100,1) if sl>0 else 0
                    sa=s.get("active",True);sst="\u6b63\u5e38" if sa else "\u505c\u7528"
                    rows+="<tr class='sub'><td>\u2514 "+s["name"]+"</td><td>\u5b50</td><td>"+str(sl)+"GB</td><td>"+str(su)+"GB ("+str(sp)+"%)</td><td>"+s.get("expiry_date","?")+"</td><td>"+sst+"</td><td>"+bw+"M</td><td><button class='btn btn-edit' onclick='editUser(\""+s["uuid"]+"\",\""+s["name"]+"\","+str(sl)+",\""+s.get("expiry_date","?")+"\","+str(int(sa))+",\"\")'>\u7f16\u8f91</button><button class='btn btn-del' onclick='delUser(\""+s["uuid"]+"\")'>\u5220\u9664</button></td></tr>"
            self._send(A.replace("{ROWS}",rows))
        elif p.path=="/user": self._send(U)
        elif p.path=="/api/user/stats":
            uid=SESS.get(qs.get("token",[""])[0])
            if not uid: self._json({"error":"\u672a\u767b\u5f55"},401);return
            data=ld()
            main=next((u for u in data["users"] if u["uuid"]==uid),None)
            if not main: self._json({"error":"\u8d26\u6237\u4e0d\u5b58\u5728"},404);return
            all_subs=[u for u in data["users"] if u.get("parent_uuid")==uid];active_subs=[s for s in all_subs if s.get("active",True)]
            sub_use=sum(s.get("used_bytes",0) for s in all_subs)
            total=main.get("used_bytes",0)+sub_use
            self._json({"main":{"name":main["name"],"limit_gb":main["limit_gb"],"total_used_gb":gb(total),"expiry":main.get("expiry_date","?"),"link":ml(main["uuid"],main["name"])},"subs":[{"name":s["name"],"uuid":s["uuid"],"limit_gb":s["limit_gb"],"active":s.get("active",True),"used_gb":gb(s.get("used_bytes",0)),"link":ml(s["uuid"],s["name"])} for s in all_subs],"remaining":round(main["limit_gb"]-sum(s["limit_gb"] for s in active_subs),2),"remaining_total":round(main["limit_gb"]-sum(s["limit_gb"] for s in all_subs),2)})
        else: self._send("Not Found",404)

    def do_POST(self):
        p=urlparse(self.path);b=self._body()
        if p.path in ("/","/admin") and len(b)==1 and list(b.keys())[0]=="pass":
            if b.get("pass",[""])[0]==ADMIN_PASS:
                sid=str(uuid_mod.uuid4());SESS["admin_"+sid]="ok"
                self.send_response(302);self.send_header("Location","/admin?sid="+sid);self.end_headers()
            else:
                self.send_response(302);self.send_header("Location","/admin");self.end_headers()
            return
        if p.path=="/api/admin/add":
            name=b.get("name",[""])[0].strip()
            wu=b.get("web_user",[""])[0].strip()
            wp=b.get("web_pass",[""])[0].strip()
            if not name or not wu or not wp: self._json({"error":"\u8bf7\u586b\u5199\u6240\u6709\u5b57\u6bb5"},400);return
            try: lg=float(b.get("limit_gb",["10"])[0]);ed=int(b.get("expiry_days",["30"])[0])
            except: self._json({"error":"\u6570\u5b57\u683c\u5f0f\u9519\u8bef"},400);return
            if lg<=0 or ed<=0: self._json({"error":"\u6d41\u91cf\u548c\u5929\u6570\u5fc5\u987b\u5927\u4e8e0"},400);return
            data=ld()
            if any(u["name"]==name for u in data["users"] if not u.get("parent_uuid")):
                self._json({"error":"\u540c\u540d\u8d26\u6237\u5df2\u5b58\u5728"},400);return
            if any(u.get("web_user")==wu for u in data["users"]):
                self._json({"error":"\u767b\u5f55\u7528\u6237\u540d\u5df2\u5b58\u5728"},400);return
            uid=str(uuid_mod.uuid4())
            exp=(datetime.now()+timedelta(days=ed)).strftime("%Y-%m-%d %H:%M:%S")
            data["users"].append({"uuid":uid,"name":name,"limit_gb":lg,"used_bytes":0,"reg_date":datetime.now().strftime("%Y-%m-%d"),"expiry_date":exp,"active":True,"parent_uuid":None,"web_user":wu,"web_pass":wp,"bandwidth_mbps":30})
            sd(data);xa(uid,name)
            self._json({"ok":True,"name":name})
        elif p.path=="/api/admin/quick":
            uid=b.get("uuid",[""])[0];act=b.get("action",[""])[0]
            data=ld()
            u=next((x for x in data["users"] if x["uuid"]==uid),None)
            if u:
                if act=="renew":
                    try: old=datetime.strptime(u["expiry_date"],"%Y-%m-%d %H:%M:%S")
                    except: old=datetime.now()
                    u["expiry_date"]=(old+timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                elif act=="add_tb": u["limit_gb"]+=1000
                sd(data)
                if u.get("active",True): xa(uid,u["name"])
                self._json({"ok":True,"action":act})
            else: self._json({"error":"not found"},404)
        elif p.path=="/api/admin/edit":
            uid=b.get("uuid",[""])[0]
            data=ld()
            u=next((x for x in data["users"] if x["uuid"]==uid),None)
            if not u: self._json({"error":"\u7528\u6237\u4e0d\u5b58\u5728"},404);return
            parent_uuid = u.get("parent_uuid")
            if parent_uuid:
                parent = next((x for x in data["users"] if x["uuid"]==parent_uuid), None)
                if parent:
                    try: new_limit = float(b.get("limit_gb",[str(u["limit_gb"])])[0])
                    except: new_limit = u["limit_gb"]
                    other_sum = sum(s["limit_gb"] for s in data["users"] if s.get("parent_uuid")==parent_uuid and s["uuid"]!=uid)
                    if new_limit + other_sum > parent["limit_gb"]:
                        rem = parent["limit_gb"] - other_sum
                        self._json({"error":"子账户超额! 主账户剩余 "+str(rem)+"GB"});return
                    ne_check = b.get("expiry",[""])[0].strip()
                    if ne_check and parent.get("expiry_date","") and ne_check > parent["expiry_date"]:
                        self._json({"error":"子账户到期日不能超过主账户: "+parent["expiry_date"]});return
            if not parent_uuid:
                try: new_limit = float(b.get("limit_gb",[str(u["limit_gb"])])[0])
                except: new_limit = u["limit_gb"]
                subs_sum = sum(s["limit_gb"] for s in data["users"] if s.get("parent_uuid")==uid)
                if new_limit < subs_sum:
                    self._json({"error":"主账户限额不能低于子账户已分配总额: "+str(subs_sum)+"GB"});return
            try: u["limit_gb"]=float(b.get("limit_gb",[str(u["limit_gb"])])[0])
            except: pass
            ne=b.get("expiry",[""])[0].strip()
            if ne: u["expiry_date"]=ne
            u["active"]=b.get("active",["1"])[0]=="1"
            np=b.get("web_pass",[""])[0].strip()
            if np: u["web_pass"]=np
            sd(data)
            if u["active"]: xa(uid,u["name"])
            else: xd(uid)
            self._json({"ok":True})
        elif p.path=="/api/admin/delete":
            uid=b.get("uuid",[""])[0]
            data=ld()
            data["users"]=[u for u in data["users"] if u["uuid"]!=uid and u.get("parent_uuid")!=uid]
            sd(data);xd(uid)
            self._json({"ok":True})
        elif p.path=="/api/user/login":
            wu=b.get("web_user",[""])[0].strip()
            wp=b.get("web_pass",[""])[0].strip()
            data=ld()
            main=next((u for u in data["users"] if not u.get("parent_uuid") and u.get("web_user")==wu and u.get("web_pass")==wp and u.get("active",True)),None)
            if not main: self._json({"error":"\u7528\u6237\u540d\u6216\u5bc6\u7801\u9519\u8bef"},401);return
            token=str(uuid_mod.uuid4());SESS[token]=main["uuid"]
            self._json({"ok":True,"token":token,"name":main["name"]})
        elif p.path=="/api/user/sub_topup":
            uid=SESS.get(b.get("token",[""])[0])
            if not uid: self._json({"error":"\u672a\u767b\u5f55"},401);return
            suid=b.get("uuid",[""])[0]
            try: amt=float(b.get("amount_gb",["5"])[0])
            except: self._json({"error":"\u53c2\u6570\u9519\u8bef"},400);return
            if amt<=0: self._json({"error":"\u52a0\u91cf\u5fc5\u987b\u5927\u4e8e0"},400);return
            data=ld()
            main=next((u for u in data["users"] if u["uuid"]==uid),None)
            sub=next((u for u in data["users"] if u["uuid"]==suid and u.get("parent_uuid")==uid),None)
            if not sub: self._json({"error":"\u53c2\u6570\u9519\u8bef"},404);return
            act_subs=[u for u in data["users"] if u.get("parent_uuid")==uid and u.get("active",True)]
            act_alloc=sum(s["limit_gb"] for s in act_subs)
            rem=main["limit_gb"]-act_alloc
            if amt>rem: self._json({"error":"\u6d41\u91cf\u4e0d\u8db3! \u5269\u4f59 "+str(rem)+"GB"},400);return
            sub["limit_gb"]+=amt
            sub["active"]=True
            sd(data)
            self._json({"ok":True,"new_limit":sub["limit_gb"]})
        elif p.path=="/api/user/add_sub":
            uid=SESS.get(b.get("token",[""])[0])
            if not uid: self._json({"error":"\u672a\u767b\u5f55"},401);return
            data=ld()
            main=next((u for u in data["users"] if u["uuid"]==uid),None)
            if not main: self._json({"error":"\u8d26\u6237\u4e0d\u5b58\u5728"},404);return
            sn=b.get("name",[""])[0].strip()
            if not sn: self._json({"error":"\u8bf7\u586b\u5199\u540d\u79f0"},400);return
            try: sl=float(b.get("limit_gb",["10"])[0])
            except: self._json({"error":"\u6570\u5b57\u683c\u5f0f\u9519\u8bef"},400);return
            if sl<=0: self._json({"error":"\u6d41\u91cf\u5fc5\u987b\u5927\u4e8e0"},400);return
            all_subs=[u for u in data["users"] if u.get("parent_uuid")==uid];active_subs=[s for s in all_subs if s.get("active",True)]
            if len(all_subs) >= 20: self._json({"error":"\u5b50\u8d26\u6237\u5df2\u8fbe\u4e0a\u965020\u4e2a"},400);return
            alloc=sum(s["limit_gb"] for s in all_subs)
            rem=main["limit_gb"]-alloc
            if sl>rem: self._json({"error":"\u6d41\u91cf\u6c60\u4e0d\u8db3! \u5269\u4f59 "+str(rem)+"GB"});return
            suid=str(uuid_mod.uuid4())
            data["users"].append({"uuid":suid,"name":sn,"limit_gb":sl,"used_bytes":0,"reg_date":datetime.now().strftime("%Y-%m-%d"),"expiry_date":main["expiry_date"],"active":True,"parent_uuid":uid})
            sd(data);xa(suid,sn)
            self._json({"ok":True,"link":ml(suid,sn),"name":sn})
        elif p.path=="/api/user/delete_sub":
            uid=SESS.get(b.get("token",[""])[0])
            if not uid: self._json({"error":"\u672a\u767b\u5f55"},401);return
            suid=b.get("uuid",[""])[0]
            data=ld()
            sub=next((u for u in data["users"] if u["uuid"]==suid and u.get("parent_uuid")==uid),None)
            if not sub: self._json({"error":"\u5b50\u8d26\u6237\u4e0d\u5b58\u5728"},404);return
            data["users"]=[u for u in data["users"] if u["uuid"]!=suid]
            sd(data);xd(suid)
            self._json({"ok":True})
        else: self._json({"error":"not found"},404)

if __name__=="__main__":
    HTTPServer(("0.0.0.0",PORT),H).serve_forever()
