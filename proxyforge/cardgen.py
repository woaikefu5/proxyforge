"""馒头的玄策 - 套餐卡 + 二维码生成"""
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont


def _get_fonts():
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return (
                    ImageFont.truetype(fp, 36),
                    ImageFont.truetype(fp, 22),
                    ImageFont.truetype(fp, 18),
                    ImageFont.truetype(fp, 28),
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
                  brand_name="馒头的玄策", contact="@me",
                  features=None):
    font_title, font_body, font_small, font_link = _get_fonts()

    card_w, card_h = 800, 650
    card = Image.new("RGB", (card_w, card_h), "#0f0f23")
    draw = ImageDraw.Draw(card)

    draw.line([(30, 75), (770, 75)], fill="#e94560", width=2)
    draw.text((40, 25), f"{brand_name} .套餐卡", fill="#e94560", font=font_title)

    traffic = package_info.get("traffic", "")
    price = package_info.get("price", 0)
    duration = package_info.get("duration", "月")

    info = [
        (f"客户: {name}", 95),
        (f"流量: {traffic}/{duration}", 135),
        (f"价格: Y{price}/{duration}", 175),
    ]
    if features:
        for i, feat in enumerate(features):
            info.append((f"  {feat}", 215 + i * 35))

    for text, y in info:
        draw.text((40, y), text, fill="#ffffff", font=font_body)

    qr_img = generate_qr(link)
    card.paste(qr_img, (380, 95))

    short = link[:60] + "..." if len(link) > 63 else link
    draw.text((40, 420), short, fill="#888888", font=font_small)

    draw.line([(30, 560), (770, 560)], fill="#e94560", width=1)
    draw.text((40, 575), "扫码导入 即开即用", fill="#aaaaaa", font=font_body)
    draw.text((40, 610), f"联系: {contact}", fill="#aaaaaa", font=font_small)

    card.save(output_path)
    return output_path


def generate_customer_card(name, uuid, link, package_info,
                           brand_name, contact, output_dir, features=None):
    os.makedirs(output_dir, exist_ok=True)
    safe_name = "".join(c for c in name if c.isalnum() or c in "_-")
    qr_path = os.path.join(output_dir, f"{safe_name}_QR.png")
    card_path = os.path.join(output_dir, f"{safe_name}_card.png")
    generate_qr(link, qr_path)
    generate_card(name, link, package_info, card_path,
                  brand_name=brand_name, contact=contact, features=features)
    return card_path, qr_path
