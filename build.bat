@echo off
chcp 65001 >nul
echo ========================================
echo   馒头的玄策 - 打包 EXE
echo ========================================
echo.
echo 安装 pyinstaller...
pip install pyinstaller -q
echo.
echo 打包中...
pyinstaller --onefile --clean --name MantouXuance proxyforge/main.py
echo.
echo ========================================
echo   完成! 文件在 dist\MantouXuance.exe
echo ========================================
pause
