param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$source = Join-Path $root 'database'
$index = Join-Path $source 'papers_index.csv'
$output = Join-Path $root 'artifacts\reports\stage-0-step-2'

function Get-SharedHash([string]$Path) {
    $stream = $null
    $sha = $null
    try {
        # Some applications keep the index open for writing; this stream is read-only.
        $stream = [IO.File]::Open($Path, 'Open', 'Read', 'ReadWrite')
        $sha = [Security.Cryptography.SHA256]::Create()
        return [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        if ($sha) { $sha.Dispose() }
        if ($stream) { $stream.Dispose() }
    }
}

function Export-Rows($Rows, [string]$Name, [string[]]$Columns) {
    $target = Join-Path $output $Name
    if (@($Rows).Count -gt 0) {
        $Rows | Select-Object $Columns | Export-Csv -LiteralPath $target -NoTypeInformation -Encoding UTF8
    }
    else {
        (($Columns | ForEach-Object { '"' + $_ + '"' }) -join ',') |
            Set-Content -LiteralPath $target -Encoding UTF8
    }
}

$indexHashBefore = Get-SharedHash $index
$rows = @(Import-Csv -LiteralPath $index -Encoding UTF8)
$required = @('分类', '序号', '标题', '状态', '本地文件')
foreach ($column in $required) {
    if ($rows.Count -eq 0 -or $column -notin $rows[0].PSObject.Properties.Name) {
        throw "CSV column missing or CSV empty: $column"
    }
}

# Enumeration errors stop this run rather than reporting an incomplete scan as complete.
$items = @(Get-ChildItem -LiteralPath $source -Recurse -Force)
if (@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count -gt 0) {
    throw 'Reparse point found in database; review scan scope before following it.'
}
$files = @($items | Where-Object { -not $_.PSIsContainer })
$manifest = @(foreach ($file in $files) {
    $hash = ''
    $status = 'readable'
    $errorText = ''
    try { $hash = Get-SharedHash $file.FullName }
    catch { $status = 'unreadable'; $errorText = $_.Exception.Message }
    [pscustomobject]@{
        relative_path = $file.FullName.Substring($source.Length + 1).Replace('\', '/')
        filename = $file.Name
        size_bytes = $file.Length
        sha256 = $hash
        read_status = $status
        error = $errorText
    }
})
$byPath = @{}
foreach ($file in $manifest) { $byPath[$file.relative_path] = $file }
$checks = @(for ($i = 0; $i -lt $rows.Count; $i++) {
    $row = $rows[$i]
    $local = $row.'本地文件'.Trim()
    $expected = ''
    $status = 'no_local_file'
    if ($local) {
        $expected = ($row.'分类'.Trim() + '/' + $local).Replace('\', '/')
        $full = [IO.Path]::GetFullPath((Join-Path $source $expected))
        if (-not $full.StartsWith($source + '\', [StringComparison]::OrdinalIgnoreCase)) {
            throw "CSV path escapes database at row $($i + 2)"
        }
        $status = 'missing_file'
        if ($byPath.ContainsKey($expected)) { $status = $byPath[$expected].read_status }
    }
    [pscustomobject]@{
        csv_row = $i + 2
        category = $row.'分类'
        number = $row.'序号'
        title = $row.'标题'
        csv_status = $row.'状态'
        local_filename = $local
        expected_relative_path = $expected
        check_status = $status
    }
})
$missing = @($checks | Where-Object check_status -eq 'missing_file')
$noLocal = @($checks | Where-Object check_status -eq 'no_local_file')
$unreadable = @($manifest | Where-Object read_status -eq 'unreadable')
$duplicateContent = @($manifest | Where-Object sha256 | Group-Object sha256 |
    Where-Object Count -gt 1 | ForEach-Object {
        [pscustomobject]@{ sha256 = $_.Name; paths = @($_.Group.relative_path) }
    })
$duplicateEntries = @($checks | Where-Object expected_relative_path |
    Group-Object expected_relative_path | Where-Object Count -gt 1 | ForEach-Object {
        [pscustomobject]@{ relative_path = $_.Name; csv_rows = @($_.Group.csv_row) }
    })
$indexHashAfter = Get-SharedHash $index
if ($indexHashBefore -ne $indexHashAfter) { throw 'CSV changed during scan; rerun against a stable index.' }

$summary = [ordered]@{
    manifest_version = '1'
    scanned_at = (Get-Date).ToString('o')
    source_root = $source
    scan_scope = 'All regular files under database, recursive, including hidden files; no exclusions.'
    pdf_validation = 'Byte readability and SHA-256 only; PDF parsing not performed.'
    csv_matching = 'category/local_filename relative to database; case-insensitive Windows paths'
    csv_sha256_before = $indexHashBefore
    csv_sha256_after = $indexHashAfter
    csv_unchanged = ($indexHashBefore -eq $indexHashAfter)
    scanned_files = $manifest.Count
    pdf_files = @($manifest | Where-Object { [IO.Path]::GetExtension($_.filename) -ieq '.pdf' }).Count
    csv_rows = $rows.Count
    csv_rows_with_filename = @($checks | Where-Object local_filename).Count
    existing_csv_files = @($checks | Where-Object { $_.check_status -in @('readable', 'unreadable') }).Count
    missing_files = $missing.Count
    no_local_file_rows = $noLocal.Count
    unreadable_files = $unreadable.Count
    duplicate_content_groups = $duplicateContent.Count
    duplicate_csv_path_groups = $duplicateEntries.Count
    csv_status_counts = @($rows | Group-Object '状态' | ForEach-Object {
        [pscustomobject]@{ status = $_.Name; count = $_.Count }
    })
}

New-Item -ItemType Directory -Force -Path $output | Out-Null
$manifestColumns = @('relative_path', 'filename', 'size_bytes', 'sha256', 'read_status', 'error')
$checkColumns = @('csv_row', 'category', 'number', 'title', 'csv_status', 'local_filename', 'expected_relative_path', 'check_status')
Export-Rows $manifest 'manifest.csv' $manifestColumns
Export-Rows $checks 'csv-check.csv' $checkColumns
Export-Rows $missing 'missing-files.csv' $checkColumns
Export-Rows $noLocal 'no-local-file.csv' $checkColumns
Export-Rows $unreadable 'unreadable-files.csv' $manifestColumns
ConvertTo-Json -InputObject $duplicateContent -Depth 5 | Set-Content (Join-Path $output 'duplicate-content.json') -Encoding UTF8
ConvertTo-Json -InputObject $duplicateEntries -Depth 5 | Set-Content (Join-Path $output 'duplicate-csv-entries.json') -Encoding UTF8
$summary | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $output 'summary.json') -Encoding UTF8
$summary | ConvertTo-Json -Depth 5
