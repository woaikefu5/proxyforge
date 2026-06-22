#  馒头的玄策 详细使用教程

##  目录

1. [环境准备](#1-环境准备)
2. [安装 馒头的玄策](#2-安装-proxyforge)
3. [首次运行 & 品牌配置](#3-首次运行--品牌配置)
4. [添加 VPS 服务器](#4-添加-vps-服务器)
5. [配置入站协议](#5-配置入站协议)
6. [生成客户套餐卡](#6-生成客户套餐卡)
7. [自定义套餐模板](#7-自定义套餐模板)
8. [VPS 端部署（用户管理+流量监控）](#8-vps-端部署)
9. [实战：卖节点的完整工作流](#9-实战卖节点的完整工作流)
10. [常见问题](#10-常见问题)

---

## 1. 环境准备

- **Python 3.9+**：python.org 下载安装
- **Git**（可选）：git-scm.com
- 一台 VPS，已安装 Xray（推荐 mack-a/v2ray-agent 一键脚本）

---

## 2. 安装 馒头的玄策

```bash
git clone https://github.com/woaikefu5/proxyforge.git
cd proxyforge
pip install -r requirements.txt
python -m proxyforge.main
```

---

## 3. 首次运行 & 品牌配置

自动弹出配置，填品牌名和联系方式。也可随时按 6 修改。

---

## 4. 添加 VPS 服务器

```
1. Add Server  输入服务器ID和IP
```

---

## 5. 配置入站协议

```
2. Add Inbound  选服务器  选协议  填参数
```

支持 VLESS+Reality / WS+TLS / gRPC / VMess / Trojan / Shadowsocks。

---

## 6. 生成客户套餐卡

```
3. Generate Card  选服务器  选入站  填客户名  选套餐  出图！
```

套餐卡自动保存到桌面。

---

## 7. 自定义套餐模板

菜单按 7 进入套餐管理：

```
[*] Package Management

  1. Light      100GB/month  Y25
  2. Standard   200GB/month  Y45
  3. Pro        500GB/month  Y90

  1. Add  2. Edit  3. Delete  4. Back
```

或直接编辑 ~/.proxyforge/config.yaml 里的 packages:。

---

## 8. VPS 端部署

### 8.1 一键安装

SSH 进 VPS，运行：

```bash
curl -sL https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/install.sh | bash
```

### 8.2 首次配置

```bash
python3 /root/xuance.py
```

首次运行会提示输入：服务器IP、端口、Reality公钥、SNI、shortId。

### 8.3 功能菜单

```
  === 玄策 v3.0 ===

  1.查看  2.添加  3.删除  4.导出  5.检查  6.退出
```

| 菜单 | 功能 |
|------|------|
| 1 查看 | 所有用户+流量使用量 |
| 2 添加 | 新客户，自动生成 VLESS 链接 |
| 3 删除 | 踢掉用户 |
| 4 导出 | 批量导出所有链接 |
| 5 检查 |  流量统计 + 超额自动停 + 30天到期自动停 |
| 6 退出 | |

### 8.4 工作原理

- **流量统计**：每5分钟从 Xray 日志估算字节数（约5MB/连接）
- **超额检查**：used >= limit 自动踢人
- **到期检查**：注册日期>30天自动踢人
- **数据库**：/root/xuance_users.db 存储所有用户

> 需要你的 Xray 配置文件路径为: /etc/v2ray-agent/xray/conf/07_VLESS_vision_reality_inbounds.json  
> 如果路径不同，修改 xuance.py 顶部的 CONF 变量。

---

## 9. 实战：卖节点的完整工作流

```
客户下单  馒头的玄策 菜单7设套餐  VPS xuance 菜单2加用户  复制UUID
                                                               
贴入馒头的玄策菜单3  套餐卡出图发客户  客户扫码即用
                                                               
VPS xuance 菜单5 定期检查  超额/到期自动踢  收钱
```

---

## 10. 常见问题

### Q: "生成套餐卡时找不到字体"

A: Windows 自动用微软雅黑；Mac 用苹方；Linux：

```bash
sudo apt install fonts-noto-cjk
```

### Q: "VPS 端 xuance 报错找不到配置"

A: 确认 Xray 配置路径正确。编辑 /root/xuance.py 顶部的 CONF 变量。

### Q: "流量统计不准确"

A: 当前基于日志估算（~5MB/连接）。精确统计需 Xray API 支持，后续版本改进。

### Q: "怎么改30天为其他期限"

A: 编辑 xuance.py，搜索 days=30 改为你需要的天数。

---

##  联系 & 贡献

- GitHub Issues：https://github.com/woaikefu5/proxyforge/issues
- 欢迎 PR / Star  

**祝你生意兴隆！**