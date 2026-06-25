#!/bin/bash
# XuanCe Entrypoint - Starts all services

set -e

echo "=== 玄策 XuanCe v4.1 ==="
echo "Starting services..."

# Update config with env vars if provided
if [ -n "$XUANCE_HOST" ]; then
    python3 -c "
import json
c = json.load(open('/root/xuance_config.json'))
if '$XUANCE_HOST': c['host'] = '$XUANCE_HOST'
if '$XUANCE_PORT': c['port'] = '$XUANCE_PORT'
if '$XUANCE_PBK': c['pbk'] = '$XUANCE_PBK'
if '$XUANCE_SNI': c['sni'] = '$XUANCE_SNI'
if '$XUANCE_SID': c['sid'] = '$XUANCE_SID'
json.dump(c, open('/root/xuance_config.json','w'), indent=2)
print('Config updated')
" 2>/dev/null || true
fi

# Update xray inbound with env vars
if [ -n "$XUANCE_HOST" ]; then
    python3 -c "
import json
conf = json.load(open('/etc/v2ray-agent/xray/conf/07_VLESS_vision_reality_inbounds.json'))
# Update reality settings
rs = conf['inbounds'][1]['streamSettings']['realitySettings']
rs['publicKey'] = open('/root/xuance_config.json').read()
rs
print('Xray config synced')
" 2>/dev/null || true
fi

# Start Xray
echo "[1/4] Starting Xray..."
/usr/local/xray/xray run -confdir /etc/v2ray-agent/xray/conf &
XRAY_PID=$!
sleep 2

# Start Subscription Server (port 28080)
echo "[2/4] Starting Subscription Server on :28080..."
cd /root && python3 /root/xuance_sub.py &
SUB_PID=$!

# Start Bot
echo "[3/4] Starting Telegram Bot..."
if [ -f /root/xuance_bot_token.json ]; then
    cd /root && python3 /root/xuance_bot.py &
    BOT_PID=$!
else
    echo "  (Bot skipped - no token)"
    BOT_PID=""
fi

# Start Web Panel (port 28081)
echo "[4/4] Starting Web Panel on :28081..."
cd /root && python3 /root/xuance_web.py &
WEB_PID=$!

echo ""
echo "=== All services started ==="
echo "Web Panel:  http://YOUR_IP:28081"
echo "Sub Server: http://YOUR_IP:28080"
echo "VLESS:      YOUR_IP:443"
echo ""

# Wait for any service to exit, then stop all
trap "kill $XRAY_PID $SUB_PID $BOT_PID $WEB_PID 2>/dev/null; exit 0" SIGTERM SIGINT

# Keep container alive
while true; do
    if ! kill -0 $XRAY_PID 2>/dev/null; then
        echo "ERROR: Xray died! Restarting..."
        /usr/local/xray/xray run -confdir /etc/v2ray-agent/xray/conf &
        XRAY_PID=$!
    fi
    if ! kill -0 $WEB_PID 2>/dev/null; then
        echo "Web panel died, restarting..."
        cd /root && python3 /root/xuance_web.py &
        WEB_PID=$!
    fi
    if ! kill -0 $SUB_PID 2>/dev/null; then
        echo "Sub server died, restarting..."
        cd /root && python3 /root/xuance_sub.py &
        SUB_PID=$!
    fi
    sleep 10
done
