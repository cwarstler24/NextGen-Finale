param(
    [switch]$DryRun
)

$repoRoot = Split-Path -Parent $PSScriptRoot

$artifactPaths = @(
    'coverage',
    'pytestCov.html',
    '.pytest_cache',
    'testing/backend/.pytest_cache',
    '.coverage',
    '.coverage.*',
    'htmlcov',
    '.mypy_cache',
    '.ruff_cache',
    '.vite',
    '.vitest'
)

$removed = @()
$skipped = @()

foreach ($relativePath in $artifactPaths) {
    if ($relativePath.Contains('*')) {
        $matches = Get-ChildItem -Path $repoRoot -Force -Name $relativePath -ErrorAction SilentlyContinue
        foreach ($match in $matches) {
            $targetPath = Join-Path $repoRoot $match
            if ($DryRun) {
                Write-Host "[DRY RUN] Would remove: $targetPath"
            } else {
                Remove-Item -Recurse -Force -Path $targetPath -ErrorAction SilentlyContinue
                $removed += $targetPath
            }
        }
        continue
    }

    $targetPath = Join-Path $repoRoot $relativePath
    if (Test-Path $targetPath) {
        if ($DryRun) {
            Write-Host "[DRY RUN] Would remove: $targetPath"
        } else {
            Remove-Item -Recurse -Force -Path $targetPath -ErrorAction SilentlyContinue
            $removed += $targetPath
        }
    } else {
        $skipped += $targetPath
    }
}

$pyCacheDirs = Get-ChildItem -Path $repoRoot -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\venv\\|\\node_modules\\|\\.git\\' }

foreach ($dir in $pyCacheDirs) {
    if ($DryRun) {
        Write-Host "[DRY RUN] Would remove: $($dir.FullName)"
    } else {
        Remove-Item -Recurse -Force -Path $dir.FullName -ErrorAction SilentlyContinue
        $removed += $dir.FullName
    }
}

if ($DryRun) {
    Write-Host 'Dry run completed. No files were removed.'
} else {
    Write-Host "Cleanup completed. Removed $($removed.Count) path(s)."
}

if ($skipped.Count -gt 0) {
    Write-Host "Skipped $($skipped.Count) missing path(s)."
}
