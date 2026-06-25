#!/bin/bash
# 玄策 XuanCe 一键部署脚本
# 支持 Ubuntu 24.04，1核1G内存即可运行

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}"
echo "  ╔══════════════════════════════╗"
echo "  ║   玄策 XuanCe v4.1          ║"
echo "  ║   VLESS Reality 代理管理    ║"
echo "  ╚══════════════════════════════╝"
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then echo -e "${RED}请用 root 运行${NC}"; exit 1; fi

# Config
HOST=${1:-$(curl -s4 ifconfig.me)}
PORT=${2:-443}
SNI=${3:-www.java.com}

echo -e "${GREEN}[1/6] 安装依赖...${NC}"
apt-get update -qq
apt-get install -y -qq curl unzip python3 python3-pip jq 2>/dev/null

echo -e "${GREEN}[2/6] 安装 Xray...${NC}"
XRAY_VER="25.4.5"
curl -sL "https://github.com/XTLS/Xray-core/releases/download/v${XRAY_VER}/Xray-linux-64.zip" -o /tmp/xray.zip
unzip -o /tmp/xray.zip -d /usr/local/xray/ > /dev/null
chmod +x /usr/local/xray/xray
rm /tmp/xray.zip

echo -e "${GREEN}[3/6] 生成密钥...${NC}"
KEYS=$(/usr/local/xray/xray x25519)
PBK=$(echo "$KEYS" | grep "Public" | awk '{print $NF}')
PVK=$(echo "$KEYS" | grep "Private" | awk '{print $NF}')
SID=$(openssl rand -hex 8)

echo -e "${GREEN}[4/6] 下载玄策脚本...${NC}"
# Scripts will be copied from the repo or local
echo "  (从本地或 GitHub 复制脚本)"

echo -e "${GREEN}[5/6] 配置...${NC}"
# Generate config
cat > /root/xuance_config.json << EOF
{
  "host": "$HOST",
  "port": "$PORT",
  "flow": "xtls-rprx-vision",
  "pbk": "$PBK",
  "sni": "$SNI",
  "sid": "$SID",
  "conf": "/etc/v2ray-agent/xray/conf/07_VLESS_vision_reality_inbounds.json"
}
EOF

echo -e "${GREEN}[6/6] 启动服务...${NC}"
systemctl enable --now xray xuance-web xuance-sub xuance-bot 2>/dev/null

echo ""
echo -e "${GREEN}=== 部署完成! ===${NC}"
echo -e "Web面板:  ${CYAN}http://$HOST:28081${NC}"
echo -e "订阅服务: ${CYAN}http://$HOST:28080${NC}"
echo -e "代理端口: ${CYAN}$HOST:$PORT${NC}"
echo -e "公钥 PBK: ${CYAN}$PBK${NC}"
echo -e "短ID SID: ${CYAN}$SID${NC}"
