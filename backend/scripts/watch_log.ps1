# 日志监控脚本（PowerShell版本）
# 使用方法: powershell -ExecutionPolicy Bypass -File backend/scripts/watch_log.ps1

$logFile = Join-Path $PSScriptRoot "..\..\backend\logs\app.log"

if (-not (Test-Path $logFile)) {
    Write-Host "日志文件不存在: $logFile" -ForegroundColor Red
    exit 1
}

Write-Host "开始监控日志文件: $logFile" -ForegroundColor Green
Write-Host "按 Ctrl+C 退出`n" -ForegroundColor Yellow

try {
    # 从文件末尾开始读取
    $reader = [System.IO.StreamReader]::new($logFile, [System.Text.Encoding]::UTF8)
    $reader.BaseStream.Seek(0, [System.IO.SeekOrigin]::End) | Out-Null

    while ($true) {
        $line = $reader.ReadLine()
        if ($line) {
            Write-Host $line
        } else {
            Start-Sleep -Milliseconds 100
        }
    }
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
} finally {
    if ($reader) {
        $reader.Dispose()
    }
    Write-Host "`n停止监控日志文件" -ForegroundColor Green
}
