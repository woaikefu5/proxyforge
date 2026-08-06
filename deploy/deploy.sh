#!/bin/bash
set -e
echo "=== XuanCe Deploy v2.1 ==="

XRAY_CONF="/etc/v2ray-agent/xray/config.json"
XUANCE_CONF="/root/xuance_config.json"
XUANCE_DB="/root/xuance_users.json"

# ============================================================
# STEP 1: Auto-detect Reality params from Xray config
# ============================================================
echo "[1/6] Detecting Reality config..."

SERVER_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || curl -s --max-time 5 ip.sb 2>/dev/null || curl -s --max-time 5 icanhazip.com 2>/dev/null)
if [ -z "$SERVER_IP" ]; then
    echo "ERROR: Cannot detect server IP"
    exit 1
fi

# Extract Reality inbound params via Python
read -r DOKO_PORT PBK SNI SID <<< $(python3 -c "
import json
cfg = json.load(open('$XRAY_CONF'))
for ib in cfg['inbounds']:
    if ib.get('protocol') == 'vless' and ib.get('streamSettings',{}).get('security') == 'reality':
        rs = ib['streamSettings']['realitySettings']
        sid = [s for s in rs.get('shortIds',[]) if s]
        sid = sid[0] if sid else ''
        print(ib['port'], rs['publicKey'], rs['serverNames'][0], sid)
        break
")

if [ -z "$DOKO_PORT" ]; then
    echo "ERROR: Cannot find Reality inbound in Xray config"
    exit 1
fi

echo "  IP:   $SERVER_IP"
echo "  Port: $DOKO_PORT"
echo "  SNI:  $SNI"
echo "  SID:  $SID"

# ============================================================
# STEP 2: Fix Reality listen address (127.0.0.1 -> 0.0.0.0)
# ============================================================
echo "[2/6] Fixing Reality listen address..."
python3 -c "
import json
cfg = json.load(open('$XRAY_CONF'))
fixed = False
for ib in cfg['inbounds']:
    if ib.get('protocol') == 'vless' and ib.get('streamSettings',{}).get('security') == 'reality':
        if ib.get('listen', '0.0.0.0') != '0.0.0.0':
            ib['listen'] = '0.0.0.0'
            fixed = True
if fixed:
    json.dump(cfg, open('$XRAY_CONF', 'w'), indent=2)
    print('  Fixed: 127.0.0.1 -> 0.0.0.0')
else:
    print('  Already 0.0.0.0, skip')
"

# ============================================================
# STEP 3: Write xuance_config.json with real values
# ============================================================
echo "[3/6] Writing xuance_config.json..."
python3 -c "
import json
config = {
    'host': '$SERVER_IP',
    'port': '$DOKO_PORT',
    'pbk': '$PBK',
    'sni': '$SNI',
    'sid': '$SID',
    'flow': 'xtls-rprx-vision',
    'policy': {
        'system': {
            'statsOutboundUplink': True,
            'statsOutboundDownlink': True
        }
    }
}
json.dump(config, open('$XUANCE_CONF', 'w'), indent=2)
print('  Done')
"

# ============================================================
# STEP 4: Deploy xuance files
# ============================================================
echo "[4/6] Deploying xuance files..."
cp xuance_web.py /root/
cp xuance_traffic_daemon.py /root/
chmod +x /root/xuance_web.py /root/xuance_traffic_daemon.py

# Init DB if missing
if [ ! -f "$XUANCE_DB" ]; then
    echo '{"version":2,"users":[]}' > "$XUANCE_DB"
    echo "  Created $XUANCE_DB"
fi

# Install systemd service
cp xuance-web.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable xuance-web 2>/dev/null || true

# Kill any running instance and restart
pkill -f xuance_web.py 2>/dev/null || true
sleep 1
systemctl restart xuance-web 2>/dev/null || nohup python3 /root/xuance_web.py > /tmp/xuance_web.log 2>&1 &
sleep 2
echo "  Panel started"

# ============================================================
# STEP 5: Fix Xray policy + restart Xray
# ============================================================
echo "[5/6] Fixing Xray policy system stats..."
python3 -c "
import json
cfg = json.load(open('$XRAY_CONF'))
if 'policy' not in cfg:
    cfg['policy'] = {}
if 'system' not in cfg['policy']:
    cfg['policy']['system'] = {}
cfg['policy']['system']['statsOutboundUplink'] = True
cfg['policy']['system']['statsOutboundDownlink'] = True
json.dump(cfg, open('$XRAY_CONF', 'w'), indent=2)
print('  Policy stats added')
"
systemctl restart xray
sleep 2
echo "  Xray restarted"

# ============================================================
# STEP 6: UFW + Cron
# ============================================================
echo "[6/6] Setting up UFW and cron..."

# Add proxy port to UFW
if command -v ufw &>/dev/null && ufw status | grep -q "active"; then
    ufw allow "$DOKO_PORT/tcp" 2>/dev/null && echo "  UFW: $DOKO_PORT/tcp added" || echo "  UFW: $DOKO_PORT/tcp already exists or failed"
fi

# Cron - every minute for traffic daemon
(crontab -l 2>/dev/null | grep -v xuance_traffic_daemon; echo "* * * * * python3 /root/xuance_traffic_daemon.py") | crontab -
echo "  Cron: traffic daemon every minute"

echo ""
echo "=============================================="
echo "  XuanCe Deploy Complete!"
echo "  Panel:  http://$SERVER_IP:8318/admin"
echo "  User:   http://$SERVER_IP:8318/user"
echo "  Port:   $DOKO_PORT"
echo "=============================================="