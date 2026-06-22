#!/usr/bin/env python3
"""ProxyForge - Xray + Card Generator"""

import os, sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from proxyforge.config import load_config, save_config
from proxyforge.protocols import gen_uuid, make_link, SUPPORTED_PROTOCOLS
from proxyforge.cardgen import generate_customer_card
from proxyforge.xray import ensure_xray, is_installed

C = {"G": "\033[0;32m", "C": "\033[0;36m", "R": "\033[0;31m", "Y": "\033[0;33m", "W": "\033[0m"}
def c(tag, text): return f"{C.get(tag, '')}{text}{C['W']}"

def banner():
    print()
    print(c("C", "=" * 42))
    print(c("C", "   ProxyForge v1.2.0"))
    print(c("C", "   Xray / Card Generator"))
    print(c("C", "=" * 42))
    print()

def setup_wizard():
    cfg = load_config()
    print(c("Y", "\n[?] First Run - Quick Setup\n"))
    cfg["brand"]["name"] = input("  Brand name: ").strip() or "MyNode"
    cfg["brand"]["contact"] = input("  Contact (Telegram/etc): ").strip() or "@me"
    save_config(cfg)
    print(c("G", "\n  [OK] Config saved\n"))

def add_server_menu():
    cfg = load_config()
    print(c("Y", "\n[+] Add Server\n"))
    sid = input("  Server ID (english): ").strip()
    host = input("  Server IP: ").strip()
    if not sid or not host:
        print(c("R", "  [X] Cannot be empty"))
        return
    cfg.setdefault("servers", {})[sid] = {"host": host, "inbounds": []}
    save_config(cfg)
    print(c("G", f"\n  [OK] Server {sid} ({host}) added\n"))

def add_inbound_menu():
    cfg = load_config()
    servers = cfg.get("servers", {})
    if not servers:
        print(c("R", "\n  [X] Add a server first"))
        return
    print(c("Y", "\n[+] Select Server:\n"))
    sids = list(servers.keys())
    for i, sid in enumerate(sids):
        print(f"  {i+1}. {sid} ({servers[sid]['host']})")
    try:
        si = int(input("\n  Which: ")) - 1
        sid = sids[si]
    except:
        print(c("R", "  [X] Invalid"))
        return
    print(c("Y", "\n[+] Select Protocol:\n"))
    protos = list(SUPPORTED_PROTOCOLS.keys())
    for i, p in enumerate(protos):
        print(f"  {i+1}. {SUPPORTED_PROTOCOLS[p]['name']}")
    try:
        pi = int(input("\n  Which: ")) - 1
        proto = protos[pi]
    except:
        print(c("R", "  [X] Invalid"))
        return
    print(c("C", f"\n  Protocol: {SUPPORTED_PROTOCOLS[proto]['name']}\n"))
    port = input("  Port: ").strip()
    remark = input("  Remark (english): ").strip() or "default"
    user_uuid = gen_uuid()
    print(f"  UUID (auto): {user_uuid}")
    inbound = {"tag": f"{proto}-{remark}", "protocol": proto, "port": int(port) if port else 443, "uuid": user_uuid, "remark": remark}
    if proto == "vless-reality":
        inbound["public_key"] = input("  Reality pubkey (pbk): ").strip()
        inbound["server_name"] = input("  Fallback SNI: ").strip() or "www.java.com"
        inbound["short_id"] = input("  shortId: ").strip()
        inbound["flow"] = input("  flow: ").strip() or "xtls-rprx-vision"
    elif proto in ("vless-ws-tls", "vmess"):
        inbound["server_name"] = input("  SNI: ").strip()
        inbound["path"] = input("  WS path: ").strip() or "/"
    elif proto == "vless-grpc":
        inbound["server_name"] = input("  SNI: ").strip()
        inbound["service_name"] = input("  gRPC service: ").strip()
    elif proto == "trojan":
        inbound["password"] = input("  Password: ").strip() or gen_uuid()[:16]
        inbound["server_name"] = input("  SNI: ").strip()
    elif proto == "ss":
        inbound["method"] = input("  Cipher: ").strip() or "aes-256-gcm"
        inbound["password"] = input("  Password: ").strip() or gen_uuid()[:16]
    host = servers[sid]["host"]
    link = make_link(proto, **{**inbound, "host": host, "remark": remark})
    inbound["sample_link"] = link
    cfg["servers"][sid].setdefault("inbounds", []).append(inbound)
    save_config(cfg)
    print(c("G", f"\n  [OK] Inbound added!"))
    print(c("C", f"\n  Sample link:\n  {link}\n"))

def gen_card_menu():
    cfg = load_config()
    servers = cfg.get("servers", {})
    if not servers:
        print(c("R", "\n  [X] Add a server + inbound first"))
        return
    sids = list(servers.keys())
    print(c("Y", "\n[+] Select Server:\n"))
    for i, sid in enumerate(sids):
        print(f"  {i+1}. {sid} ({servers[sid]['host']})")
    try:
        si = int(input("\n  > ")) - 1
        server = servers[sids[si]]
    except:
        print(c("R", "  [X] Cancel"))
        return
    inbounds = server.get("inbounds", [])
    if not inbounds:
        print(c("R", "\n  [X] No inbounds on this server"))
        return
    print(c("Y", "\n[+] Select Inbound:\n"))
    for i, ib in enumerate(inbounds):
        print(f"  {i+1}. {ib['tag']}")
    try:
        ii = int(input("\n  > ")) - 1
        ib = inbounds[ii]
    except:
        print(c("R", "  [X] Cancel"))
        return
    name = input("\n  Customer name: ").strip()
    packages = cfg.get("packages", [])
    print(c("Y", "\n[+] Select Package:\n"))
    for i, pkg in enumerate(packages):
        print(f"  {i+1}. {pkg['name']} - {pkg['traffic']}/month - Y{pkg['price']}")
    print(f"  {len(packages)+1}. Custom")
    try:
        pi = int(input("\n  > ")) - 1
        if pi == len(packages):
            traffic = input("  Traffic (e.g. 100GB): ").strip()
            price = input("  Price (e.g. 25): ").strip()
            pkg = {"name": "Custom", "traffic": traffic, "price": int(price), "duration": "month"}
        else:
            pkg = packages[pi]
    except:
        print(c("R", "  [X] Cancel"))
        return
    user_uuid = gen_uuid()
    host = server["host"]
    proto = ib["protocol"]
    link_args = {"host": host, "remark": name}
    for k in ("port", "public_key", "server_name", "short_id", "flow", "path", "service_name", "network", "password", "method"):
        if k in ib:
            link_args[k] = ib[k]
    link_args["user_uuid"] = user_uuid
    link = make_link(proto, **link_args)
    desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
    card_path, qr_path = generate_customer_card(
        name=name, uuid=user_uuid, link=link, package_info=pkg,
        brand_name=cfg["brand"]["name"], contact=cfg["brand"]["contact"],
        output_dir=desktop,
        features=["Unlimited devices", "Global streaming"],
    )
    print(c("G", f"\n  [OK] Card: {card_path}"))
    print(c("G", f"  [OK] QR:   {qr_path}"))
    print(c("C", f"\n  Link:\n  {link}\n"))
    if sys.platform == "win32":
        os.startfile(card_path)

def list_servers_menu():
    cfg = load_config()
    servers = cfg.get("servers", {})
    if not servers:
        print(c("Y", "\n  No servers yet. Use option 1 to add one."))
        return
    for sid, svr in servers.items():
        print(c("C", f"\n  [{sid}] {svr['host']}"))
        for ib in svr.get("inbounds", []):
            print(f"    - {ib['tag']}  :{ib.get('port','?')}")

def package_menu():
    """Manage packages"""
    cfg = load_config()
    packages = cfg.get("packages", [])
    while True:
        print(c("Y", "\n[*] Package Management\n"))
        if packages:
            for i, pkg in enumerate(packages):
                print(f"  {i+1}. {pkg['name']:<10} {pkg['traffic']}/month  Y{pkg['price']}")
        else:
            print(c("R", "  No packages defined yet"))
        print("\n  1. Add  2. Edit  3. Delete  4. Back")
        ch = input("\n  > ").strip()
        if ch == "1":
            name = input("  Name (e.g. Light): ").strip()
            traffic = input("  Traffic (e.g. 100GB): ").strip()
            price = input("  Price (e.g. 25): ").strip()
            packages.append({"name": name, "traffic": traffic, "price": int(price), "duration": "month"})
            cfg["packages"] = packages
            save_config(cfg)
            print(c("G", f"\n  [OK] {name} added"))
        elif ch == "2":
            if not packages:
                print(c("R", "  Nothing to edit"))
                continue
            idx = input(f"  Edit which (1-{len(packages)}): ").strip()
            try:
                i = int(idx) - 1
                pkg = packages[i]
                name = input(f"  Name [{pkg['name']}]: ").strip() or pkg['name']
                traffic = input(f"  Traffic [{pkg['traffic']}]: ").strip() or pkg['traffic']
                price = input(f"  Price [{pkg['price']}]: ").strip() or str(pkg['price'])
                packages[i] = {"name": name, "traffic": traffic, "price": int(price), "duration": "month"}
                cfg["packages"] = packages
                save_config(cfg)
                print(c("G", f"\n  [OK] {name} updated"))
            except:
                print(c("R", "  [X] Invalid"))
        elif ch == "3":
            if not packages:
                print(c("R", "  Nothing to delete"))
                continue
            idx = input(f"  Delete which (1-{len(packages)}): ").strip()
            try:
                i = int(idx) - 1
                name = packages[i]["name"]
                del packages[i]
                cfg["packages"] = packages
                save_config(cfg)
                print(c("G", f"\n  [OK] {name} deleted"))
            except:
                print(c("R", "  [X] Invalid"))
        elif ch == "4":
            break

def vps_deploy_menu():
    """VPS one-click deploy helper"""
    cfg = load_config()
    servers = cfg.get("servers", {})
    
    print(c("C", "\n" + "=" * 50))
    print(c("C", "   VPS One-Click Deploy"))
    print(c("C", "=" * 50))
    
    print(c("Y", "\n[Step 1] SSH into your VPS\n"))
    print("  ssh root@your-vps-ip")
    
    print(c("Y", "\n[Step 2] Run this one-liner:\n"))
    print(c("G", "  bash <(curl -sL https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/install.sh)"))
    
    print(c("Y", "\n[Step 3] First-run config (run  lisa  on VPS):\n"))
    if servers:
        for sid, svr in list(servers.items())[:1]:
            print(f"  Server IP: {svr['host']}")
            for ib in svr.get("inbounds", []):
                if ib.get("protocol") == "vless-reality":
                    print(f"  Port: {ib.get('port', '443')}")
                    print(f"  pubkey: {ib.get('public_key', 'your-pbk')}")
                    print(f"  shortId: {ib.get('short_id', 'your-sid')}")
                    print(f"  SNI: {ib.get('server_name', 'www.java.com')}")
                    print(f"  flow: {ib.get('flow', 'xtls-rprx-vision')}")
    else:
        print(c("R", "  (Add a server first for auto-fill)"))
    
    print(c("Y", "\n[Step 4] Manage users on VPS:\n"))
    print("  lisa    (or: python3 /root/lisa.py)")
    print("  1. View users + traffic")
    print("  2. Add user  -> auto-generates VLESS link")
    print("  3. Delete user")
    print("  4. Export all links")
    print("  5. Check limits + auto-stop over-limit/expired")
    print("  6. Exit")
    
    print(c("Y", "\n[Step 5] Back on desktop, generate card:\n"))
    print("  Menu 3 -> paste customer UUID -> pick package -> card ready!")
    
    print(c("C", "\n" + "=" * 50))
    input(c("Y", "\n[Enter] return to menu"))

def main():
    cfg = load_config()
    if not cfg.get("brand", {}).get("name"):
        setup_wizard()
    banner()
    while True:
        xs = c("G", "[OK]") if is_installed() else c("R", "[X]")
        print(f"  1. Add Server              Xray: {xs}")
        print("  2. Add Inbound (Protocol)")
        print("  3. Generate Card + QR")
        print("  4. List Servers")
        print("  5. Download Xray Core")
        print("  6. Global Config (brand/contact)")
        print("  7. Manage Packages (add/edit/delete)")
        print("  8. VPS One-Click Deploy")
        print("  9. Exit")
        print()
        ch = input("  > ").strip()
        if ch == "1": add_server_menu()
        elif ch == "2": add_inbound_menu()
        elif ch == "3": gen_card_menu()
        elif ch == "4": list_servers_menu()
        elif ch == "5":
            from proxyforge.xray import download_xray
            print(c("Y", "\n[*] Downloading...\n"))
            try:
                download_xray()
                print(c("G", "\n  [OK]\n"))
            except Exception as e:
                print(c("R", f"\n  [X] {e}\n"))
        elif ch == "6":
            cfg = load_config()
            print(c("Y", "\n[*] Global Config\n"))
            cfg["brand"]["name"] = input(f"  Brand [{cfg['brand']['name']}]: ").strip() or cfg["brand"]["name"]
            cfg["brand"]["contact"] = input(f"  Contact [{cfg['brand']['contact']}]: ").strip() or cfg["brand"]["contact"]
            save_config(cfg)
            print(c("G", "  [OK]\n"))
        elif ch == "7":
            package_menu()
        elif ch == "8":
            vps_deploy_menu()
        elif ch == "9":
            print(c("C", "\n  Bye!\n"))
            break

if __name__ == "__main__":
    main()
