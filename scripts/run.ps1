param(
    [ValidateSet('ingest', 'verify', 'test', 'test-all', 'embed', 'index', 'inspect', 'ask', 'chat', 'compatibility', 'traces', 'test-rag', 'ui')]
    [string]$Task = 'ui',
    [switch]$ForceReparse,
    [string]$Question = '',
    [ValidateSet('auto', 'cloud', 'local', 'none')][string]$QueryMode = 'auto',
    [ValidateSet('neo4j', 'offline')][string]$Backend = 'neo4j',
    [switch]$SkipRerank,
    [switch]$NoQueryPlanner,
    [switch]$NoFastPath,
    [switch]$NoPremiseCheck,
    [switch]$NoGraphCards,
    [switch]$SyncTraces,
    [switch]$LegacyMode,
    [int]$Port = 8501
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$sitePackages = Join-Path $projectRoot '.venv\Lib\site-packages'
if (-not (Test-Path -LiteralPath $venvPython)) { throw 'Project virtual environment not found' }

# Prefer .venv python; fall back cleanly to pyvenv.cfg base interpreter + PYTHONPATH if _ctypes DLL is restricted.
$pythonExe = $venvPython
$prevEap = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& $venvPython -c "import ctypes" 2>$null | Out-Null
$venvOk = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = $prevEap
if (-not $venvOk) {
    $cfgPath = Join-Path $projectRoot '.venv\pyvenv.cfg'
    $baseExe = $null
    if (Test-Path -LiteralPath $cfgPath) {
        foreach ($line in Get-Content -LiteralPath $cfgPath) {
            if ($line -match '^\s*executable\s*=\s*(.+)$') { $baseExe = $Matches[1].Trim(); break }
        }
    }
    if (-not $baseExe -or -not (Test-Path -LiteralPath $baseExe)) {
        $baseExe = Join-Path $env:LOCALAPPDATA 'Python\bin\python.exe'
    }
    if (-not (Test-Path -LiteralPath $baseExe)) { throw 'Fallback base Python executable not found' }
    $pythonExe = $baseExe
    $env:PYTHONPATH = "$sitePackages;$(Join-Path $projectRoot 'src')"
}

$cacheDir = Join-Path $projectRoot '.cache'
New-Item -ItemType Directory -Force -Path (Join-Path $cacheDir 'temp') | Out-Null
$env:TEMP = Join-Path $cacheDir 'temp'
$env:TMP = $env:TEMP
$env:PYTHONPYCACHEPREFIX = Join-Path $cacheDir 'pycache'
$env:PIP_CACHE_DIR = Join-Path $cacheDir 'pip'

function Build-AskFlags {
    $flags = @('--query-mode', $QueryMode, '--backend', $Backend)
    if ($SkipRerank) { $flags += '--skip-rerank' }
    if ($NoQueryPlanner) { $flags += '--no-query-planner' }
    if ($NoFastPath) { $flags += '--no-fast-path' }
    if ($NoPremiseCheck) { $flags += '--no-premise-check' }
    if ($NoGraphCards) { $flags += '--no-graph-cards' }
    if ($SyncTraces) { $flags += '--sync-traces' }
    if ($LegacyMode) { $flags += '--legacy-mode' }
    return $flags
}

Push-Location $projectRoot
try {
    switch ($Task) {
        'ingest' {
            if ($ForceReparse) { & $pythonExe -X utf8 scripts\ingest-pilot.py --force }
            else { & $pythonExe -X utf8 scripts\ingest-pilot.py }
        }
        'verify' { & $pythonExe -X utf8 scripts\verify-ingestion.py }
        'test' { & $pythonExe -X utf8 scripts\test-ingestion.py }
        'test-all' { & $pythonExe -X utf8 -m unittest discover -s tests -p "test_*.py" }
        'test-rag' { & $pythonExe -X utf8 scripts\test-rag.py }
        'ui' {
            & $pythonExe -X utf8 -m streamlit run app.py --server.address 127.0.0.1 --server.port $Port --server.headless true --browser.gatherUsageStats false
        }
        'ask' {
            $askArgs = @('-X', 'utf8', 'scripts/stage2.py', 'ask', '--question', $Question) + (Build-AskFlags)
            & $pythonExe @askArgs
        }
        'chat' {
            $chatArgs = @('-X', 'utf8', 'scripts/stage2.py', 'chat') + (Build-AskFlags)
            & $pythonExe @chatArgs
        }
        default { & $pythonExe -X utf8 scripts\stage2.py $Task }
    }
    if ($LASTEXITCODE -ne 0) { throw "Task $Task failed with exit code $LASTEXITCODE" }
}
finally { Pop-Location }
