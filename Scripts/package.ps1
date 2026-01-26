# ========================================
# 프로젝트 루트 탐색
# (.gitignore / requirements.txt / python-version.txt
#  중 하나라도 있으면 루트로 간주)
# ========================================

$ROOT_MARKERS = @(
    ".gitignore",
    "requirements.txt",
    "python-version.txt"
)

$currentDir = $PSScriptRoot
$PROJECT_ROOT = $null
$FOUND_MARKER = $null

while ($true) {
    foreach ($marker in $ROOT_MARKERS) {
        if (Test-Path (Join-Path $currentDir $marker)) {
            $PROJECT_ROOT = $currentDir
            $FOUND_MARKER = $marker
            break
        }
    }

    if ($PROJECT_ROOT) {
        break
    }

    $parentDir = Split-Path $currentDir -Parent
    if (-not $parentDir -or $parentDir -eq $currentDir) {
        break
    }

    $currentDir = $parentDir
}

if (-not $PROJECT_ROOT) {
    Write-Host "[FAIL] Project root not found."
    Write-Host "[FAIL] None of the following files were found in any parent directory:"
    foreach ($marker in $ROOT_MARKERS) {
        Write-Host "   - $marker"
    }
    exit 1
}

Set-Location $PROJECT_ROOT
Write-Host "[OK] Project root detected at:"
Write-Host "  $PROJECT_ROOT"
Write-Host "  (marker: $FOUND_MARKER)"
Write-Host ""

Write-Host "=== Release build start ==="
Write-Host "Project Root: $PROJECT_ROOT"

# 기존 빌드 폴더 제거
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# release 폴더 정리(선택)
Remove-Item -Recurse -Force release -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force release | Out-Null

# PyInstaller 빌드 (onedir)
pyinstaller --noconsole --onedir `
  --clean `
  --add-data "src\assets;assets" `
  --name "PC_Spec_Viewer" `
  src\main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] PyInstaller build failed."
    exit 1
}

# onedir / onefile 자동 대응
$distDir = Join-Path $PROJECT_ROOT "dist"

$onedirBundle = Join-Path $distDir "PC_Spec_Viewer"
$onefileExe   = Join-Path $distDir "PC_Spec_Viewer.exe"

if (Test-Path $onedirBundle) {
    Write-Host "[OK] onedir bundle detected"
    $sourcePath = $onedirBundle
}
elseif (Test-Path $onefileExe) {
    Write-Host "[OK] onefile exe detected"
    $sourcePath = $onefileExe
}
else {
    Write-Host "[FAIL] No valid build output found."
    exit 1
}

# release에 런타임 번들 전체 복사 (exe + dll + 포함된 파일들)
$releaseDir = Join-Path $PROJECT_ROOT "release\PC_Spec_Viewer"
Copy-Item $sourcePath $releaseDir -Recurse -Force

Write-Host "=== Release build complete ==="
Write-Host "Release Folder: $releaseDir"
Write-Host "EXE: $($releaseDir)\PC_Spec_Viewer.exe"
