# ProxyForge 🚀

> 傻瓜式 Xray 多协议管理 + 套餐卡生成器  
> 下载 → 配置 → 出卡，三步搞定

---

## ✨ 功能

- 🎯 **多协议支持**: VLESS+Reality, VLESS+WS+TLS, VLESS+gRPC, VMess, Trojan, Shadowsocks
- 📦 **Xray 自动下载**: 内置 Xray-core 下载，无需手动安装
- 🎨 **套餐卡生成**: 一键生成带二维码的精美套餐卡
- 🧾 **客户管理**: 多服务器、多入站统一管理
- 🖥 **跨平台**: Windows / macOS / Linux

## 📥 快速开始

### 方式一：直接下载 EXE (推荐)

从 [Releases](https://github.com/your/proxyforge/releases) 下载 `ProxyForge.exe`，双击运行。

### 方式二：Python 运行

```bash
# 1. 克隆
git clone https://github.com/your/proxyforge.git
cd proxyforge

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python -m proxyforge.main
```

## 📖 使用教程

### 第一步：配置品牌

首次运行会自动弹出配置引导，设置品牌名称和联系方式。

### 第二步：添加服务器

```
1 → 输入服务器ID和IP
```

### 第三步：添加入站协议

```
2 → 选择服务器 → 选择协议 → 填写参数
```

支持的协议：

| 协议 | 传输 | 安全 |
|------|------|------|
| VLESS | TCP | Reality+Vision |
| VLESS | WebSocket | TLS |
| VLESS | gRPC | TLS |
| VMess | WebSocket | TLS |
| Trojan | TCP | TLS |
| Shadowsocks | TCP | AEAD |

### 第四步：生成套餐卡

```
3 → 选择服务器和入站 → 填写客户名 → 选套餐 → 出图！
```

套餐卡保存到桌面，包含二维码和客户信息。

## 🛠 配置说明

配置文件位于 `~/.proxyforge/config.yaml`：

```yaml
brand:
  name: "我的节点"
  contact: "@your_telegram"

packages:
  - name: "轻量"
    traffic: "100GB"
    price: 25
    duration: "月"

servers:
  my-vps:
    host: "1.2.3.4"
    inbounds:
      - tag: "vless-reality-default"
        protocol: "vless-reality"
        port: 443
        uuid: "xxxx-xxxx"
        ...
```

## 🔨 打包成 EXE

```bash
pip install pyinstaller
pyinstaller --onefile --name ProxyForge proxyforge/main.py
```

## ⚠️ 免责声明

本工具仅供学习和合法使用。请遵守当地法律法规。

## 📄 License

MIT
