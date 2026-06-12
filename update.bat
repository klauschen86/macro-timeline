@echo off
chcp 65001 > nul
cd /d "D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline"

C:\Users\chen8\.workbuddy\binaries\python\versions\3.13.12\python.exe scripts\run_daily.py

echo.
echo 更新完成。刷新浏览器中的 Dashboard 即可看到最新数据。
pause
