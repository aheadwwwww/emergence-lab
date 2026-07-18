<#
.SYNOPSIS
    知识库更新脚本 (PowerShell 版)
    扫描探索笔记、实验代码和记忆文件，更新 knowledge_base.json
#>

$workspace = "."
$categories = @{
    "exploration" = @{ "path" = "exploration"; "pattern" = "*.md" }
    "experiments" = @{ "path" = "experiments"; "pattern" = "*.py" }
    "memory"      = @{ "path" = "memory";      "pattern" = "*.md" }
}

$kb = @{
    "last_updated" = (Get-Date -Format "o")
    "categories" = @{}
}

foreach ($catName in $categories.Keys) {
    $cat = $categories[$catName]
    $dir = Join-Path $workspace $cat.path
    if (-not (Test-Path $dir)) { continue }

    $items = Get-ChildItem -Path $dir -Filter $cat.pattern -Recurse:$($catName -eq "memory") | ForEach-Object {
        @{
            "name"     = $_.BaseName
            "path"     = $_.Path.Replace((Resolve-Path $workspace).Path + "\", "").Replace("/", "\")
            "size"     = $_.Length
            "modified" = $_.LastWriteTime.ToString("o")
        }
    }

    $sorted = $items | Sort-Object -Property modified -Descending
    $kb.categories[$catName] = @{
        "count" = $sorted.Count
        "items" = $sorted
    }
}

$outputPath = Join-Path $workspace "knowledge_base.json"
$json = $kb | ConvertTo-Json -Depth 4
[System.IO.File]::WriteAllText((Resolve-Path $outputPath).Path, $json, [System.Text.UTF8Encoding]::new($false))

Write-Host "[OK] Knowledge base updated: $outputPath"
Write-Host "  - Exploration notes: $($kb.categories['exploration'].count)"
Write-Host "  - Experiment files: $($kb.categories['experiments'].count)"
Write-Host "  - Memory files: $($kb.categories['memory'].count)"
