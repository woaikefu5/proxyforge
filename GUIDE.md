#  ProxyForge 详细使用教程

> 从零开始，手把手教你用 ProxyForge 管理节点、生成客户套餐卡。

---

##  目录

1. [环境准备](#1-环境准备)
2. [安装 ProxyForge](#2-安装-proxyforge)
3. [首次运行 & 品牌配置](#3-首次运行--品牌配置)
4. [添加你的 VPS 服务器](#4-添加你的-vps-服务器)
5. [配置入站协议](#5-配置入站协议)
6. [生成客户套餐卡](#6-生成客户套餐卡)
7. [自定义套餐模板](#7-自定义套餐模板)
8. [Xray-core 下载 & 使用](#8-xray-core-下载--使用)
9. [实战：卖节点的完整工作流](#9-实战卖节点的完整工作流)
10. [常见问题](#10-常见问题)

---

## 1. 环境准备

- **Python 3.9+**：[python.org](https://python.org) 下载安装（勾选 ""Add to PATH""）
- **Git**（可选，克隆用）：[git-scm.com](https://git-scm.com)
- 一台 VPS，已安装 Xray（推荐 [mack-a/v2ray-agent](https://github.com/mack-a/v2ray-agent) 一键脚本）

---

## 2. 安装 ProxyForge

`ash
# 克隆项目
git clone https://github.com/woaikefu5/proxyforge.git
cd proxyforge

# 安装依赖
pip install -r requirements.txt

# 运行
python -m proxyforge.main
`

> 如果不想装 Python，也可以用 pyinstaller 打包成 EXE 双击运行。

---

## 3. 首次运行 & 品牌配置

第一次运行会自动弹出配置：

`
[?] First Run - Quick Setup

  Brand name: 我的节点          # 你的节点品牌名
  Contact: @lisa_net            # Telegram 或微信

  [OK] Config saved
`

之后在套餐卡上会显示品牌名和联系方式。

> 随时可以选菜单 6. Global Config 修改。

---

## 4. 添加你的 VPS 服务器

选菜单 1. Add Server：

`
[+] Add Server

  Server ID: my-vps           # 英文标识，方便区分
  Server IP: 1.2.3.4    # VPS 公网 IP

  [OK] Server my-vps (1.2.3.4) added
`

可以添加多个服务器，比如 my-vps、lisa-hk、lisa-jp。

---

## 5. 配置入站协议

选菜单 2. Add Inbound，然后分三步：

### 5.1 选择服务器

`
[+] Select Server:

  1. my-vps (1.2.3.4)

  Which: 1
`

### 5.2 选择协议

`
[+] Select Protocol:

  1. VLESS+Reality+Vision     #  推荐
  2. VLESS+WebSocket+TLS      # CDN 友好
  3. VLESS+gRPC+TLS           # 高性能
  4. VMess+WebSocket+TLS      # 兼容旧客户端
  5. Trojan+TLS               # 轻量伪装
  6. Shadowsocks              # 极简自用

  Which: 1
`

### 5.3 填写参数

**以 VLESS+Reality 为例：**

`
  Protocol: VLESS+Reality+Vision

  Port: 443
  Remark: default
  UUID (auto): a1b2c3d4-...-xxxx          # 自动生成

  Reality pubkey (pbk): Pp6QrLALjluABm...
  Fallback SNI: www.java.com
  shortId: 6ba85179e30d4fc2
  flow: xtls-rprx-vision

  [OK] Inbound added!

  Sample link:
  vless://a1b2c3d4...@1.2.3.4:443?type=tcp&security=reality...
`

>   pbk / shortId 这些参数在你 VPS 的 Xray 配置文件里找。  
> 如果用 mack-a 脚本，在 /etc/v2ray-agent/xray/conf/07_VLESS_vision_reality_inbounds.json

**以 VMess+WS+TLS 为例：**

`
  Protocol: VMess+WebSocket+TLS

  Port: 443
  Remark: ws-node
  UUID (auto): e5f6g7h8-...

  SNI: your-domain.com
  WS path: /ws123

  [OK] Inbound added!
`

---

## 6. 生成客户套餐卡

选菜单 3. Generate Card + QR：

### 6.1 选服务器 & 入站

`
[+] Select Server:
  1. my-vps (1.2.3.4)
  > 1

[+] Select Inbound:
  1. vless-reality-default
  > 1
`

### 6.2 填客户信息

`
  Customer name: zhangsan
`

### 6.3 选套餐

`
[+] Select Package:
  1. 轻量 - 100GB/month - Y25
  2. 标准 - 200GB/month - Y45
  3. 进阶 - 500GB/month - Y90
  4. Custom

  > 2
`

### 6.4 出图！

`
  [OK] Card: C:\Users\...\Desktop\zhangsan_card.png
  [OK] QR:   C:\Users\...\Desktop\zhangsan_QR.png

  Link:
  vless://new-uuid...@1.2.3.4:443?...#zhangsan
`

套餐卡会自动打开，桌面上同时生成两张图：
- zhangsan_card.png — 精美套餐卡（发给客户）
- zhangsan_QR.png — 纯二维码（方便发群）

---

## 7. 自定义套餐模板

编辑 ~/.proxyforge/config.yaml：

`yaml
packages:
  - name: ""体验""
    traffic: ""50GB""
    price: 10
    duration: ""月""
  - name: ""轻量""
    traffic: ""100GB""
    price: 25
    duration: ""月""
  - name: ""标准""
    traffic: ""200GB""
    price: 45
    duration: ""月""
  - name: ""进阶""
    traffic: ""500GB""
    price: 90
    duration: ""月""
  - name: ""旗舰""
    traffic: ""1000GB""
    price: 150
    duration: ""月""
`

改完重启 ProxyForge 即可生效。

---

## 8. Xray-core 下载 & 使用

ProxyForge 内置 Xray-core 下载器，选菜单 5 自动下载：

`
[*] Downloading Xray core...
  下载 Xray v25.2.21 (windows-64)...
  解压中...
  Xray 已安装到 ~/.proxyforge/xray
  [OK] Done
`

> 国内用户可能需要开代理才能下载（走 GitHub）。  
> 也可以手动下载 Xray-core 放到 ~/.proxyforge/xray/ 目录。

---

## 9. 实战：卖节点的完整工作流

### 流程总览

`
客户下单  打开 ProxyForge  菜单 3 生成套餐卡  发卡给客户
    ↓                                                    ↓
客户扫码导入   在 VPS 上用 lisa 脚本添加用户  完成
`

### 详细步骤

**Step 1 — 客户联系你**

> ""老板，来个 200G 的节点""

**Step 2 — 打开 ProxyForge**

`ash
cd proxyforge
python -m proxyforge.main
`

**Step 3 — 生成套餐卡**

`
3 → 选服务器 → 选入站 → 客户名: zhangsan → 选标准200G → 回车
`

桌面立刻生成 zhangsan_card.png。

**Step 4 — 发卡给客户**

把套餐卡图片发给客户，他扫二维码就能一键导入 v2rayN / NekoBox / Shadowrocket。

**Step 5 — 在 VPS 上添加用户**

SSH 进 VPS，运行 lisa 脚本（或用 X-UI 面板），把客户 UUID 加入 Xray 配置并重启：

`ash
lisa    # 或者 python3 /tmp/lisa.py
# 选 2 添加用户 → 填昵称/流量 → 记录 UUID
`

**Step 6 — 收钱，完事**

---

## 10. 常见问题

### Q: ""生成套餐卡时报错：找不到字体""

A: Windows 自动使用微软雅黑；Mac 用苹方；Linux 需要安装：

`ash
sudo apt install fonts-noto-cjk    # Ubuntu/Debian
sudo yum install google-noto-cjk   # CentOS
`

### Q: ""二维码扫出来打不开""

A: 检查 Host 填的是不是 VPS 公网 IP，端口有没有开放。可以用 v2rayN 手动导入链接测试。

### Q: ""Xray 下载失败""

A: 国内访问 GitHub 不稳定，开代理或手动下载 [Xray-core Releases](https://github.com/XTLS/Xray-core/releases)，解压到 ~/.proxyforge/xray/。

### Q: ""支持 IPv6 吗""

A: 支持，Host 填 IPv6 地址即可，如 [2001:db8::1]。

### Q: ""怎么生成批量套餐卡""

A: 目前用交互式菜单逐张生成。批量模式在开发计划中，欢迎提 PR。

---

##  联系 & 贡献

- GitHub Issues：[提交反馈](https://github.com/woaikefu5/proxyforge/issues)
- 欢迎 PR / Star  

---

**祝你生意兴隆，节点大卖！**
