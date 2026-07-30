#!/bin/bash
# XuanCe 完美版一键部署
# 前提：已安装 Xray (mack-a脚本) + Python3

echo "=== XuanCe 完美版部署 ==="

# 1. 部署 xuance daemon (流量统计)
cp xuance_traffic_daemon.py /root/xuance_traffic_daemon.py
chmod +x /root/xuance_traffic_daemon.py

# 2. 部署 web 面板
cp xuance_web.py /usr/local/bin/xuance_web
chmod +x /usr/local/bin/xuance_web

# 3. Xray API路由修复 (防gRPC被劫持)
python3 -c "
import json
cfg = json.load(open('/etc/v2ray-agent/xray/config.json'))
rules = cfg['routing']['rules']
has_api = any('api' in str(r.get('inboundTag','')) for r in rules)
if not has_api:
    rules.insert(0, {'type':'field','inboundTag':['api'],'outboundTag':'api'})
    json.dump(cfg, open('/etc/v2ray-agent/xray/config.json','w'), indent=2)
    print('API路由规则已添加')
else:
    print('API路由规则已存在')
"

# 4. 设置 cron
(crontab -l 2>/dev/null | grep -v xuance; echo '* * * * * python3 /root/xuance_traffic_daemon.py') | crontab -

# 5. 重启服务
pkill -f xuance_web 2>/dev/null
sleep 1
nohup python3 /usr/local/bin/xuance_web > /dev/null 2>&1 &
systemctl restart xray

echo "=== 部署完成 ==="
echo "管理面板: http://服务器IP:8318/admin"
echo "用户面板: http://服务器IP:8318/user"
echo "后台密码: admin123456"
