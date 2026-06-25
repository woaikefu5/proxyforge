# 玄策 XuanCe v4.1 - One-Click Proxy Management
# 1核1G VPS 就能跑 | Runs on 1GB RAM VPS
FROM ubuntu:24.04

LABEL org.xuance.version="4.1"
LABEL org.xuance.description="XuanCe VLESS Reality Proxy Manager"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip ca-certificates python3 python3-pip jq openssl \
    && rm -rf /var/lib/apt/lists/*

# Install Xray
ARG XRAY_VERSION=25.4.5
RUN curl -sL "https://github.com/XTLS/Xray-core/releases/download/v${XRAY_VERSION}/Xray-linux-64.zip" -o /tmp/xray.zip \
    && unzip -o /tmp/xray.zip -d /usr/local/xray/ \
    && chmod +x /usr/local/xray/xray \
    && rm /tmp/xray.zip

RUN pip3 install --break-system-packages grpcio typing-extensions 2>/dev/null || true

RUN mkdir -p /etc/v2ray-agent/xray/conf /data /root

# Copy everything
COPY xuance.py /root/xuance.py
COPY xuance_web.py /root/xuance_web.py
COPY xuance_sub.py /root/xuance_sub.py
COPY xuance_bot.py /root/xuance_bot.py
COPY entrypoint.sh /entrypoint.sh
COPY xray-conf/ /etc/v2ray-agent/xray/conf/

RUN chmod +x /entrypoint.sh /root/xuance.py

EXPOSE 443/tcp 28080/tcp 28081/tcp

VOLUME ["/data"]
ENTRYPOINT ["/entrypoint.sh"]
