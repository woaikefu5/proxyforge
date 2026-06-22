import io
with open(r"D:\ProxyForge\proxyforge\cardgen.py", "r", encoding="utf-8") as f:
    content = f.read()

old = 'Powered by \u9992\u5934\u7684\u7384\u7b56 | woaikefu5'
new = '\u514d\u8d23: \u4ec5\u4f9b\u5b66\u4e60\u4ea4\u6d41 \u00b7 \u4f7f\u7528\u4e0e\u672c\u4eba\u65e0\u5173", fill="#777777", font=font_small)\n    draw.text((40, 640), "Powered by \u9992\u5934\u7684\u7384\u7b56 | woaikefu5'

content = content.replace(old, new)
with open(r"D:\ProxyForge\proxyforge\cardgen.py", "w", encoding="utf-8") as f:
    f.write(content)
print("OK")
