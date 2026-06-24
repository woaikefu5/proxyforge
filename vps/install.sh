#!/bin/bash
# 馒头的玄策 VPS 一键部署脚本 v4.0
# 用法: bash <(curl -sL https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/install.sh)

set -e
echo "========================================"
echo "  玄策 v4.0 — 1核1G 轻松跑"
echo "  VPS 用户管理系统"
echo "========================================"
echo ""

# 检测 Python3
if ! command -v python3 &>/dev/null; then
    echo "[*] 安装 Python3..."
    apt update && apt install -y python3
fi

echo "[OK] Python3 就绪"

# 下载 xuance.py
echo "[*] 下载玄策管理系统..."
curl -sL "https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/xuance.py" -o /root/xuance.py
chmod +x /root/xuance.py

# 创建全局命令
ln -sf /root/xuance.py /usr/local/bin/xuance 2>/dev/null || true

# 清理旧版残留
rm -f /root/lisa.py /root/lisa_v3.py /root/lisa_v2.py /root/lisa_users.db 2>/dev/null || true
sed -i '/alias lisa=/d' /root/.bashrc 2>/dev/null || true

# 设置定时检查（每小时）
crontab -l 2>/dev/null | grep -v xuance > /tmp/cron.tmp 2>/dev/null || true
echo "0 * * * * python3 /root/xuance.py 2>/dev/null" >> /tmp/cron.tmp
crontab /tmp/cron.tmp 2>/dev/null || true
rm -f /tmp/cron.tmp

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "  输入 xuance 进入管理"
echo ""
echo "  功能:"
echo "    1.查看用户 + 流量统计"
echo "    2.添加用户"
echo "    3.删除用户"
echo "    4.充值续费 ← 新增"
echo "    5.导出链接"
echo "    6.检查(超额/到期自动踢)"
echo "    7.退出"
echo ""
echo "  首次运行会提示配置服务器参数"
echo "  需先安装 Xray(mack-a 一键脚本)"
echo ""