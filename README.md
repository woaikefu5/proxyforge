<p align=""center"">
  <h1> ProxyForge</h1>
  <p><b>Xray 多协议管理 + 套餐卡一键生成</b></p>
  <p><code>Python 3.9+</code> · <code>Win / Mac / Linux</code> · <code>MIT</code> · <code>v1.0.0</code></p>
</p>

---

##  这是什么？

**ProxyForge** 是一个给节点主用的工具箱。

> 添加服务器  配置协议  生成客户的二维码套餐卡，三步搞定。

![demo card](assets/demo-card.png)

---

##  功能

| 模块 | 说明 |
|------|------|
|  多协议链接生成 | VLESS+Reality / VLESS+WS+TLS / VLESS+gRPC / VMess / Trojan / Shadowsocks |
|  Xray 自动下载 | 内置 Xray-core 下载器，无需手动安装 |
|  套餐卡生成 | 一键生成带二维码的客户套餐卡 (PNG) |
|  多服务器管理 | 同时管理多个 VPS 节点，每个节点多个入站 |
|  跨平台 | Windows / macOS / Linux 都能跑 |

---

##  支持的协议

| 协议 | 传输 | 安全 | 适用场景 |
|------|------|------|----------|
| VLESS | TCP | Reality+Vision |  推荐首选 |
| VLESS | WebSocket | TLS | CDN 友好 |
| VLESS | gRPC | TLS | 高性能 |
| VMess | WebSocket | TLS | 兼容旧客户端 |
| Trojan | TCP | TLS | 轻量伪装 |
| Shadowsocks | TCP | AEAD | 极简自用 |

---

##  快速开始

### 方式一：Python

`ash
git clone https://github.com/woaikefu5/proxyforge.git
cd proxyforge
pip install -r requirements.txt
python -m proxyforge.main
`

### 方式二：打包 EXE

`ash
pip install pyinstaller
pyinstaller --onefile --name ProxyForge proxyforge/main.py
`

---

##  使用流程

`
1. 添加服务器       输入 VPS IP
2. 添加入站协议     选 VLESS+Reality，填公钥/SNI/shortId
3. 生成套餐卡       填客户名 + 选套餐  出图到桌面！
`

首次运行会自动弹出配置引导，设置品牌名和联系方式。

---

##  配置

配置文件自动生成在 ~/.proxyforge/config.yaml：

`yaml
brand:
  name: ""我的节点""
  contact: ""@your_telegram""

servers:
  my-vps:
    host: ""1.2.3.4""
    inbounds:
      - tag: ""vless-reality-default""
        protocol: ""vless-reality""
        port: 443
        uuid: ""auto-generated""
        public_key: ""your-pbk""
        server_name: ""www.java.com""
        short_id: ""abc123""

packages:
  - name: ""轻量""
    traffic: ""100GB""
    price: 25
`

---

##  项目结构

`
proxyforge/
  main.py           CLI 交互菜单
  config.py         配置管理
  protocols.py      6 种协议链接生成
  cardgen.py        套餐卡 + 二维码
  xray.py           Xray-core 下载器
  assets/           展示图
`

---

##  免责声明

本工具仅供学习和技术交流。使用者需遵守当地法律法规。

##  License

MIT