#!/bin/bash
# 馒头的玄策 VPS 一键部署脚本
# 用法: bash <(curl -sL https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/install.sh)

set -e
echo "========================================"
echo "  馒头的玄策 VPS 部署工具"
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

# 用 symlink 做全局命令（比 alias 更可靠）
ln -sf /root/xuance.py /usr/local/bin/xuance 2>/dev/null || true

# 清理旧 lisa 残留
rm -f /root/lisa.py /root/lisa_v3.py /root/lisa_v2.py /root/lisa_users.db 2>/dev/null || true
sed -i '/alias lisa=/d' /root/.bashrc 2>/dev/null || true

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "  直接输入: xuance"
echo "  或:        python3 /root/xuance.py"
echo ""
echo "  首次运行会提示配置服务器参数"