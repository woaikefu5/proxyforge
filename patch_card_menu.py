import re
t = open(r"D:\ProxyForge\proxyforge\main.py", "r", encoding="utf-8").read()
func_start = t.find("def gen_card_menu():")
next_def = t.find("\
def ", func_start + 10)
func_body = t[func_start:next_def] if next_def > 0 else t[func_start:]
rest = t[next_def:] if next_def > 0 else ""
name_marker = '    name = input("\\n  Customer name: ").strip()'
idx = func_body.find(name_marker)
desktop_idx = func_body.find("    desktop = os.path.join", idx)
if idx == -1 or desktop_idx == -1:
    print("NOT FOUND", idx, desktop_idx)
    exit()
new_mid = '    name = input("\\n  Customer name: ").strip()\n    if not name:\n        print(c("R", "  [X] Cancel"))\n        return\n\n    packages = cfg.get("packages", [])\n    pkg = {}\n    if packages:\n        print(c("Y", "\\n[+] \\u9009\\u62e9\\u5957\\u9910:\\n"))\n        for i, p in enumerate(packages):\n            print(f"  {i+1}. {p[\"name\"]:<10} {p[\"traffic\"]}/{p.get(\"duration\",\"month\"):<6} Y{p[\"price\"]}")\n        print(f"  {len(packages)+1}. \\u81ea\\u5b9a\\u4e49\\u8f93\\u5165")\n        try:\n            pi = int(input("\\n  > "))\n            if 1 <= pi <= len(packages):\n                pkg = packages[pi-1]\n            else:\n                pkg["traffic"] = input("  \\u6d41\\u91cf (\\u5982 100GB): ").strip()\n                pkg["price"] = int(input("  \\u4ef7\\u683c: ").strip() or "0")\n                pkg["duration"] = input("  \\u5468\\u671f [month]: ").strip() or "month"\n        except:\n            pkg["traffic"] = input("  \\u6d41\\u91cf: ").strip()\n            pkg["price"] = int(input("  \\u4ef7\\u683c: ").strip() or "0")\n            pkg["duration"] = "month"\n    else:\n        pkg["traffic"] = input("  \\u6d41\\u91cf (\\u5982 100GB): ").strip()\n        pkg["price"] = int(input("  \\u4ef7\\u683c: ").strip() or "0")\n        pkg["duration"] = input("  \\u5468\\u671f [month]: ").strip() or "month"\n\n    if not pkg.get("traffic"):\n        print(c("R", "  [X] Cancel"))\n        return\n\n    proto = ib["protocol"]\n    user_uuid = ib.get("uuid", "")\n    link = make_link(proto, **{**ib, "host": host, "remark": name, "uuid": user_uuid})\n\n'
new_func = func_body[:idx] + new_mid + func_body[desktop_idx:]
t = t[:func_start] + new_func + rest
open(r"D:\ProxyForge\proxyforge\main.py", "w", encoding="utf-8").write(t)
print("OK")
