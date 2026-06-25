# 🥷 玄策 XuanCe v4.1

**1核1G VPS 就能跑的 VLESS Reality 代理管理系统**

[![Version](https://img.shields.io/badge/version-4.1-blue)](https://github.com/woaikefu5/proxyforge)
[![Python](https://img.shields.io/badge/python-3.8+-green)](https://www.python.org/)
[![Xray](https://img.shields.io/badge/xray-25.4.x-orange)](https://github.com/XTLS/Xray-core)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen)](https://hub.docker.com/)

---

## 功能一览

| 功能 | 说明 |
|------|------|
| 🖥️ **Web 管理面板** | 暗色主题，Dashboard + 用户管理，充值/删用户/一键检查 |
| 📊 **gRPC 精确流量** | 字节级统计，比日志估算精准；gRPC 挂了自动回退 |
| 🔗 **订阅直达** | Clash / Sing-box 订阅链接，用户一键导入 |
| 📱 **QR 二维码** | 用户面板一键生成 vless:// 二维码 |
| 🤖 **Telegram Bot** | `@YourBotNameBot` 用户自助查流量/充值/加用户 |
| 🔄 **充值重置** | 充值自动重置已用流量 + 续费天数，不充不重置 |
| 🐳 **Docker 一键部署** | `docker-compose up -d` 就跑 |
| ⚡ **裸机一键脚本** | VPS 上一条命令全搞定 |

---

## 快速部署

### Docker（推荐）
```bash
git clone https://github.com/woaikefu5/proxyforge.git
cd proxyforge/docker
# 编辑 docker-compose.yml 填入你的 IP 和密钥
docker-compose up -d
```

### 裸机一键脚本
```bash
bash <(curl -sL https://raw.githubusercontent.com/woaikefu5/proxyforge/main/docker/one-click.sh)
```

### 手动部署
```bash
# 1. 安装 Xray
curl -sL "https://github.com/XTLS/Xray-core/releases/download/v25.4.5/Xray-linux-64.zip" -o /tmp/xray.zip
unzip /tmp/xray.zip -d /usr/local/xray/ && chmod +x /usr/local/xray/xray

# 2. 生成密钥
/usr/local/xray/xray x25519
# 记下 Public key 和 Private key

# 3. 拷贝配置文件
cp xray-conf/* /etc/v2ray-agent/xray/conf/
# 编辑 07_VLESS_vision_reality_inbounds.json 替换 YOUR_SERVER_IP, YOUR_PUBLIC_KEY 等

# 4. 启动
cp systemd/* /etc/systemd/system/
systemctl enable --now xray xuance-web xuance-sub xuance-bot
```

---

## 端口说明

| 端口 | 服务 | 协议 |
|------|------|------|
| 443 | VLESS Reality 代理 | TCP + TLS |
| 28080 | 订阅服务器 (Clash/Sing-box) | HTTP |
| 28081 | Web 管理面板 | HTTP |
| 62789 | Xray gRPC API (仅本地) | gRPC |

---

## 项目结构

```
proxyforge/
├── xuance.py              # CLI 管理工具 (玄策核心)
├── xuance_web.py          # Web 管理面板 (端口 28081)
├── xuance_sub.py          # 订阅服务器 (端口 28080)
├── xuance_bot.py          # Telegram Bot
├── xray-conf/             # Xray 配置文件
│   ├── 00_log.json
│   ├── 01_api.json        # gRPC API 配置
│   ├── 07_VLESS_vision_reality_inbounds.json
│   ├── 09_routing.json
│   ├── 11_dns.json
│   ├── 12_policy.json     # 流量统计策略
│   ├── blackhole.json
│   └── direct.json
├── systemd/               # Systemd 服务文件
│   ├── xray.service
│   ├── xuance-web.service
│   ├── xuance-sub.service
│   └── xuance-bot.service
├── docker/                # Docker 部署
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── entrypoint.sh
│   └── one-click.sh
└── README.md
```

---

## 使用说明

### Web 面板
1. 浏览器打开 `http://YOUR_SERVER_IP:28081`
2. 默认密码 `admin`（通过 `/root/xuance_web_pass.json` 修改）
3. Dashboard 看总览 → Users 页面管理用户

### CLI 管理
```bash
python3 /root/xuance.py
# 1.查看  2.添加  3.删除  4.充值  5.导出  6.检查  7.退出
```

### 订阅链接
- Clash: `http://YOUR_SERVER_IP:28080/sub/用户名?format=clash`
- Sing-box: `http://YOUR_SERVER_IP:28080/sub/用户名?format=singbox`
- 全部用户: `http://YOUR_SERVER_IP:28080/all?format=clash`

---

## 更新日志

### v4.1 (2026-06-25)
- 🆕 gRPC API 精确流量统计（字节级，用户级追踪）
- 🆕 Docker 一键部署
- 🐛 修复 `level:0` 污染配置文件
- 🐛 修复 Web 面板新建用户缺失流量追踪
- 🧹 清理残留测试文件和重复代码

### v4.0
- 🆕 Web 管理面板 + REST API
- 🆕 QR 二维码生成
- 🆕 Clash / Sing-box 订阅直达
- 🆕 Telegram Bot 用户管理
- 🆕 充值重置功能

---

## 安全提醒

- 默认密码请第一时间修改
- 建议用 `ufw` 只开放 443/28080/28081 端口
- Bot Token 和密钥请妥善保管
- 生产环境建议套 Nginx 反代 Web 面板加 SSL

---

## License

MIT
