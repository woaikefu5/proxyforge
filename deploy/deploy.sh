#!/bin/bash
set -e
echo "=== XuanCe Deploy ==="
cp xuance_traffic_daemon.py /root/
cp xuance_web.py /root/
cp xuance_config.json /root/
chmod +x /root/xuance_web.py /root/xuance_traffic_daemon.py

# Auto-fill xuance_config.json from Xray config
SERVER_IP=
DOKO_PORT=
PBK=
SNI=
SID=
python3 -c "import json;c=json.load(open(/root/xuance_config.json));c[host]=;c[port]=str();c[pbk]=;c[sni]=;c[sid]=;json.dump(c,open(/root/xuance_config.json,w),indent=2)"

# Init DB
if [ ! -f /root/xuance_users.json ]; then
    echo version:2 > /root/xuance_users.json
fi

# Install service
cp xuance-web.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable xuance-web
systemctl restart xuance-web

# Cron
(crontab -l 2>/dev/null | grep -v xuance_traffic_daemon; echo "*/5 * * * * python3 /root/xuance_traffic_daemon.py") | crontab -

echo "=== Done: http:// ==="
 #!/bin/bash
set -e
echo "=== XuanCe Deploy ==="
cp xuance_traffic_daemon.py /root/
cp xuance_web.py /root/
cp xuance_config.json /root/
chmod +x /root/xuance_web.py /root/xuance_traffic_daemon.py

# Auto-fill xuance_config.json from Xray config
SERVER_IP=
DOKO_PORT=
PBK=
SNI=
SID=
python3 -c "import json;c=json.load(open(/root/xuance_config.json));c[host]=;c[port]=str();c[pbk]=;c[sni]=;c[sid]=;json.dump(c,open(/root/xuance_config.json,w),indent=2)"

# Init DB
if [ ! -f /root/xuance_users.json ]; then
    echo users:[] > /root/xuance_users.json
fi

# Install service
cp xuance-web.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable xuance-web
systemctl restart xuance-web

# Cron
(crontab -l 2>/dev/null | grep -v xuance_traffic_daemon; echo "*/5 * * * * python3 /root/xuance_traffic_daemon.py") | crontab -

echo "=== Done: http:// ==="


# Fix Xray policy system stats
cp fix_policy.py /root/
python3 /root/fix_policy.py
echo 'Policy stats fixed'
