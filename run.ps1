# Run from a Visual Studio Developer PowerShell with Python 3 installed.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force -Path build | Out-Null
cl /nologo /std:c++17 /EHsc /O2 /W4 src/main.cpp /Fe:build/migrator.exe
if ($LASTEXITCODE -ne 0) { throw "C++ build failed" }
python server.py @args
