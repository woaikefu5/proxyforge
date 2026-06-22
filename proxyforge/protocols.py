"""馒头的玄策 - 多协议链接生成"""

import base64
import json
import uuid as _uuid


# ============ VLESS ============

def gen_vless_reality(host, port, user_uuid, public_key, server_name,
                      short_id="", flow="xtls-rprx-vision", remark=""):
    """VLESS + Reality + Vision"""
    link = (
        f"vless://{user_uuid}@{host}:{port}"
        f"?type=tcp&security=reality&flow={flow}"
        f"&fp=chrome&pbk={public_key}&sni={server_name}"
        f"&sid={short_id}"
        f"#{remark}"
    )
    return link


def gen_vless_ws_tls(host, port, user_uuid, server_name, path="/", remark=""):
    """VLESS + WebSocket + TLS"""
    link = (
        f"vless://{user_uuid}@{host}:{port}"
        f"?type=ws&security=tls&path={path}"
        f"&sni={server_name}&fp=chrome"
        f"#{remark}"
    )
    return link


def gen_vless_grpc(host, port, user_uuid, server_name, service_name="", remark=""):
    """VLESS + gRPC + TLS"""
    link = (
        f"vless://{user_uuid}@{host}:{port}"
        f"?type=grpc&security=tls&serviceName={service_name}"
        f"&sni={server_name}&fp=chrome"
        f"#{remark}"
    )
    return link


# ============ VMess ============

def gen_vmess(host, port, user_uuid, network="ws", path="/",
              tls="tls", server_name="", remark=""):
    """VMess 通用"""
    cfg = {
        "v": "2",
        "ps": remark,
        "add": host,
        "port": str(port),
        "id": user_uuid,
        "aid": "0",
        "scy": "auto",
        "net": network,
        "type": "none",
        "host": server_name,
        "path": path,
        "tls": tls,
        "sni": server_name,
        "fp": "chrome",
    }
    j = json.dumps(cfg, ensure_ascii=False)
    return "vmess://" + base64.b64encode(j.encode()).decode()


# ============ Trojan ============

def gen_trojan(host, port, password, server_name="", remark=""):
    """Trojan + TLS"""
    link = (
        f"trojan://{password}@{host}:{port}"
        f"?security=tls&sni={server_name}&fp=chrome"
        f"&type=tcp"
        f"#{remark}"
    )
    return link


# ============ Shadowsocks ============

def gen_ss(method, password, host, port, remark=""):
    """Shadowsocks"""
    userinfo = method + ":" + password
    b64 = base64.b64encode(userinfo.encode()).decode().rstrip("=")
    link = f"ss://{b64}@{host}:{port}#{remark}"
    return link


# ============ 工具 ============

def gen_uuid():
    return str(_uuid.uuid4())


def make_link(protocol, **kwargs):
    """统一入口，根据协议类型生成链接"""
    p = protocol.lower()
    if p == "vless-reality":
        return gen_vless_reality(**kwargs)
    elif p == "vless-ws-tls":
        return gen_vless_ws_tls(**kwargs)
    elif p == "vless-grpc":
        return gen_vless_grpc(**kwargs)
    elif p == "vmess":
        return gen_vmess(**kwargs)
    elif p == "trojan":
        return gen_trojan(**kwargs)
    elif p == "ss":
        return gen_ss(**kwargs)
    else:
        raise ValueError(f"不支持的协议: {protocol}")


SUPPORTED_PROTOCOLS = {
    "vless-reality": {"name": "VLESS+Reality+Vision", "fields": ["host", "port", "user_uuid", "public_key", "server_name", "short_id", "flow"]},
    "vless-ws-tls":  {"name": "VLESS+WebSocket+TLS",  "fields": ["host", "port", "user_uuid", "server_name", "path"]},
    "vless-grpc":    {"name": "VLESS+gRPC+TLS",       "fields": ["host", "port", "user_uuid", "server_name", "service_name"]},
    "vmess":         {"name": "VMess+WebSocket+TLS",   "fields": ["host", "port", "user_uuid", "network", "path", "server_name"]},
    "trojan":        {"name": "Trojan+TLS",            "fields": ["host", "port", "password", "server_name"]},
    "ss":            {"name": "Shadowsocks",           "fields": ["method", "password", "host", "port"]},
}
