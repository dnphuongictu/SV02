# SPDX-License-Identifier: Apache-2.0
[CmdletBinding()]
param([string]$ProjectRoot)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$required = @(
    "README.md", "AGENTS.md", "CLAUDE.md", "LICENSE",
    "THIRD_PARTY_NOTICES.md", "CONTRIBUTING.md",
    "src/index.html", "src/js/app.js", "tests/all.test.mjs",
    "data/study_session.schema.json",
    "docs/07_KIEN_TRUC_VA_DANH_MUC_ARTIFACT.md",
    "handoff/README.md", ".github/workflows/ci.yml"
)

Write-Host "FocusMate AI - kiem tra bo ban giao"
Write-Host "Root: $ProjectRoot"
$missing = @($required | Where-Object {
    -not (Test-Path -LiteralPath (Join-Path $ProjectRoot $_))
})
if ($missing.Count -gt 0) {
    throw "Thieu tep bat buoc: $($missing -join ', ')"
}
Write-Host "[PASS] Tep bat buoc"

Get-Content -Raw -LiteralPath (Join-Path $ProjectRoot "package.json") |
    ConvertFrom-Json | Out-Null
Get-Content -Raw -LiteralPath (Join-Path $ProjectRoot "data/study_session.schema.json") |
    ConvertFrom-Json | Out-Null
Write-Host "[PASS] JSON hop le"

$ownedCode = Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "src") -Recurse -File |
    Where-Object { $_.Extension -in ".js", ".css", ".html" }
$withoutSpdx = @($ownedCode | Where-Object {
    -not (Select-String -LiteralPath $_.FullName -Pattern "SPDX-License-Identifier: Apache-2.0" -Quiet)
})
if ($withoutSpdx.Count -gt 0) {
    throw "Tep ma thieu SPDX: $($withoutSpdx.FullName -join ', ')"
}
Write-Host "[PASS] SPDX tren ma san pham"

Push-Location $ProjectRoot
try {
    & npm test
    if ($LASTEXITCODE -ne 0) { throw "npm test that bai: $LASTEXITCODE" }
}
finally { Pop-Location }
Write-Host "[PASS] 24 test"
Write-Host "Bo ban giao hop le."
