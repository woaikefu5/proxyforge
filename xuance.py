#!/usr/bin/env python3
"""玄策 · 用户管理系统 v4.1 — gRPC 精确流量 + 充值续费"""

import json, subprocess, os, sys, re
from datetime import datetime, timedelta

CONF = "/etc/v2ray-agent/xray/conf/07_VLESS_vision_reality_inbounds.json"
API_PORT = 62789
DB = "/root/xuance_users.json"
CONFIG_FILE = "/root/xuance_config.json"
OLD_DB = "/root/xuance_users.db"

HOST = PORT = FLOW = PBK = SNI = SID = ""
XRAY_BIN = "/etc/v2ray-agent/xray/xray"

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def run_get_exit(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.stdout.strip(), p.returncode

def load_server_config():
    global HOST, PORT, FLOW, PBK, SNI, SID, CONF
    if os.path.exists(CONFIG_FILE):
        cfg = json.load(open(CONFIG_FILE))
        HOST = cfg.get("host", "")
        PORT = cfg.get("port", "443")
        FLOW = cfg.get("flow", "xtls-rprx-vision")
        PBK = cfg.get("pbk", "")
        SNI = cfg.get("sni", "www.java.com")
        SID = cfg.get("sid", "")
        if cfg.get("conf"): CONF = cfg["conf"]
    if not HOST: first_run()

def first_run():
    global HOST, PORT, PBK, SNI, SID, CONF
    print("\n=== 首次运行 · 配置 ===\n")
    h = input("  服务器IP: ").strip()
    p = input("  端口 (默认443): ").strip() or "443"
    pbk = input("  Reality公钥(pbk): ").strip()
    sni = input("  回落SNI (默认www.java.com): ").strip() or "www.java.com"
    sid = input("  shortId: ").strip()
    cf = input(f"  Xray配置路径 (默认{CONF}): ").strip()
    HOST, PORT, PBK, SNI, SID = h, p, pbk, sni, sid
    if cf: CONF = cf
    json.dump({"host": h, "port": p, "flow": "xtls-rprx-vision", "pbk": pbk, "sni": sni, "sid": sid, "conf": CONF},
              open(CONFIG_FILE, "w"), indent=2)
    print("  配置已保存")

def load_db():
    if os.path.exists(DB): return json.load(open(DB))
    if os.path.exists(OLD_DB): return migrate_old_db()
    return {"version": 2, "users": []}

def save_db(data):
    json.dump(data, open(DB, "w"), indent=2)

def migrate_old_db():
    users = []
    xc = json.load(open(CONF))
    xray_emails = [c["email"] for c in xc["inbounds"][1]["settings"]["clients"]]
    for line in open(OLD_DB).read().strip().split("\n"):
        parts = line.strip().split("|")
        if len(parts) < 5: continue
        name = parts[0]
        if name not in xray_emails:
            print(f"  跳过: {name} (不在Xray配置中)"); continue
        try:
            reg = datetime.strptime(parts[3], "%Y-%m-%d")
            expiry = (reg + timedelta(days=30)).strftime("%Y-%m-%d")
        except:
            expiry = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        users.append({"uuid": parts[1], "name": name, "limit_gb": float(parts[2].replace("GB","")),
                       "used_bytes": int(parts[4]), "reg_date": parts[3], "expiry_date": expiry, "active": True})
    data = {"version": 2, "users": users}
    save_db(data); os.rename(OLD_DB, OLD_DB + ".bak")
    print(f"  已迁移 {len(users)} 个用户"); return data

def update_traffic(data):
    """通过 gRPC API 获取精确流量 (回退到日志估算)"""
    try:
        out = run(f"/usr/local/xray/xray api statsquery --server=127.0.0.1:{API_PORT}")
        stats = json.loads(out)
        user_bytes = {}
        for stat in stats.get("stat", []):
            name = stat.get("name", "")
            value = int(stat.get("value", 0))
            parts = name.split(">>>")
            if len(parts) >= 4 and parts[0] == "user" and parts[2] == "traffic":
                email = parts[1]
                user_bytes[email] = user_bytes.get(email, 0) + value
        for u in data["users"]:
            if u.get("name") in user_bytes and u.get("active", True):
                u["used_bytes"] = max(u.get("used_bytes", 0), user_bytes[u["name"]])
        return data
    except:
        pass
    # Fallback: log-based estimation
    try:
        out = run("journalctl -u xray --no-pager --since '5 min ago' 2>/dev/null | grep accepted")
        counts = {}
        for line in out.split("\n"):
            m = re.search(r'email: (\S+)', line)
            if m:
                e = m.group(1)
                counts[e] = counts.get(e, 0) + 1
        for u in data["users"]:
            if not u.get("active", True): continue
            cnt = counts.get(u["name"], 0)
            if cnt > 0:
                u["used_bytes"] += cnt * 5242880
    except: pass
    return data
def list_users(data):
    data = update_traffic(data)
    save_db(data)
    users = [u for u in data["users"] if u.get("active", True)]
    if not users: print("\n  暂无用户"); return
    print(f"\n  用户 ({len(users)}):")
    print(f"  {'#':<3} {'名称':<22} {'已用':<12} {'限额':<9} {'到期':<12} {'状态'}")
    print(f"  {'-'*62}")
    for i, u in enumerate(users, 1):
        gb = u["used_bytes"] / 1073741824
        lim = u["limit_gb"]
        pct = gb / lim * 100 if lim > 0 else 0
        try: expired = datetime.strptime(u.get("expiry_date","2099-01-01"), "%Y-%m-%d") < datetime.now()
        except: expired = False
        print(f"  {i:<3} {u['name']:<22} {gb:<7.2f}GB {pct:<4.1f}% {lim:<7.0f}GB {u.get('expiry_date','?'):<12} {'已过期' if expired else '正常'}")
    save_db(data)

def add_user(data):
    name = input("  昵称: ").strip()
    limit = input("  流量上限GB: ").strip()
    days = input("  有效期天数 (默认30): ").strip() or "30"
    uuid_val = run("cat /proc/sys/kernel/random/uuid")
    try:
        xc = json.load(open(CONF))
        xc["inbounds"][1]["settings"]["clients"].append({"id": uuid_val, "email": name, "flow": "xtls-rprx-vision", "level": 0})
        json.dump(xc, open(CONF, "w"), indent=2)
    except Exception as e:
        print(f"  [X] 配置更新失败: {e}"); return
    data["users"].append({"uuid": uuid_val, "name": name, "limit_gb": float(limit), "used_bytes": 0,
                           "reg_date": datetime.now().strftime("%Y-%m-%d"),
                           "expiry_date": (datetime.now() + timedelta(days=int(days))).strftime("%Y-%m-%d"),
                           "active": True})
    save_db(data)
    print(f"\n  [OK] {name} ({limit}GB / {days}天)")
    print(f"  {make_link(uuid_val, name)}")
    run("systemctl restart xray 2>/dev/null")

def delete_user(data):
    active = [u for u in data["users"] if u.get("active", True)]
    if not active: print("\n  暂无用户"); return
    print(f"\n  {'#':<3} {'名称':<25} {'UUID':<40}"); print(f"  {'-'*68}")
    for i, u in enumerate(active, 1): print(f"  {i:<3} {u['name']:<25} {u['uuid']}")
    idx = input("\n  删哪个: ").strip()
    if not idx: return
    try:
        i = int(idx) - 1
        target = active[i]
        xc = json.load(open(CONF))
        xc["inbounds"][1]["settings"]["clients"] = [c for c in xc["inbounds"][1]["settings"]["clients"] if c["id"] != target["uuid"]]
        json.dump(xc, open(CONF, "w"), indent=2)
        data["users"] = [u for u in data["users"] if u["uuid"] != target["uuid"]]
        save_db(data)
        print(f"  [OK] {target['name']} 已删除")
        run("systemctl restart xray 2>/dev/null")
    except: print("  [X] 无效选择")

def recharge_user(data):
    active = [u for u in data["users"] if u.get("active", True)]
    if not active: print("\n  暂无用户"); return
    print(f"\n  {'#':<3} {'名称':<22} {'已用':<12} {'限额':<10} {'到期':<12}")
    print(f"  {'-'*59}")
    for i, u in enumerate(active, 1):
        print(f"  {i:<3} {u['name']:<22} {u['used_bytes']/1073741824:<8.2f}GB {u['limit_gb']:<8.0f}GB {u.get('expiry_date','?'):<12}")
    idx = input("\n  充值哪个用户: ").strip()
    if not idx: return
    try:
        i = int(idx) - 1
        actual = next((u for u in data["users"] if u["uuid"] == active[i]["uuid"]), None)
        if not actual: return
        print(f"\n  用户: {actual['name']}")
        print(f"  当前限额: {actual['limit_gb']}GB  已用: {actual['used_bytes']/1073741824:.2f}GB  到期: {actual.get('expiry_date','?')}")
        add_gb = input("\n  充值流量 (GB): ").strip()
        add_days = input("  续费天数 (默认30): ").strip() or "30"
        actual["used_bytes"] = 0
        actual["limit_gb"] = float(add_gb)
        actual["expiry_date"] = (datetime.now() + timedelta(days=int(add_days))).strftime("%Y-%m-%d")
        save_db(data)
        print(f"\n  [OK] {actual['name']} 充值完成!")
        print(f"  新限额: {actual['limit_gb']}GB  到期: {actual['expiry_date']}")
        print(f"  {make_link(actual['uuid'], actual['name'])}")
    except: print("  [X] 无效选择")

def export_links(data):
    print()
    for u in data["users"]:
        if u.get("active", True): print(f"  {make_link(u['uuid'], u['name'])}")

def check_all(data):
    data = update_traffic(data)
    xc = json.load(open(CONF))
    clients = xc["inbounds"][1]["settings"]["clients"]
    changed = False
    for user in data["users"][:]:
        if not user.get("active", True): continue
        reason = None
        if user["used_bytes"] / 1073741824 >= user["limit_gb"]: reason = "超额"
        try:
            if datetime.strptime(user["expiry_date"], "%Y-%m-%d") < datetime.now(): reason = "到期"
        except: pass
        if reason:
            clients = [c for c in clients if c["id"] != user["uuid"]]
            user["active"] = False
            print(f"  [{reason}] {user['name']} 已停止"); changed = True
    if changed:
        xc["inbounds"][1]["settings"]["clients"] = clients
        json.dump(xc, open(CONF, "w"), indent=2); save_db(data)
        run("systemctl restart xray 2>/dev/null"); print("  Xray 已重启")
    else: print("  全部正常")

def make_link(uid, name):
    return f"vless://{uid}@{HOST}:{PORT}?type=tcp&security=reality&flow={FLOW}&fp=chrome&pbk={PBK}&sni={SNI}&sid={SID}#{name}"

def main():
    load_server_config()
    data = load_db()
    print("\n  === 玄策 v4.0 ===")
    while True:
        print("\n  1.查看  2.添加  3.删除  4.充值  5.导出  6.检查  7.退出")
        c = input("  > ").strip()
        if c == "1": list_users(data)
        elif c == "2": add_user(data)
        elif c == "3": delete_user(data)
        elif c == "4": recharge_user(data)
        elif c == "5": export_links(data)
        elif c == "6": check_all(data)
        elif c == "7": print("\n  Bye!\n"); break

if __name__ == "__main__":
    main()


