# XuanCe 部署流程（和94一模一样）

## 前提
- Ubuntu 22.04/24.04
- 已安装 Python3

## 步骤

### 1. 安装 Xray（mack-a v3.5.20 旧版 → 生成 config.json）
bash <(wget -qO- https://raw.githubusercontent.com/woaikefu5/proxyforge/main/deploy/macka_v3.5.20_install.sh)
# 选1安装 → 选3 VLESS+Reality → 无域名

### 2. 合并API配置（config.json加API+stats+策略+路由豁免）
python3 -c "
import json
c=json.load(open('/etc/v2ray-agent/xray/config.json'))
c['api']={'tag':'api','services':['HandlerService','LoggerService','StatsService']}
c['stats']={}
c.setdefault('policy',{}).setdefault('levels',{}).setdefault('0',{})['statsUserUplink']=True
c['policy']['levels']['0']['statsUserDownlink']=True
c['policy'].setdefault('system',{})['statsOutboundUplink']=True
c['policy']['system']['statsOutboundDownlink']=True
c.setdefault('inbounds',[]).append({'listen':'127.0.0.1','port':8080,'protocol':'dokodemo-door','settings':{'address':'127.0.0.1'},'tag':'api'})
c['routing']['rules'].insert(0,{'type':'field','inboundTag':['api'],'outboundTag':'api'})
json.dump(c,open('/etc/v2ray-agent/xray/config.json','w'),indent=2)
systemctl restart xray
"

### 3. 一键部署 xuance
bash deploy.sh

### 4. 验证
xray api statsquery --server=127.0.0.1:8080
# 应该返回含有 "user>>>" 的统计数据

## 绝对禁止
- 不要用新版mack-a（会生成confdir模式）
- 不要在confdir下加API（会爆内存）
- 94已经跑通的每一步，184一模一样复制

## 关键文件
- Xray配置: /etc/v2ray-agent/xray/config.json (单文件模式)
- 用户数据: /root/xuance_users.json 
- Daemon: /root/xuance_traffic_daemon.py (v10差量累加)
- 面板: /usr/local/bin/xuance_web
- 管理: http://IP:8318/admin (admin123456)
