@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================
echo   宏观数据时间轴 - 手机访问模式
echo ============================================
echo.

echo [1/2] 更新数据...
python scripts\run_daily.py 2>nul

echo.
echo [2/2] 启动 HTTP 服务...

powershell -NoProfile -Command ^
  "$ip = (Get-NetIPAddress -AddressFamily IPv4 ^| Where-Object {$_.InterfaceAlias -match '以太|WLAN|Wi-Fi|无线|Ethernet'} ^| Select-Object -First 1).IPAddress; ^
   if (-not $ip) { $ip = (ipconfig ^| Select-String 'IPv4.*: (\\d+\\.\\d+\\.\\d+\\.\\d+)' ^| ForEach-Object {$_.Matches.Groups[1].Value} ^| Where-Object {$_ -notlike '169.254.*'} ^| Select-Object -First 1) }; ^
   if (-not $ip) { $ip = '127.0.0.1' }; ^
   Write-Host ''; ^
   Write-Host '============================================'; ^
   Write-Host ''; ^
   Write-Host '   请在手机浏览器打开：'; ^
   Write-Host ''; ^
   Write-Host ('       http://' + $ip.Trim() + ':8765'); ^
   Write-Host ''; ^
   Write-Host '   确保手机和电脑在同一 WiFi 网络下！'; ^
   Write-Host ''; ^
   Write-Host '   打开后操作：'; ^
   Write-Host '     Chrome  - 菜单 - 添加到主屏幕'; ^
   Write-Host '     其他浏览器 - 菜单 - 添加书签到桌面'; ^
   Write-Host ''; ^
   Write-Host '   按 Ctrl+C 停止服务'; ^
   Write-Host '============================================'; ^
   Write-Host ''"

echo.
echo 正在启动服务...
python -m http.server 8765
pause
