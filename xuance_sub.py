#!/usr/bin/env python3
"""XuanCe Subscription Server - Clash / Sing-box v1.0"""

import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, '/root')
import xuance

PORT = 28080

def get_user(name):
    data = xuance.load_db()
    for u in data["users"]:
        if u["name"] == name and u.get("active", True):
            return u
    return None

def gen_clash(user, host, port, flow, pbk, sni, sid):
    name = user["name"]
    uuid = user["uuid"]
    lines = []
    lines.append("proxies:")
    lines.append('  - name: "' + name + '"')
    lines.append("    type: vless")
    lines.append("    server: " + host)
    lines.append("    port: " + port)
    lines.append("    uuid: " + uuid)
    lines.append("    network: tcp")
    lines.append("    tls: true")
    lines.append("    udp: true")
    lines.append("    flow: " + flow)
    lines.append("    client-fingerprint: chrome")
    lines.append("    servername: " + sni)
    lines.append("    reality-opts:")
    lines.append("      public-key: " + pbk)
    lines.append("      short-id: " + sid)
    lines.append("")
    lines.append("proxy-groups:")
    lines.append('  - name: "XuanCe-' + name + '"')
    lines.append("    type: select")
    lines.append("    proxies:")
    lines.append('      - "' + name + '"')
    lines.append("")
    lines.append("rules:")
    lines.append("  - MATCH,XuanCe-" + name)
    return "\n".join(lines)

def gen_singbox(user, host, port, flow, pbk, sni, sid):
    return json.dumps({
        "outbounds": [{
            "type": "vless",
            "tag": user["name"],
            "server": host,
            "server_port": int(port),
            "uuid": user["uuid"],
            "flow": flow,
            "tls": {
                "enabled": True,
                "server_name": sni,
                "utls": {"enabled": True, "fingerprint": "chrome"},
                "reality": {"enabled": True, "public_key": pbk, "short_id": sid}
            },
            "transport": {"type": "tcp"}
        }]
    }, indent=2, ensure_ascii=False)

def gen_all_clash(host, port, flow, pbk, sni, sid):
    data = xuance.load_db()
    users = [u for u in data["users"] if u.get("active", True)]
    if not users:
        return "# No active users"
    lines = ["proxies:"]
    names = []
    for u in users:
        name = u["name"]
        names.append(name)
        lines.append('  - name: "' + name + '"')
        lines.append("    type: vless")
        lines.append("    server: " + host)
        lines.append("    port: " + port)
        lines.append("    uuid: " + u["uuid"])
        lines.append("    network: tcp")
        lines.append("    tls: true")
        lines.append("    udp: true")
        lines.append("    flow: " + flow)
        lines.append("    client-fingerprint: chrome")
        lines.append("    servername: " + sni)
        lines.append("    reality-opts:")
        lines.append("      public-key: " + pbk)
        lines.append("      short-id: " + sid)
    lines.append("")
    lines.append("proxy-groups:")
    lines.append('  - name: "XuanCe-All"')
    lines.append("    type: select")
    lines.append("    proxies:")
    for n in names:
        lines.append('      - "' + n + '"')
    lines.append("")
    lines.append("rules:")
    lines.append("  - MATCH,XuanCe-All")
    return "\n".join(lines)

def gen_all_singbox(host, port, flow, pbk, sni, sid):
    data = xuance.load_db()
    users = [u for u in data["users"] if u.get("active", True)]
    outbounds = []
    for u in users:
        outbounds.append({
            "type": "vless",
            "tag": u["name"],
            "server": host,
            "server_port": int(port),
            "uuid": u["uuid"],
            "flow": flow,
            "tls": {
                "enabled": True,
                "server_name": sni,
                "utls": {"enabled": True, "fingerprint": "chrome"},
                "reality": {"enabled": True, "public_key": pbk, "short_id": sid}
            },
            "transport": {"type": "tcp"}
        })
    return json.dumps({"outbounds": outbounds}, indent=2, ensure_ascii=False)

class SubHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.strip("/")
        params = parse_qs(parsed.query)
        fmt = params.get("format", ["clash"])[0]

        if fmt not in ("clash", "singbox"):
            self.send_error(400, "Invalid format")
            return

        xuance.load_server_config()
        host = xuance.HOST
        port = xuance.PORT
        flow = xuance.FLOW
        pbk = xuance.PBK
        sni = xuance.SNI
        sid = xuance.SID

        parts = path.split("/")
        cmd = parts[0] if parts else ""
        username = parts[1] if len(parts) > 1 else ""

        if cmd == "sub" and username:
            user = get_user(username)
            if not user:
                self.send_error(404, "User not found")
                return
            if fmt == "clash":
                content = gen_clash(user, host, port, flow, pbk, sni, sid)
                ct = "text/yaml; charset=utf-8"
            else:
                content = gen_singbox(user, host, port, flow, pbk, sni, sid)
                ct = "application/json; charset=utf-8"

        elif cmd == "all":
            if fmt == "clash":
                content = gen_all_clash(host, port, flow, pbk, sni, sid)
                ct = "text/yaml; charset=utf-8"
            else:
                content = gen_all_singbox(host, port, flow, pbk, sni, sid)
                ct = "application/json; charset=utf-8"

        else:
            content = "<html><body><h1>XuanCe Sub</h1><p>/sub/user?format=clash</p><p>/all?format=clash</p></body></html>"
            ct = "text/html; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Subscription-Userinfo", "upload=0; download=0; total=0")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

if __name__ == "__main__":
    print("XuanCe Sub Server :" + str(PORT))
    server = HTTPServer(("0.0.0.0", PORT), SubHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
