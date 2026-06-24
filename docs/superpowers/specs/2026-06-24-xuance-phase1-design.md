# 玄策 Phase 1 — VPS 核心升级设计文档

> 日期: 2026-06-24
> 项目: proxyforge / 馒头的玄策
> 状态: 已批准

## 概述

对 VPS 端玄策管理系统 (`xuance.py`) 进行核心升级：
1. 启用 Xray gRPC API 实现精确流量统计
2. 增加充值续费系统
3. 数据库升级为 JSON 格式

## 改动清单

### 1. Xray API 启用

新增 `/etc/v2ray-agent/xray/conf/01_api.json`：
- 启用 StatsService / HandlerService
- 本地 gRPC 端口 62789
- 路由规则指向直连出站

### 2. xuance.py 重构

| 功能 | 说明 |
|------|------|
| 精确流量统计 | 用 `xray api statsquery` 替代 journalctl 日志估算 |
| 充值续费 | 选择用户 → 输入流量(GB) + 天数 → 用量归零 + 限额增加 + 到期延长 |
| 数据库 JSON 化 | 从管道符文本改为 JSON，支持充值记录 |
| 老数据迁移 | 自动将旧 .db 迁移到新格式 |
| 到期检测 | 基于 expiry_date 而非注册日期 |
| 清理残留 | 自动忽略 http-user 等非 VLESS 记录 |

### 3. 数据库格式

`/root/xuance_users.json`:
```json
{
  "version": 2,
  "users": [
    {
      "uuid": "3fe93c65-...",
      "name": "3fe93c65-vless_reality_vision",
      "limit_gb": 999999,
      "used_bytes": 0,
      "expiry_date": "2026-07-24",
      "active": true
    }
  ]
}
```

### 4. 菜单变更

玄策菜单 v4.0:
```
1. 查看      — 显示用户 + API 精确流量
2. 添加      — 新增用户
3. 删除      — 删除用户
4. 充值      — 选择用户 → 充流量/延天数
5. 导出      — 导出所有 VLESS 链接
6. 检查      — API拉流量 + 超额/到期踢人
7. 退出
```

## 不变的部分

- CLI 交互风格不变
- VLESS 链接格式不变
- 现有的 install.sh 兼容
- 桌面端 proxyforge 不受影响
