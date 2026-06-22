"""馒头的玄策 - 配置文件管理"""
import yaml
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "brand": {
        "name": "馒头的玄策",
        "contact": "@your_telegram",
        "logo_text": ""
    },
    "servers": {},
    "packages": [
        {"name": "轻量", "traffic": "100GB", "price": 25, "duration": "月"},
        {"name": "标准", "traffic": "200GB", "price": 45, "duration": "月"},
        {"name": "进阶", "traffic": "500GB", "price": 90, "duration": "月"},
    ],
    "xray_version": "latest",
}

CONFIG_DIR = Path.home() / ".proxyforge"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def ensure_dirs():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    ensure_dirs()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            # merge with defaults for backward compat
            merged = DEFAULT_CONFIG.copy()
            merged.update(cfg)
            return merged
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)


def get_server(server_id):
    cfg = load_config()
    return cfg["servers"].get(server_id)


def add_server(server_id, host, **kwargs):
    cfg = load_config()
    cfg["servers"][server_id] = {
        "host": host,
        "inbounds": [],
        **kwargs,
    }
    save_config(cfg)


def add_inbound(server_id, inbound):
    cfg = load_config()
    if server_id not in cfg["servers"]:
        raise ValueError(f"服务器 {server_id} 不存在")
    cfg["servers"][server_id].setdefault("inbounds", []).append(inbound)
    save_config(cfg)
