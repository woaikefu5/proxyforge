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

# 下载 xuance.py
echo "[*] 下载玄策管理系统..."
curl -sL "https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/xuance.py" -o /root/xuance.py
chmod +x /root/xuance.py

# 设置快捷命令
if ! grep -q "alias xuance=" /root/.bashrc 2>/dev/null; then
    echo "alias xuance='python3 /root/xuance.py'" >> /root/.bashrc
    echo "[OK] 已添加 xuance 快捷命令"
fi

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "  直接输入: python3 /root/xuance.py"
echo "  或简化:   xuance"
echo ""
echo "  首次运行会提示配置服务器信息"
