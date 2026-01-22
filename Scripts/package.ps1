# 항상 프로젝트 루트 기준으로 실행
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $PROJECT_ROOT

# 터미널에서 .\package.ps1 로 실행

Write-Host "=== Release build start (src-based) ==="
Write-Host "Project Root: $PROJECT_ROOT"

# 기존 빌드 폴더 제거
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# PyInstaller 빌드
pyinstaller --noconsole --onefile `
  --clean `
  --icon=src\assets\ico_out-nano-logo_blue.ico `
  --add-data="src\assets;assets" `
  --name "PC_Spec_Viewer" `
  src\main.py

# 릴리즈 폴더 생성
New-Item -ItemType Directory -Force release

# 결과물 이동
Copy-Item dist\PC_Spec_Viewer.exe release\ -Recurse

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] PyInstaller build failed."
    exit 1
}

$exePath = "dist\PC_Spec_Viewer.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "[FAIL] Output exe not found: $exePath"
    exit 1
}

Copy-Item $exePath "release\" -Force
Write-Host "=== Release build complete ==="
