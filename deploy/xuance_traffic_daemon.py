#!/usr/bin/env python3
"""XuanCe Traffic Daemon v10 - Delta tracking only, no overwrite"""
import json, subprocess

DB = "/root/xuance_users.json"
STATE = "/tmp/xuance_traffic_state.json"
XRAY_BIN = "/etc/v2ray-agent/xray/xray"
API_ADDR = "127.0.0.1:8080"

def shell(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def load_json(path, default=None):
    try: return json.load(open(path))
    except: return default or {}

def save_json(data, path):
    json.dump(data, open(path, "w"), indent=2)

def main():
    db = load_json(DB, {"version": 4, "users": []})
    state = load_json(STATE, {})

    # Get current Xray stats
    try:
        raw = shell(f"{XRAY_BIN} api statsquery --server={API_ADDR}")
        if not raw: return
        api = json.loads(raw)
    except: return

    # Parse per-user stats
    cur = {}
    for item in api.get("stat", []):
        n = item.get("name", "")
        if not n.startswith("user>>>"): continue
        parts = n.split(">>>")
        if len(parts) < 4: continue
        email = parts[1]
        cur.setdefault(email, {"up": 0, "down": 0})
        cur[email]["up" if parts[3] == "uplink" else "down"] = item.get("value", 0) or 0

    # Build email -> uuid
    email_uid = {}
    for u in db.get("users", []):
        email_uid[u.get("name", "")] = u["uuid"]

    updated = 0
    for email, cv in cur.items():
        uid = email_uid.get(email)
        if not uid: continue
        total = cv["up"] + cv["down"]
        prev_total = state.get(uid, {}).get("total", 0)

        # Xray restart detected: counter reset, skip to preserve data
        if total < prev_total:
            delta = 0
        else:
            delta = total - prev_total

        if delta > 0:
            for u in db["users"]:
                if u["uuid"] == uid:
                    u["used_bytes"] = u.get("used_bytes", 0) + delta
                    updated += 1
                    break

        state[uid] = {"total": total}

    save_json(db, DB)
    save_json(state, STATE)
    if updated > 0:
        print(f"  +{updated} users traffic updated")

if __name__ == "__main__":
    main()
