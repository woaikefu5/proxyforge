<p align="center">
  <h1>馒头的玄策</h1>
  <p><b>VPS 用户管理系统 — 1核1G 轻松跑</b></p>
  <p><code>Python 3.9+</code> · <code>Linux VPS</code> · <code>MIT</code> · <code>v4.0</code></p>
  <p>
    <a href="https://github.com/woaikefu5/proxyforge/actions/workflows/ci.yml">
      <img src="https://github.com/woaikefu5/proxyforge/actions/workflows/ci.yml/badge.svg" alt="CI">
    </a>
  </p>
</p>

---

## 这是什么？

**馒头的玄策** — 给 VPS 节点主用的轻量用户管理工具箱。

> 装好 Xray 后一键部署，CLI 管理用户，自动踢超额/到期，支持充值续费。
> **最低配置：1核CPU + 1GB内存**，跑 Xray + 玄策无压力。

---

## 快速开始

### VPS 端（一键部署）

```bash
bash <(curl -sL https://raw.githubusercontent.com/woaikefu5/proxyforge/main/vps/install.sh)
```

安装后输入 `xuance` 进入管理菜单。

### 桌面端（套餐卡生成）

```bash
git clone https://github.com/woaikefu5/proxyforge.git
cd proxyforge
pip install -r requirements.txt
python -m proxyforge.main
```

---

## VPS 管理功能

| 功能 | 说明 |
|------|------|
| **查看用户** | 列出所有用户 + 实时流量统计 |
| **添加用户** | 自动生成 VLESS Reality 链接 |
| **删除用户** | 从 Xray 配置中移除 |
| **充值续费** | 重置流量 + 延长到期日 |
| **导出链接** | 批量导出所有客户端链接 |
| **自动检查** | 每小时检测，超额/到期自动踢人 |

---

## 运行环境

> **极低门槛**：1核CPU + 1GB内存的 VPS 即可流畅运行。
> Xray 核心 + 玄策管理系统内存占用不到 300MB。
> 支持 Ubuntu / Debian / CentOS。

---

## 详细教程

- 📖 [从零到卖节点完整教程](TUTORIAL.md)
- 📖 [详细使用指南](GUIDE.md)
- 📖 [更新日志](CHANGELOG.md)

---

## 支持作者

如果这个工具帮到了你，可以请我喝杯咖啡 ☕

<p align="center">
  <img src="https://raw.githubusercontent.com/woaikefu5/proxyforge/main/assets/wechat-donate.jpg" width="260" alt="微信打赏">
</p>

---

## License

MIT