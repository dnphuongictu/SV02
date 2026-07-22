param(
    [string]$Url,
    [string]$Dest
)

$h = @{"User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
try {
    Invoke-WebRequest -Uri $Url -OutFile $Dest -Headers $h -TimeoutSec 60
    $size = (Get-Item $Dest).Length
    Write-Host "SUCCESS: Size = $([math]::Round($size/1KB, 1)) KB"
} catch {
    Write-Host "FAILED: $_"
    exit 1
}