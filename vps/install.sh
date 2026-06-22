#!/bin/bash
# ProxyForge VPS 一键部署脚本
# 用法: bash <(curl -sL https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/install.sh)

set -e
echo "========================================"
echo "  ProxyForge VPS 部署工具"
echo "========================================"
echo ""

# 检测 Python3
if ! command -v python3 &>/dev/null; then
    echo "[!] 安装 Python3..."
    apt update && apt install -y python3
fi

echo "[OK] Python3 已就绪"

# 下载 lisa.py
echo "[*] 下载丽萨管理系统..."
curl -sL "https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/lisa.py" -o /root/lisa.py
chmod +x /root/lisa.py

# 设置快捷命令
if ! grep -q "alias lisa=" /root/.bashrc 2>/dev/null; then
    echo "alias lisa='python3 /root/lisa.py'" >> /root/.bashrc
    echo "[OK] 已添加 lisa 快捷命令"
fi

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "  直接输入: python3 /root/lisa.py"
echo "  或简化:   lisa"
echo ""
echo "  首次运行会提示配置服务器信息"
