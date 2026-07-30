# XuanCe Web Panel

Web management panel for XuanCe VPS proxy management system.

## Files
- `xuance_web.py` - Main web panel (Python, single file)
- `xuance-web.service` - systemd service file

## Deploy
1. Copy `xuance_web.py` to `/usr/local/bin/xuance_web` on VPS
2. Copy `xuance-web.service` to `/etc/systemd/system/`
3. `systemctl daemon-reload && systemctl enable --now xuance-web`

## Requirements
- Python 3
- Xray (mack-a v2ray-agent)
- XuanCe CLI (proxyforge)

## Endpoints
- Admin: `/admin` (POST login)
- User: `/user` (login with web_user/web_pass)
- API: `/api/admin/*`, `/api/user/*`
