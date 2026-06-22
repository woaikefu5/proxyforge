#!/usr/bin/env python3
"""ProxyForge - Xray + """

import os
import sys
import json

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from proxyforge.config import load_config, save_config
from proxyforge.protocols import gen_uuid, make_link, SUPPORTED_PROTOCOLS
from proxyforge.cardgen import generate_customer_card
from proxyforge.xray import ensure_xray, is_installed


C = {
    "G": "\033[0;32m",
    "C": "\033[0;36m",
    "R": "\033[0;31m",
    "Y": "\033[0;33m",
    "W": "\033[0m",
}


def c(tag, text):
    return f"{C.get(tag, '')}{text}{C['W']}"


def banner():
    print()
    print(c("C", "=" * 42))
    print(c("C", "   ProxyForge v1.0.0"))
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

    cfg.setdefault("servers", {})[sid] = {
        "host": host,
        "inbounds": [],
    }
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

    pdef = SUPPORTED_PROTOCOLS[proto]
    print(c("C", f"\n  Protocol: {pdef['name']}\n"))

    port = input("  Port: ").strip()
    remark = input("  Remark (english): ").strip() or "default"
    user_uuid = gen_uuid()
    print(f"  UUID (auto): {user_uuid}")

    inbound = {
        "tag": f"{proto}-{remark}",
        "protocol": proto,
        "port": int(port) if port else 443,
        "uuid": user_uuid,
        "remark": remark,
    }

    if proto == "vless-reality":
        inbound["public_key"] = input("  Reality pubkey (pbk): ").strip()
        inbound["server_name"] = input("  Fallback SNI (default www.java.com): ").strip() or "www.java.com"
        inbound["short_id"] = input("  shortId: ").strip()
        inbound["flow"] = input("  flow (default xtls-rprx-vision): ").strip() or "xtls-rprx-vision"
    elif proto in ("vless-ws-tls", "vmess"):
        inbound["server_name"] = input("  SNI: ").strip()
        inbound["path"] = input("  WS path (default /): ").strip() or "/"
    elif proto == "vless-grpc":
        inbound["server_name"] = input("  SNI: ").strip()
        inbound["service_name"] = input("  gRPC service name: ").strip()
    elif proto == "trojan":
        inbound["password"] = input("  Password: ").strip() or gen_uuid()[:16]
        inbound["server_name"] = input("  SNI: ").strip()
    elif proto == "ss":
        inbound["method"] = input("  Cipher (default aes-256-gcm): ").strip() or "aes-256-gcm"
        inbound["password"] = input("  Password: ").strip() or gen_uuid()[:16]

    host = servers[sid]["host"]
    link = make_link(proto, **{**inbound, "host": host})
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
            pkg = {"traffic": traffic, "price": int(price), "duration": "month"}
        else:
            pkg = packages[pi]
    except:
        print(c("R", "  [X] Cancel"))
        return

    user_uuid = gen_uuid()
    host = server["host"]
    proto = ib["protocol"]

    link_args = {"host": host, "remark": name}
    for k in ("port", "public_key", "server_name", "short_id", "flow",
              "path", "service_name", "network", "password", "method"):
        if k in ib:
            link_args[k] = ib[k]
    link_args["user_uuid"] = user_uuid

    link = make_link(proto, **link_args)

    desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
    card_path, qr_path = generate_customer_card(
        name=name,
        uuid=user_uuid,
        link=link,
        package_info=pkg,
        brand_name=cfg["brand"]["name"],
        contact=cfg["brand"]["contact"],
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


def main():
    cfg = load_config()

    if not cfg.get("brand", {}).get("name"):
        setup_wizard()

    banner()

    while True:
        xray_status = c("G", "[OK] Installed") if is_installed() else c("R", "[X] Not installed")

        print(f"  1. Add Server              Xray: {xray_status}")
        print("  2. Add Inbound (Protocol)")
        print("  3. Generate Card + QR")
        print("  4. List Servers")
        print("  5. Download/Update Xray Core")
        print("  6. Global Config")
        print("  7. Exit")
        print()

        ch = input("  Choice (1-7): ").strip()

        if ch == "1":
            add_server_menu()
        elif ch == "2":
            add_inbound_menu()
        elif ch == "3":
            gen_card_menu()
        elif ch == "4":
            list_servers_menu()
        elif ch == "5":
            from proxyforge.xray import download_xray
            print(c("Y", "\n[*] Downloading Xray core...\n"))
            try:
                download_xray()
                print(c("G", "\n  [OK] Done\n"))
            except Exception as e:
                print(c("R", f"\n  [X] {e}\n"))
        elif ch == "6":
            cfg = load_config()
            print(c("Y", "\n[*] Global Config\n"))
            cfg["brand"]["name"] = input(f"  Brand [{cfg['brand']['name']}]: ").strip() or cfg["brand"]["name"]
            cfg["brand"]["contact"] = input(f"  Contact [{cfg['brand']['contact']}]: ").strip() or cfg["brand"]["contact"]
            save_config(cfg)
            print(c("G", "  [OK] Saved\n"))
        elif ch == "7":
            print(c("C", "\n  Bye!\n"))
            break
        else:
            print(c("R", "  Invalid"))


if __name__ == "__main__":
    main()
