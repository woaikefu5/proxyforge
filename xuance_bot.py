#!/usr/bin/env python3
"""?? Telegram Bot ? ???????? v1.0"""

import json, time, urllib.request, urllib.parse, urllib.error
import sys, os, threading, re
from datetime import datetime, timedelta

sys.path.insert(0, '/root')
import xuance

BOT_TOKEN_FILE = "/root/xuance_bot_token.json"
ADMIN_FILE = "/root/xuance_admin.json"

def load_bot_config():
    if os.path.exists(BOT_TOKEN_FILE):
        return json.load(open(BOT_TOKEN_FILE))
    return None

def save_admin(chat_id):
    json.dump({"admin_chat_id": chat_id}, open(ADMIN_FILE, "w"))

def get_admin():
    if os.path.exists(ADMIN_FILE):
        return json.load(open(ADMIN_FILE)).get("admin_chat_id")
    return None

def api(method, params=None):
    cfg = load_bot_config()
    if not cfg: return None
    token = cfg["token"]
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        if params:
            data = urllib.parse.urlencode(params).encode()
            req = urllib.request.Request(url, data=data)
        else:
            req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode())
    except Exception as e:
        print(f"API Error: {e}")
        return None

def send_message(chat_id, text, parse_mode="HTML"):
    MAX_LEN = 4000
    for i in range(0, len(text), MAX_LEN):
        chunk = text[i:i+MAX_LEN]
        api("sendMessage", {"chat_id": chat_id, "text": chunk, "parse_mode": parse_mode})

def format_user(u, idx=None):
    gb = u["used_bytes"] / 1073741824
    lim = u["limit_gb"]
    pct = gb/lim*100 if lim>0 else 0
    prefix = f"<b>{idx}.</b> " if idx else ""
    return f"{prefix}<b>{u['name']}</b>: {gb:.1f}/{lim:.0f}GB ({pct:.1f}%) ? {u.get('expiry_date','?')}"

def handle_update(update):
    msg = update.get("message", {})
    if not msg: return
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "").strip()
    admin_id = get_admin()

    if not chat_id: return

    # First user becomes admin
    if not admin_id:
        save_admin(chat_id)
        admin_id = chat_id
        send_message(chat_id, "<b>\U0001f977 ?? Bot \u5df2\u6fc0\u6d3b!</b>\n\u4f60\u5df2\u6210\u4e3a\u7ba1\u7406\u5458\u3002\n\u53d1\u9001 /help \u67e5\u770b\u547d\u4ee4\u5217\u8868\u3002\n\n\u8bf7\u5148\u7528 /config \u914d\u7f6e\u670d\u52a1\u5668\u4fe1\u606f\u3002")
        return

    is_admin = (chat_id == admin_id)

    # === PUBLIC COMMANDS ===
    if text == "/start":
        send_message(chat_id, "\u56de\u590d <code>/my \u6635\u79f0</code> \u67e5\u770b\u4f60\u7684\u4f7f\u7528\u60c5\u51b5\uff0c\u6216\u8054\u7cfb\u7ba1\u7406\u5458\u83b7\u53d6\u5e2e\u52a9\u3002")

    elif text == "/help":
        if is_admin:
            send_message(chat_id, """<b>\U0001f4cb \u7ba1\u7406\u5458\u547d\u4ee4</b>
<code>/list</code> ? \u67e5\u770b\u6240\u6709\u7528\u6237
<code>/add \u6635\u79f0 \u6d41\u91cfGB \u5929\u6570</code> ? \u6dfb\u52a0\u7528\u6237
<code>/del \u5e8f\u53f7</code> ? \u5220\u9664\u7528\u6237
<code>/recharge \u5e8f\u53f7 \u6d41\u91cfGB \u5929\u6570</code> ? \u5145\u503c\u91cd\u7f6e
<code>/export</code> ? \u5bfc\u51fa\u6240\u6709\u94fe\u63a5
<code>/check</code> ? \u68c0\u67e5\u8fc7\u671f/\u8d85\u989d
<code>/my \u6635\u79f0</code> ? \u67e5\u5355\u4e2a\u7528\u6237
<code>/status</code> ? \u670d\u52a1\u5668\u72b6\u6001""")
        else:
            send_message(chat_id, """<b>\U0001f4cb \u7528\u6237\u547d\u4ee4</b>
<code>/my \u6635\u79f0</code> ? \u67e5\u770b\u4f60\u7684\u4f7f\u7528\u60c5\u51b5
<code>/link \u6635\u79f0</code> ? \u83b7\u53d6\u4f60\u7684\u8ba2\u9605\u94fe\u63a5
<code>/help</code> ? \u663e\u793a\u6b64\u5e2e\u52a9""")

    elif text.startswith("/my"):
        data = xuance.load_db()
        data = xuance.update_traffic(data)
        xuance.save_db(data)
        users = [u for u in data["users"] if u.get("active", True)]
        name = text.replace("/my", "").strip()
        if not name:
            if is_admin:
                if not users:
                    send_message(chat_id, "\u6682\u65e0\u7528\u6237")
                    return
                lines = ["<b>\U0001f4ca \u6240\u6709\u7528\u6237</b>", ""]
                for i, u in enumerate(users, 1):
                    lines.append(format_user(u, i))
                send_message(chat_id, "\n".join(lines))
            else:
                send_message(chat_id, "\u7528\u6cd5: <code>/my \u6635\u79f0</code>")
            return
        matches = [u for u in users if u["name"] == name]
        if matches:
            send_message(chat_id, format_user(matches[0]))
        else:
            send_message(chat_id, f"\u274c \u672a\u627e\u5230\u7528\u6237: {name}")

    elif text.startswith("/link"):
        name = text.replace("/link", "").strip()
        if not name:
            send_message(chat_id, "\u7528\u6cd5: <code>/link \u6635\u79f0</code>")
            return
        xuance.load_server_config()
        data = xuance.load_db()
        users = [u for u in data["users"] if u.get("active", True)]
        matches = [u for u in users if u["name"] == name]
        if matches:
            link = xuance.make_link(matches[0]["uuid"], matches[0]["name"])
            send_message(chat_id, f"<b>\U0001f517 {name}</b>\n<code>{link}</code>")
        else:
            send_message(chat_id, f"\u274c \u672a\u627e\u5230\u7528\u6237: {name}")

    # === ADMIN COMMANDS ===
    elif not is_admin:
        send_message(chat_id, "\u274c \u4f60\u6ca1\u6709\u7ba1\u7406\u6743\u9650\uff0c\u8bf7\u8054\u7cfb\u7ba1\u7406\u5458\u3002")
        return

    elif text == "/list":
        data = xuance.load_db()
        data = xuance.update_traffic(data)
        xuance.save_db(data)
        users = [u for u in data["users"] if u.get("active", True)]
        if not users:
            send_message(chat_id, "\u6682\u65e0\u7528\u6237")
            return
        lines = ["<b>\U0001f4ca \u7528\u6237\u5217\u8868</b>", ""]
        for i, u in enumerate(users, 1):
            lines.append(format_user(u, i))
        send_message(chat_id, "\n".join(lines))

    elif text.startswith("/add"):
        parts = text.split()
        if len(parts) < 3:
            send_message(chat_id, "\u7528\u6cd5: <code>/add \u6635\u79f0 \u6d41\u91cfGB \u5929\u6570</code>\n\u4f8b: /add test-user 100 30")
            return
        name = parts[1]
        try:
            limit = float(parts[2])
            days = int(parts[3]) if len(parts) > 3 else 30
        except:
            send_message(chat_id, "\u274c \u6d41\u91cf\u548c\u5929\u6570\u5fc5\u987b\u662f\u6570\u5b57")
            return
        xuance.load_server_config()
        data = xuance.load_db()
        uuid_val = xuance.run("cat /proc/sys/kernel/random/uuid")
        try:
            xc = json.load(open(xuance.CONF))
            xc["inbounds"][1]["settings"]["clients"].append({"id": uuid_val, "email": name, "flow": "xtls-rprx-vision"})
            json.dump(xc, open(xuance.CONF, "w"), indent=2)
        except Exception as e:
            send_message(chat_id, f"\u274c \u914d\u7f6e\u5931\u8d25: {e}")
            return
        data["users"].append({
            "uuid": uuid_val, "name": name, "limit_gb": limit, "used_bytes": 0,
            "reg_date": datetime.now().strftime("%Y-%m-%d"),
            "expiry_date": (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d"),
            "active": True
        })
        xuance.save_db(data)
        xuance.run("systemctl restart xray 2>/dev/null")
        link = xuance.make_link(uuid_val, name)
        send_message(chat_id, f"\u2705 <b>{name}</b> \u5df2\u6dfb\u52a0\n{limit}GB / {days}\u5929\n<code>{link}</code>")

    elif text.startswith("/del"):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "\u7528\u6cd5: <code>/del \u5e8f\u53f7</code>\n\u5148\u7528 /list \u67e5\u770b\u5e8f\u53f7")
            return
        try:
            data = xuance.load_db()
            users = [u for u in data["users"] if u.get("active", True)]
            i = int(parts[1]) - 1
            if i < 0 or i >= len(users):
                send_message(chat_id, "\u274c \u65e0\u6548\u5e8f\u53f7")
                return
            target = users[i]
            xc = json.load(open(xuance.CONF))
            xc["inbounds"][1]["settings"]["clients"] = [c for c in xc["inbounds"][1]["settings"]["clients"] if c["id"] != target["uuid"]]
            json.dump(xc, open(xuance.CONF, "w"), indent=2)
            data["users"] = [u for u in data["users"] if u["uuid"] != target["uuid"]]
            xuance.save_db(data)
            xuance.run("systemctl restart xray 2>/dev/null")
            send_message(chat_id, f"\u2705 {target['name']} \u5df2\u5220\u9664")
        except Exception as e:
            send_message(chat_id, f"\u274c \u5220\u9664\u5931\u8d25: {e}")

    elif text.startswith("/recharge"):
        parts = text.split()
        if len(parts) < 4:
            send_message(chat_id, "\u7528\u6cd5: <code>/recharge \u5e8f\u53f7 \u6d41\u91cfGB \u5929\u6570</code>\n\u4f8b: /recharge 1 200 30")
            return
        try:
            idx = int(parts[1]) - 1
            add_gb = float(parts[2])
            add_days = int(parts[3])
        except:
            send_message(chat_id, "\u274c \u53c2\u6570\u683c\u5f0f\u9519\u8bef")
            return
        data = xuance.load_db()
        users = [u for u in data["users"] if u.get("active", True)]
        if idx < 0 or idx >= len(users):
            send_message(chat_id, "\u274c \u65e0\u6548\u5e8f\u53f7")
            return
        actual = next((u for u in data["users"] if u["uuid"] == users[idx]["uuid"]), None)
        if not actual:
            send_message(chat_id, "\u274c \u7528\u6237\u4e0d\u5b58\u5728")
            return
        actual["used_bytes"] = 0  # reset on recharge
        actual["limit_gb"] = add_gb
        actual["expiry_date"] = (datetime.now() + timedelta(days=add_days)).strftime("%Y-%m-%d")
        xuance.save_db(data)
        send_message(chat_id, f"\u2705 <b>{actual['name']}</b> \u5145\u503c\u5b8c\u6210\n\u65b0\u9650\u989d: {add_gb}GB\n\u5230\u671f: {actual['expiry_date']}")

    elif text == "/export":
        xuance.load_server_config()
        data = xuance.load_db()
        links = []
        for u in data["users"]:
            if u.get("active", True):
                links.append(f"<b>{u['name']}</b>\n<code>{xuance.make_link(u['uuid'], u['name'])}</code>")
        if links:
            for link in links:
                send_message(chat_id, link)
        else:
            send_message(chat_id, "\u6682\u65e0\u6d3b\u8dc3\u7528\u6237")

    elif text == "/check":
        data = xuance.load_db()
        data = xuance.update_traffic(data)
        xc = json.load(open(xuance.CONF))
        clients = xc["inbounds"][1]["settings"]["clients"]
        changed = False
        msgs = []
        for user in data["users"][:]:
            if not user.get("active", True): continue
            reason = None
            if user["used_bytes"] / 1073741824 >= user["limit_gb"]: reason = "\u8d85\u989d"
            try:
                if datetime.strptime(user["expiry_date"], "%Y-%m-%d") < datetime.now():
                    reason = "\u5230\u671f"
            except: pass
            if reason:
                clients = [c for c in clients if c["id"] != user["uuid"]]
                user["active"] = False
                msgs.append(f"[{reason}] {user['name']}")
                changed = True
        if changed:
            xc["inbounds"][1]["settings"]["clients"] = clients
            json.dump(xc, open(xuance.CONF, "w"), indent=2)
            xuance.save_db(data)
            xuance.run("systemctl restart xray 2>/dev/null")
            send_message(chat_id, "<b>\U0001f50d \u68c0\u67e5\u5b8c\u6210</b>\n" + "\n".join(msgs))
        else:
            send_message(chat_id, "\u2705 \u5168\u90e8\u6b63\u5e38")

    elif text == "/status":
        uptime = xuance.run("uptime")
        mem = xuance.run("free -h | grep Mem")
        disk = xuance.run("df -h / | tail -1")
        send_message(chat_id, f"<b>\U0001f4bb \u670d\u52a1\u5668\u72b6\u6001</b>\n{uptime}\n{mem}\n\u78c1\u76d8: {disk}")

    else:
        send_message(chat_id, "\u672a\u77e5\u547d\u4ee4\uff0c\u53d1\u9001 /help \u67e5\u770b\u53ef\u7528\u547d\u4ee4\u3002")

def main():
    print("=== \u7384\u7b56 Telegram Bot ===")
    cfg = load_bot_config()
    if not cfg:
        token = input("\u8bf7\u8f93\u5165 Telegram Bot Token (\u4ece @BotFather \u83b7\u53d6): ").strip()
        if not token:
            print("\u9700\u8981 Token \u624d\u80fd\u542f\u52a8 Bot")
            sys.exit(1)
        json.dump({"token": token}, open(BOT_TOKEN_FILE, "w"))
        cfg = {"token": token}
        print("Token \u5df2\u4fdd\u5b58")

    print("\u2714 Bot Token \u5df2\u914d\u7f6e")
    admin = get_admin()
    if admin:
        print(f"\u2714 \u7ba1\u7406\u5458 Chat ID: {admin}")
    else:
        print("\u26a0 \u7b49\u5f85\u7ba1\u7406\u5458\u53d1\u9001 /start ...")

    last_update = 0
    print("\U0001f7e2 Bot \u8fd0\u884c\u4e2d...")

    while True:
        try:
            result = api("getUpdates", {"offset": last_update + 1, "timeout": 30})
            if result and result.get("ok") and result.get("result"):
                for update in result["result"]:
                    last_update = update["update_id"]
                    threading.Thread(target=handle_update, args=(update,)).start()
        except KeyboardInterrupt:
            print("\nBot \u5df2\u505c\u6b62")
            break
        except Exception as e:
            print(f"Poll error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

