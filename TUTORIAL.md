# 馒头的玄策 · 从零到卖节点完整教程

> 零基础也能看懂的 VPS 卖节点全流程。  
> 从买服务器到客户扫码上网，每一步都有。

---

## 目录

1. [买 VPS 服务器](#1-买-vps-服务器)
2. [登录你的 VPS](#2-登录你的-vps)
3. [安装 Xray（一键脚本）](#3-安装-xray一键脚本)
4. [安装玄策 VPS 管理系统](#4-安装玄策-vps-管理系统)
5. [桌面安装馒头的玄策](#5-桌面安装馒头的玄策)
6. [完整出单流程](#6-完整出单流程)
7. [日常运维](#7-日常运维)
8. [常见问题](#8-常见问题)

---

## 1. 买 VPS 服务器

### 1.1 推荐商家

| 商家 | 特点 | 适合 |
|------|------|------|
| **RackNerd** | 便宜稳定，黑五常年有货 | 新手首选 |
| **BandwagonHost（搬瓦工）** | 线路好，CN2 GIA | 追求速度 |
| **Vultr** | 按小时计费，随时删 | 测试用 |
| **DigitalOcean** | 稳定，全球多机房 | 长期用 |
| **AkileCloud** | 国内商家，支付宝付款 | 不想折腾外币 |

### 1.2 配置选择

| 用途 | CPU | 内存 | 流量 | 价格参考 |
|------|-----|------|------|----------|
| 个人自用 | 1 核 | 512MB | 500GB/月 | ~/年 |
| 小规模卖（3-10 人） | 1 核 | 1GB | 1TB/月 | ~/年 |
| 中等规模（10-30 人） | 2 核 | 2GB | 3TB/月 | ~/年 |
| 大规模（30+ 人） | 4 核 | 4GB | 5TB+ | ~/年 |

>   **省钱技巧**：RackNerd 每逢黑色星期五/圣诞/新年有超低折扣，-20/年拿下 1GB 内存机型。

### 1.3 机房选择

- **亚洲客户为主**：选洛杉矶、圣何塞、新加坡、日本
- **国内用户为主**：CN2 GIA 线路（搬瓦工洛杉矶 DC6/DC9）
- **无所谓延迟**：美西最便宜

---

## 2. 登录你的 VPS

### 2.1 下载 SSH 工具

- **Windows**：[FinalShell](https://www.hostbuf.com/)（中文界面，推荐）或 [MobaXterm](https://mobaxterm.mobatek.net/)
- **Mac**：自带终端，或 [Termius](https://termius.com/)
- **iOS/Android**：Termius、JuiceSSH

### 2.2 连接 VPS

买完 VPS 后，商家会给你：
- **IP 地址**：如 192.168.1.1
- **端口**：默认 22
- **用户名**：默认 oot
- **密码**：随机生成的密码（首次登录后建议修改）

打开 FinalShell，新建连接，填上 IP、端口、用户名、密码，点连接。

---

## 3. 安装 Xray（一键脚本）

### 3.1 推荐：mack-a 八合一脚本

SSH 登录后，直接复制粘贴这条命令：

`ash
bash <(wget -qO- https://raw.githubusercontent.com/mack-a/v2ray-agent/master/install.sh)
`

按照提示操作：
1. 选 1（安装）
2. 选 1（VLESS+TCP+XTLS / VLESS+TCP+TLS）— **推荐 Reality 协议**
3. 输入你的域名（如果没有，脚本会自动用 IP 生成）
4. 等待安装完成

### 3.2 获取关键参数

安装完成后，脚本会输出：

`
VLESS + Reality + Vision 配置：
  端口: 443（或你自定义的）
  协议: vless
  传输: tcp
  安全: reality
  flow: xtls-rprx-vision
  publicKey: Pp6QrLALjluABmSyEjMq1...   ← 这就是 PBK
  shortId: 6ba85179e30d4fc2              ← 这就是 SID
  serverName: www.java.com               ← 这就是 SNI
`

记下这三个参数：**PBK**、**SID**、**SNI**、**端口号**。后面要用。

---

## 4. 安装玄策 VPS 管理系统

### 4.1 一键安装

在 VPS 上跑：

`ash
bash <(curl -sL https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/install.sh)
`

### 4.2 首次配置

输入 xuance 进入管理系统，首次运行会提示：

`
服务器IP:          ← 填你的 VPS 公网 IP
端口 (默认443):     ← 填你的 Xray 端口
Reality公钥(pbk):   ← 填第 3 步记下的 PBK
回落SNI:           ← 填 SNI，默认回车
shortId:           ← 填第 3 步记下的 SID
Xray配置路径:       ← 默认 /etc/v2ray-agent/xray/conf/... 回车即可
`

配置完就进主菜单了。

### 4.3 玄策菜单说明

`
1. 查看  — 列出所有用户，显示流量使用
2. 添加  — 添加新客户，自动生成 VLESS 链接
3. 删除  — 删除用户
4. 导出  — 导出所有用户链接
5. 检查  — 流量统计 + 超额自动踢 + 30天到期自动踢
6. 退出
`

>   **强烈建议**：把「检查」加到 crontab 定时跑，例如每小时一次。
> `ash
> echo "0 * * * * python3 /root/xuance.py -c 'cl()' 2>/dev/null" | crontab -
> `

---

## 5. 桌面安装馒头的玄策

### 5.1 安装 Python

- [python.org](https://python.org) 下载 Python 3.9+
- 安装时 **勾选 "Add Python to PATH"**

### 5.2 下载项目

`ash
git clone https://github.com/woaikefu5/proxyforge.git
cd proxyforge
pip install -r requirements.txt
`

> 不会用 Git？直接点 GitHub 页面上的绿色 "Code" → "Download ZIP"，解压后进目录。

### 5.3 运行

`ash
python -m proxyforge.main
`

### 5.4 首次配置

自动弹出设置：
`
Brand name: 你的品牌名（如 "极速云"）
Contact: 你的联系方式（如 "@jisuyun"）
`

### 5.5 添加服务器和协议

按 1 添加服务器，按 2 添加入站协议（填入 VPS 的参数）。

### 5.6 设定套餐

按 7 进入套餐管理，预设你的套餐：

`
轻量   100GB/月  ￥25
标准   200GB/月  ￥45
进阶   500GB/月  ￥90
旗舰   1000GB/月 ￥150
`

---

## 6. 完整出单流程

### Step 1 — 客户联系你

> "老板，来个 200G/月"

### Step 2 — VPS 上添加用户

`ash
xuance
> 2                          # 选添加
昵称: zhangsan               # 客户名
流量上限GB: 200              # 套餐流量
`

复制生成的那一串 less:// 开头的链接和 UUID。

### Step 3 — 桌面生成套餐卡

`
python -m proxyforge.main
> 3                          # 生成卡
选服务器 → 选入站
客户名: zhangsan
选套餐: 标准 200GB
`

桌面秒出 zhangsan_card.png 套餐卡！

### Step 4 — 发卡 + 收钱

把套餐卡图片发给客户，他扫码就能在 v2rayN / Shadowrocket / NekoBox 一键导入。

收钱 → 完成！

---

## 7. 日常运维

### 7.1 每天看一眼

`ash
xuance
> 5    # 检查流量 + 超额/到期自动处理
> 1    # 查看所有用户状态
`

### 7.2 加新套餐

桌面馒头的玄策 → 按 7 → 添加/编辑套餐。

### 7.3 踢人

`ash
xuance
> 3    # 删除用户
`

### 7.4 备份数据库

`ash
cp /root/xuance_users.db /root/xuance_users.db.bak
`

---

## 8. 常见问题

### Q: 客户说连不上
A: 检查 VPS 端口是否开放：
`ash
ss -tlnp | grep 你的端口
`
如果没监听，重启 Xray：systemctl restart xray

### Q: 流量统计准吗
A: 当前基于日志估算，约 5MB/连接，有 ±10% 误差。精确统计需要 Xray API，后续版本会改进。

### Q: 怎么改 30 天到期
A: 编辑 /root/xuance.py，搜索 days=30 改成你要的天数。

### Q: 商家跑路了怎么办
A: 数据库在 /root/xuance_users.db，定期备份。换 VPS 后跑一遍安装脚本，恢复数据库就行。

### Q: 怎么收钱
A: 微信/支付宝收款码，或者用 USDT（推荐 [Binance](https://binance.com)）。国外客户用 PayPal 或加密货币。

---

##  总结

`
  买 VPS（RackNerd /年）
       ↓
  装 Xray（bash 一键脚本，5 分钟）
       ↓
  装玄策（bash 一键脚本，30 秒）
       ↓
  桌面装馒头的玄策（pip install，1 分钟）
       ↓
  设套餐 → 接单 → 出卡 → 收钱！
`

**从 0 到卖节点，30 分钟全搞定。**

---

>   开源不易，欢迎 [Star](https://github.com/woaikefu5/proxyforge)  
>   有问题提 [Issues](https://github.com/woaikefu5/proxyforge/issues)