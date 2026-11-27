param([switch]$Start)
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$root = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $root '.runtime'
$downloads = Join-Path $root '.cache/downloads'
$tempPath = Join-Path $root '.cache/temp'
New-Item -ItemType Directory -Force -Path $runtime,$downloads,$tempPath | Out-Null
$env:TEMP = $tempPath
$env:TMP = $tempPath
$env:JAVA_TOOL_OPTIONS = "-Djava.io.tmpdir=$tempPath -Djna.tmpdir=$tempPath"
$neoName = 'neo4j-community-5.26.12'
$neoZip = Join-Path $downloads "$neoName-windows.zip"
$neoHome = Join-Path $runtime $neoName
if (-not (Test-Path -LiteralPath $neoHome)) {
    $uri = "https://dist.neo4j.org/$neoName-windows.zip"
    if (-not (Test-Path -LiteralPath $neoZip)) { Invoke-WebRequest -UseBasicParsing -Uri $uri -OutFile $neoZip }
    # Official .sha256 retrieved during setup; pin rather than rely on another download.
    $expected = 'd8f4fc840bd8108ae811a960910208b63b5d75b1f837ed4ec837b5b8d8e268ab'
    if ((Get-FileHash -LiteralPath $neoZip -Algorithm SHA256).Hash.ToLower() -ne $expected.ToLower()) { throw 'Neo4j download checksum mismatch' }
    Expand-Archive -LiteralPath $neoZip -DestinationPath $runtime
}
$java = Get-ChildItem -LiteralPath $runtime -Directory | Where-Object Name -Like 'zulu21*' | Select-Object -First 1
if (-not $java) {
    $releases = Invoke-RestMethod -Uri 'https://api.azul.com/metadata/v1/zulu/packages/?java_version=21&os=windows&arch=x86&archive_type=zip&java_package_type=jre&latest=true&release_status=ga&availability_types=CA'
    $release = $releases | Where-Object { $_.name -notmatch '-fx-' -and $_.name -match 'win_x64' } | Select-Object -First 1
    if (-not $release) { throw 'No compatible official JRE found' }
    $javaZip = Join-Path $downloads $release.name
    if (-not (Test-Path -LiteralPath $javaZip)) { Invoke-WebRequest -UseBasicParsing -Uri $release.download_url -OutFile $javaZip }
    $details = Invoke-RestMethod -Uri ('https://api.azul.com/metadata/v1/zulu/packages/'+$release.package_uuid)
    $expected = $details.sha256_hash
    if ((Get-FileHash -LiteralPath $javaZip -Algorithm SHA256).Hash.ToLower() -ne $expected.ToLower()) { throw 'Java download checksum mismatch' }
    Expand-Archive -LiteralPath $javaZip -DestinationPath $runtime
    $java = Get-ChildItem -LiteralPath $runtime -Directory | Where-Object Name -Like 'zulu21*' | Select-Object -First 1
}
$env:JAVA_HOME = $java.FullName
$env:NEO4J_HOME = $neoHome
$configPath = Join-Path $neoHome 'conf/neo4j.conf'
$marker = '# PaperTech local configuration'
if (-not (Select-String -LiteralPath $configPath -Pattern $marker -SimpleMatch -Quiet)) {
    Add-Content -LiteralPath $configPath -Encoding UTF8 -Value @'

# PaperTech local configuration
server.default_listen_address=127.0.0.1
server.memory.heap.initial_size=256m
server.memory.heap.max_size=512m
server.memory.pagecache.size=256m
dbms.security.procedures.unrestricted=
dbms.usage_report.enabled=false
'@
}
# An existing .env/password is never overwritten. Cloud fields remain blank.
$envPath = Join-Path $root '.env'
if (-not (Test-Path -LiteralPath $envPath)) { Copy-Item -LiteralPath (Join-Path $root '.env.example') -Destination $envPath }
$lines = Get-Content -LiteralPath $envPath -Encoding UTF8
$passwordLine = $lines | Where-Object { $_ -match '^NEO4J_PASSWORD=.+' } | Select-Object -First 1
if (-not $passwordLine) {
    $password = 'ptg-' + [Guid]::NewGuid().ToString('N')
    # Password is passed only to this local admin process, never printed in reports.
    & (Join-Path $neoHome 'bin/neo4j-admin.bat') dbms set-initial-password $password | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Neo4j initial password setup failed' }
    $lines = $lines -replace '^NEO4J_PASSWORD=.*$', ('NEO4J_PASSWORD='+$password)
    [System.IO.File]::WriteAllLines($envPath, $lines, (New-Object System.Text.UTF8Encoding($false)))
}
if ($Start) {
    $existing = Get-NetTCPConnection -LocalPort 7687 -State Listen -ErrorAction SilentlyContinue
    if (-not $existing) {
        $launcher = Join-Path $runtime 'start-neo4j.ps1'
        $text = "`$env:JAVA_HOME='$($java.FullName)'`r`n`$env:NEO4J_HOME='$neoHome'`r`n`$env:TEMP='$tempPath'`r`n`$env:TMP='$tempPath'`r`n`$env:JAVA_TOOL_OPTIONS='-Djava.io.tmpdir=$tempPath -Djna.tmpdir=$tempPath'`r`n& '$neoHome\bin\neo4j.bat' console"
        [System.IO.File]::WriteAllText($launcher,$text,(New-Object System.Text.UTF8Encoding($false)))
        $process = Start-Process powershell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$launcher) -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtime 'neo4j-console.log') -RedirectStandardError (Join-Path $runtime 'neo4j-console.err') -PassThru
        $process.Id | Set-Content -LiteralPath (Join-Path $runtime 'neo4j-launcher.pid')
        Write-Output "Neo4j console launched (PID $($process.Id)); logs under .runtime."
    } else { Write-Output 'Bolt port already listening; verify server identity with stage2 inspect.' }
}
Write-Output "Neo4j: $neoHome"
Write-Output "Java: $($java.FullName)"
