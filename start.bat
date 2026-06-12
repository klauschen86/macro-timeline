@echo off
chcp 65001 > nul
cd /d "D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline"

echo ========================================
echo   宏观数据时间轴 Macro Timeline
echo ========================================
echo.
echo [1/2] 更新数据...
C:\Users\chen8\.workbuddy\binaries\python\versions\3.13.12\python.exe scripts\run_daily.py

echo.
echo [2/2] 打开 Dashboard...
start "" "D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\index.html"

echo.
echo Dashboard 已在浏览器中打开。
echo 下次更新请运行此 start.bat。
pause
