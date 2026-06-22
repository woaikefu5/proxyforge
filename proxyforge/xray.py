"""馒头的玄策 - Xray 核心下载管理"""
import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

XRAY_DIR = Path.home() / ".proxyforge" / "xray"
XRAY_EXE = XRAY_DIR / ("xray.exe" if sys.platform == "win32" else "xray")


def get_platform():
    p = sys.platform
    if p == "win32":
        return "windows-64"
    elif p == "darwin":
        return "macos-64"
    else:
        # detect arch
        import platform
        m = platform.machine()
        if m in ("aarch64", "arm64"):
            return "linux-arm64-v8a"
        return "linux-64"


def get_latest_version():
    """获取 Xray-core 最新版本号"""
    try:
        req = Request(
            "https://api.github.com/repos/XTLS/Xray-core/releases/latest",
            headers={"User-Agent": "mantou-xuance"}
        )
        data = json.loads(urlopen(req, timeout=10).read())
        return data["tag_name"].lstrip("v")
    except Exception as e:
        print(f"  获取版本失败: {e}，使用默认版本 25.2.21")
        return "25.2.21"


def is_installed():
    return XRAY_EXE.exists()


def download_xray(version=None):
    """下载 Xray 核心"""
    if version is None:
        version = get_latest_version()
    
    plat = get_platform()
    filename = f"Xray-{plat}.zip"
    url = f"https://github.com/XTLS/Xray-core/releases/download/v{version}/{filename}"
    
    XRAY_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = XRAY_DIR / filename
    
    print(f"  下载 Xray v{version} ({plat})...")
    print(f"  {url}")
    
    try:
        req = Request(url, headers={"User-Agent": "mantou-xuance"})
        with urlopen(req, timeout=120) as resp:
            with open(zip_path, "wb") as f:
                f.write(resp.read())
    except URLError as e:
        if "443" in str(e) or "timeout" in str(e).lower():
            raise RuntimeError(
                "下载失败：无法连接 GitHub。\n"
                "  请确保已开启代理，或手动下载 Xray-core 放到:\n"
                f"  {XRAY_DIR}"
            )
        raise
    
    print("  解压中...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(XRAY_DIR)
    
    # macOS/Linux 可执行权限
    if sys.platform != "win32":
        os.chmod(XRAY_EXE, 0o755)
    
    os.remove(zip_path)
    print(f"  Xray 已安装到 {XRAY_DIR}")
    return str(XRAY_EXE)


def ensure_xray():
    """确保 Xray 已安装，没有则下载"""
    if is_installed():
        return str(XRAY_EXE)
    return download_xray()
