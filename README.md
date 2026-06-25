# 🥷 玄策 XuanCe v4.1

**1核1G 内存就能跑的 VLESS Reality 代理管理系统 | 自带 Web 面板 + TG Bot + 订阅服务**

[![Version](https://img.shields.io/badge/version-4.1-blue)](https://github.com/woaikefu5/proxyforge)
[![Python](https://img.shields.io/badge/python-3.8+-green)](https://www.python.org/)
[![Xray](https://img.shields.io/badge/xray-25.4.x-orange)](https://github.com/XTLS/Xray-core)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen)](https://hub.docker.com/)

> 买台 VPS，装个玄策，小白也能开机场。

---

## 为什么选玄策
- 🪶 **极致轻量**：1核1G VPS 流畅运行，不吃资源
- 🎛️ **Web 可视化管理**：暗色面板，添加/删除/充值/查流量点点鼠标就行
- 📊 **gRPC 精确流量**：字节级统计，不是每连接瞎估 5MB
- 🤖 **TG Bot 自助服务**：用户自己查流量、管理员远程操作
- 🔗 **Clash / Sing-box 订阅直达**：用户一键导入，告别手动复制
- 🐳 **Docker 一键部署**：`docker-compose up -d` 就跑，新手友好
- 🔄 **充值即重置**：充了流量自动清零+续期，不充不重置

---

## 功能清单

| 功能 | 说明 |
|------|------|
| 🖥️ **Web 管理面板** | Dashboard 总览 + 用户增删改查 + 一键检查过期/超额 |
| 📊 **gRPC 精确流量** | 字节级统计，gRPC 挂掉自动回退日志估算 |
| 🔗 **订阅一键直达** | Clash YAML / Sing-box JSON 格式订阅链接 |
| 📱 **QR 二维码** | 面板内生成 vless:// 二维码，手机扫即连 |
| 🤖 **Telegram Bot** | 用户 `/my` 查流量，管理员远程管理 |
| 🔄 **充值重置** | 充值自动重置已用流量 + 续费天数 |
| 🐳 **Docker 部署** | 一键启动，自带进程守护和自动重启 |
| ⚡ **裸机脚本** | 不用 Docker 也行，`one-click.sh` 一条命令部署 |

---

## 快速开始

### 方式一：Docker（推荐）
```bash
git clone https://github.com/woaikefu5/proxyforge.git
cd proxyforge
# 编辑 docker-compose.yml 填入服务器 IP 和密钥
docker-compose up -d
```

### 方式二：裸机一键脚本
```bash
bash <(curl -sL https://raw.githubusercontent.com/woaikefu5/proxyforge/main/one-click.sh)
```

---

## 端口说明

| 端口 | 用途 |
|------|------|
| `443` | VLESS Reality 代理 |
| `28080` | 订阅服务器 (Clash/Sing-box) |
| `28081` | Web 管理面板 |
| `62789` | Xray gRPC API (仅本地) |

---

## 项目结构

```
├── xuance.py           CLI 管理工具
├── xuance_web.py       Web 面板 (28081)
├── xuance_sub.py       订阅服务器 (28080)
├── xuance_bot.py       Telegram Bot
├── xray-conf/          Xray 配置
├── systemd/            服务文件
├── Dockerfile          Docker 镜像
├── docker-compose.yml  编排文件
├── entrypoint.sh       容器入口
├── one-click.sh        裸机部署脚本
└── README.md
```

---

## 更新日志

### v4.1
- 🆕 gRPC API 精确流量统计（字节级，用户级追踪）
- 🆕 Docker 一键部署 + 裸机一键脚本
- 🐛 修复 `level:0` 污染配置文件
- 🐛 修复 Web 面板新建用户缺失流量追踪
- 🧹 清理残留代码，规范项目结构

### v4.0
- 🆕 Web 管理面板 + REST API
- 🆕 QR 二维码生成
- 🆕 Clash / Sing-box 订阅直达
- 🆕 Telegram Bot
- 🆕 充值重置功能

---

## License

MIT
