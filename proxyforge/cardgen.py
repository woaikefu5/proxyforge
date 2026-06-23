# -*- coding: utf-8 -*-
"""馒头的玄策 - 套餐卡 + 二维码 + Clash配置 生成器"""
import os, sys, platform, json
import qrcode
from PIL import Image, ImageDraw, ImageFont


def _get_fonts():
    system = platform.system()
    font_paths = []
    
    if system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/simsun.ttc",
        ]
    elif system == "Darwin":
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]
    else:
        import subprocess
        result = subprocess.run(["fc-list", ":lang=zh"], capture_output=True, text=True, timeout=5)
        if result.stdout:
            for line in result.stdout.split("\n"):
                path = line.split(":")[0].strip()
                if path and path not in font_paths:
                    font_paths.append(path)
        if not font_paths:
            font_paths = [
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            ]
    
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return (
                    ImageFont.truetype(fp, 36), ImageFont.truetype(fp, 22),
                    ImageFont.truetype(fp, 18), ImageFont.truetype(fp, 28),
                )
            except:
                pass
    return (ImageFont.load_default(),) * 4


def generate_qr(data, path=None, size=400):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data)
    qr.make()
    img = qr.make_image(fill="black", back_color="white").convert("RGB")
    img = img.resize((size, size))
    if path:
        img.save(path)
    return img


def generate_card(name, link, package_info, output_path,
                  brand_name="馒头的玄策", contact="woaikefu5@gmail.com",
                  features=None):
    font_title, font_body, font_small, font_link = _get_fonts()
    card = Image.new("RGB", (800, 650), "#0f0f23")
    draw = ImageDraw.Draw(card)

    draw.line([(30, 75), (770, 75)], fill="#e94560", width=2)
    draw.text((40, 25), f"{brand_name} · 套餐卡", fill="#e94560", font=font_title)

    traffic = package_info.get("traffic", "")
    price = package_info.get("price", 0)
    duration = package_info.get("duration", "月")
    protocol = package_info.get("protocol", "")

    info = [(f"客户: {name}", 95)]
    if protocol:
        info.append((f"协议: {protocol}", 130))
    info += [(f"流量: {traffic}/{duration}", 170),
             (f"价格: ¥{price}/{duration}", 210)]

    if features:
        for i, feat in enumerate(features):
            info.append((f"  {feat}", 250 + i * 35))

    for text, y in info:
        draw.text((40, y), text, fill="#ffffff", font=font_body)

    qr_img = generate_qr(link)
    card.paste(qr_img, (380, 95))

    short = link[:60] + "..." if len(link) > 63 else link
    draw.text((40, 420), short, fill="#888888", font=font_small)
    draw.line([(30, 560), (770, 560)], fill="#e94560", width=1)
    draw.text((40, 575), "扫码导入 即开即用", fill="#aaaaaa", font=font_body)
    draw.text((40, 610), f"联系: {contact}", fill="#aaaaaa", font=font_small)
    draw.text((40, 632), "免责: 仅供学习交流 · 使用与本人无关", fill="#777777", font=font_small)
    draw.text((40, 640), f"Powered by {brand_name} | {contact}",
              fill="#555555", font=font_small)
    card.save(output_path)
    return output_path


def generate_clash_yaml(name, server, port, username, password, output_path,
                        protocol="http", brand_name="馒头的玄策"):
    """生成Clash Verge兼容的YAML配置文件"""
    node_name = f"{brand_name} {name}"
    yaml = f"""# Clash Verge 配置 - {brand_name}
# 生成时间: 即开即用
# 注意: 流量耗尽或到期后此配置失效

port: 7890
socks-port: 7891
allow-lan: true
mode: Rule
log-level: info

proxies:
  - name: "{node_name}"
    type: {protocol}
    server: {server}
    port: {port}
    username: {username}
    password: {password}
    udp: false
"""
    if protocol == "http":
        yaml += "    tls: false\n"
    
    yaml += f"""
proxy-groups:
  - name: Proxy
    type: select
    proxies:
      - "{node_name}"

rules:
  - MATCH,Proxy
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(yaml)
    return output_path


def generate_all(name, protocol, server, port, username, password,
                 package_info, output_dir, brand_name="馒头的玄策",
                 contact="woaikefu5@gmail.com", features=None):
    """生成全套：二维码 + 套餐卡图片 + Clash YAML配置"""
    os.makedirs(output_dir, exist_ok=True)
    safe = "".join(c for c in name if c.isalnum() or c in "_-")
    
    if protocol == "http":
        link = f"http://{username}:{password}@{server}:{port}"
    else:
        link = f"vless://{username}@{server}:{port}?type=tcp&security=reality"
    
    qr_path = os.path.join(output_dir, f"{safe}_QR.png")
    card_path = os.path.join(output_dir, f"{safe}_card.png")
    yaml_path = os.path.join(output_dir, f"{safe}_clash.yaml")
    
    generate_qr(link, qr_path)
    generate_card(name, link, package_info, card_path,
                  brand_name=brand_name, contact=contact, features=features)
    generate_clash_yaml(name, server, port, username, password, yaml_path,
                        protocol=protocol, brand_name=brand_name)
    
    return {"qr": qr_path, "card": card_path, "clash": yaml_path}
