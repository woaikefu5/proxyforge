#!/usr/bin/env python3
"""玄策 · 用户管理系统 v3.0
将此文件放到你的 VPS 上: /root/xuance.py
首次运行会自动提示配置服务器信息。
"""

import json, subprocess, re, os
from datetime import datetime, timedelta

# ========== 配置区（首次运行自动生成） ==========
CONF = "/etc/v2ray-agent/xray/conf/07_VLESS_vision_reality_inbounds.json"
HOST = "你的服务器IP"
PORT = "443"
FLOW = "xtls-rprx-vision"
PBK = "你的Reality公钥"
SNI = "www.java.com"
SID = "你的shortId"
DB = "/root/xuance_users.db"

CONFIG_FILE = "/root/xuance_config.json"

def first_run():
    """首次运行引导"""
    global HOST, PORT, FLOW, PBK, SNI, SID, CONF
    if os.path.exists(CONFIG_FILE):
        cfg = json.load(open(CONFIG_FILE))
        HOST = cfg.get("host", HOST)
        PORT = cfg.get("port", PORT)
        FLOW = cfg.get("flow", FLOW)
        PBK = cfg.get("pbk", PBK)
        SNI = cfg.get("sni", SNI)
        SID = cfg.get("sid", SID)
        if cfg.get("conf"):
            CONF = cfg["conf"]
        return
    print("\n=== 首次运行 · 配置 ===\n")
    HOST = input("  服务器IP: ").strip()
    PORT = input("  端口 (默认443): ").strip() or "443"
    PBK = input("  Reality公钥(pbk): ").strip()
    SNI = input("  回落SNI (默认www.java.com): ").strip() or "www.java.com"
    SID = input("  shortId: ").strip()
    cf = input(f"  Xray配置路径 (默认{CONF}): ").strip()
    if cf:
        CONF = cf
    json.dump({"host": HOST, "port": PORT, "flow": FLOW, "pbk": PBK, "sni": SNI, "sid": SID, "conf": CONF}, open(CONFIG_FILE, "w"), indent=2)
    print("  配置已保存到 " + CONFIG_FILE)
    print(f"  Xray配置: {CONF}")

# ========== 工具函数 ==========
def run(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()

def ld():
    d = {}
    if os.path.exists(DB):
        for l in open(DB).read().strip().split('\n'):
            p = l.strip().split('|')
            if len(p) >= 5:
                d[p[1]] = {'n': p[0], 'l': p[2], 'd': p[3], 'u': int(p[4])}
    return d

def sv(db):
    with open(DB, 'w') as f:
        for k, v in db.items():
            f.write(v['n'] + '|' + k + '|' + v['l'] + '|' + v['d'] + '|' + str(v['u']) + '\n')

def lu():
    d = json.load(open(CONF))
    db = ld()
    cs = d['inbounds'][1]['settings']['clients']
    print(f'\n  用户 ({len(cs)}):')
    for i, c in enumerate(cs):
        u = db.get(c['id'], {'u': 0, 'l': '?'})
        used = u['u'] // 1073741824
        limit = u['l'].replace('GB','')
        print(f'  {i+1}. {c["email"]:<25} {used}GB/{limit}GB')

def ad():
    n = input('  昵称: ').strip()
    l = input('  流量上限GB: ').strip()
    u = run('cat /proc/sys/kernel/random/uuid')
    d = json.load(open(CONF))
    d['inbounds'][1]['settings']['clients'].append({'id': u, 'email': n, 'flow': FLOW})
    json.dump(d, open(CONF, 'w'), indent=2)
    db = ld()
    db[u] = {'n': n, 'l': l, 'd': str(datetime.now().date()), 'u': 0}
    sv(db)
    a = '&'; h = '#'
    lk = f'vless://{u}@{HOST}:{PORT}?type=tcp{a}security=reality{a}flow={FLOW}{a}fp=chrome{a}pbk={PBK}{a}sni={SNI}{a}sid={SID}{h}{n}'
    print(f'\n  [完成] {n} ({l}GB)\n  {lk}')
    run('systemctl restart xray 2>/dev/null')

def dl():
    lu()
    x = input('  删哪个: ').strip()
    if not x: return
    d = json.load(open(CONF))
    idx = int(x) - 1
    uid = d['inbounds'][1]['settings']['clients'][idx]['id']
    del d['inbounds'][1]['settings']['clients'][idx]
    json.dump(d, open(CONF, 'w'), indent=2)
    db = ld()
    if uid in db: del db[uid]
    sv(db)
    print('  已删除')
    run('systemctl restart xray 2>/dev/null')

def ex():
    d = json.load(open(CONF))
    a = '&'; h = '#'
    print('\n  导出链接:')
    for c in d['inbounds'][1]['settings']['clients']:
        lk = f'vless://{c["id"]}@{HOST}:{PORT}?type=tcp{a}security=reality{a}flow={FLOW}{a}fp=chrome{a}pbk={PBK}{a}sni={SNI}{a}sid={SID}{h}{c["email"]}'
        print(f'  {lk}')

def cl():
    """检查：流量统计 + 超额/到期自动停"""
    # 流量统计
    db = ld()
    import re as _re
    logs = run('journalctl -u xray --no-pager --since "5 min ago" | grep accepted').split('\n')
    for l in logs:
        m = _re.search(r'email: (\S+)', l)
        if m:
            nm = m.group(1)
            for uid, v in db.items():
                if v['n'] == nm: v['u'] += 5242880
    sv(db)

    # 超额/到期检查
    d = json.load(open(CONF))
    db = ld()
    rm = False
    for c in d['inbounds'][1]['settings']['clients'][:]:
        v = db.get(c['id'])
        if v:
            over = float(v['l'].replace('GB', ''))
            usedGB = v['u'] // 1073741824
            try:
                reg = datetime.strptime(v['d'], '%Y-%m-%d')
                expired = datetime.now() > reg + timedelta(days=30)
            except:
                expired = False
            if usedGB >= over or expired:
                r = '超限' if usedGB >= over else '到期'
                d['inbounds'][1]['settings']['clients'].remove(c)
                if c['id'] in db: del db[c['id']]
                print(f'  [{r}] {c["email"]} 已停止')
                rm = True
    if rm:
        json.dump(d, open(CONF, 'w'), indent=2)
        sv(db)
        run('systemctl restart xray 2>/dev/null')
    else:
        print('  全部正常')

# ========== 主菜单 ==========
first_run()
print('  === 玄策 v3.0 ===')
while True:
    print('\n  1.查看  2.添加  3.删除  4.导出  5.检查  6.退出')
    c = input('  > ').strip()
    if c == '1': lu()
    elif c == '2': ad()
    elif c == '3': dl()
    elif c == '4': ex()
    elif c == '5': cl()
    elif c == '6': break
