$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = Join-Path $Root "src"
$Ucrt64Bin = "C:\msys64\ucrt64\bin"
if (Test-Path (Join-Path $Ucrt64Bin "g++.exe")) {
    $env:PATH = "$Ucrt64Bin;$env:PATH"
}

$PythonCommand = $null
foreach ($Candidate in @(
    @{ Exe = "py"; Args = @("-3.11") },
    @{ Exe = "py"; Args = @("-3") },
    @{ Exe = "python"; Args = @() }
)) {
    try {
        $VersionOutput = & $Candidate.Exe @($Candidate.Args) -V 2>$null
        if (
            $LASTEXITCODE -eq 0 `
            -and $VersionOutput -match "Python (\d+)\.(\d+)" `
            -and [int]$Matches[1] -eq 3 `
            -and [int]$Matches[2] -ge 11
        ) {
            $PythonCommand = $Candidate
            break
        }
    } catch {
        continue
    }
}

if (-not $PythonCommand) {
    throw "Python 3.11 or newer was not found. Install Python from https://www.python.org/downloads/"
}

& $PythonCommand.Exe @($PythonCommand.Args) -m cf_workbench @args
