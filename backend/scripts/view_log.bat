@echo off
chcp 65001 >nul
echo ====================================
echo     逸流后端日志查看工具
echo ====================================
echo.
echo 选择操作:
echo   1. 实时监控日志（推荐）
echo   2. 查看最后50行
echo   3. 查看最后100行
echo   4. 查看完整日志
echo   5. 清空日志
echo   0. 退出
echo.
set /p choice=请输入选项 (0-5):

if "%choice%"=="1" goto watch
if "%choice%"=="2" goto tail50
if "%choice%"=="3" goto tail100
if "%choice%"=="4" goto full
if "%choice%"=="5" goto clear
if "%choice%"=="0" goto end

:watch
echo.
echo 实时监控日志（按 Ctrl+C 停止）...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0watch_log.ps1"
goto end

:tail50
echo.
echo 最后50行日志:
echo.
powershell -Command "Get-Content '%~dp0..\logs\app.log' -Tail 50 -Encoding UTF8"
goto end

:tail100
echo.
echo 最后100行日志:
echo.
powershell -Command "Get-Content '%~dp0..\logs\app.log' -Tail 100 -Encoding UTF8"
goto end

:full
echo.
echo 完整日志内容:
echo.
powershell -Command "Get-Content '%~dp0..\logs\app.log' -Encoding UTF8"
goto end

:clear
echo.
echo 确定要清空日志文件吗？(Y/N)
set /p confirm=
if /i "%confirm%"=="Y" (
    echo. > "%~dp0..\logs\app.log"
    echo 日志文件已清空
) else (
    echo 取消清空操作
)
goto end

:end
echo.
pause
