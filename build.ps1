# Builds dist\LangProfileSwitcher-Setup.exe (Inno Setup 6) from a PyInstaller one-folder build.
# Pure ASCII on purpose (Windows PowerShell 5.1). Usage: .\build.ps1   [-SkipInstaller]
param([switch]$SkipInstaller)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

python -m pip install --disable-pip-version-check -q -r requirements-dev.txt
python -m unittest discover -s tests
if ($LASTEXITCODE) { throw 'Tests failed - not building.' }

$version = (python -c "import langprofile; print(langprofile.__version__)").Trim()
New-Item -ItemType Directory -Force build | Out-Null
python -c "from PySide6.QtWidgets import QApplication; app = QApplication([]); from langprofile import theme; theme.apply(app); assert theme.app_icon().pixmap(256).save('build/app.ico')"

python -m PyInstaller --noconfirm --clean --onedir --windowed --add-data "langprofile/assets;langprofile/assets" `
    --name LangProfileSwitcher --icon build\app.ico run.py
if ($LASTEXITCODE) { throw 'PyInstaller failed.' }
if ($SkipInstaller) { return }

$iscc = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe", "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
          "$env:ProgramFiles\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { throw 'Inno Setup 6 not found. Install it: winget install JRSoftware.InnoSetup' }
& $iscc /Q "/DAppVersion=$version" installer\LangProfileSwitcher.iss
if ($LASTEXITCODE) { throw 'Inno Setup failed.' }

$setup = Get-Item dist\LangProfileSwitcher-Setup.exe
"Built v$version -> $($setup.FullName) ($([math]::Round($setup.Length / 1MB, 1)) MB)"
"SHA256 $((Get-FileHash $setup -Algorithm SHA256).Hash)"
