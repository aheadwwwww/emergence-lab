<#
.SYNOPSIS
    知识库更新脚本 (PowerShell 版)
    扫描探索笔记、实验代码和记忆文件，更新 knowledge_base.json
#>

$workspace = Resolve-Path "."
$categories = @{
    "exploration" = @{ "path" = "exploration"; "pattern" = "*.md"; "recurse" = $false }
    "experiments" = @{ "path" = "experiments"; "pattern" = "*.py";  "recurse" = $false }
    "memory"      = @{ "path" = "memory";      "pattern" = "*.md";  "recurse" = $true }
}

$kb = @{
    "last_updated" = (Get-Date -Format "o")
    "categories" = @{}
}

foreach ($catName in $categories.Keys) {
    $cat = $categories[$catName]
    $dir = Join-Path $workspace $cat.path
    if (-not (Test-Path $dir)) { 
        Write-Host "[WARN] Directory not found: $dir"
        continue 
    }

    $items = Get-ChildItem -Path $dir -Filter $cat.pattern -Recurse:$cat.recurse
    
    $itemList = @()
    foreach ($item in $items) {
        $relPath = $item.FullName.Substring($workspace.Path.Length + 1)
        $itemList += @{
            "name"     = $item.BaseName
            "path"     = $relPath
            "size"     = $item.Length
            "modified" = $item.LastWriteTime.ToString("o")
        }
    }

    $sorted = $itemList | Sort-Object -Property modified -Descending
    $kb.categories[$catName] = @{
        "count" = $sorted.Count
        "items" = $sorted
    }
}

$outputPath = [System.IO.Path]::Combine($workspace.Path, "knowledge_base.json")
$json = $kb | ConvertTo-Json -Depth 4
[System.IO.File]::WriteAllText($outputPath, $json, [System.Text.UTF8Encoding]::new($false))

Write-Host "[OK] Knowledge base updated: knowledge_base.json"
Write-Host "  - Exploration notes: $($kb.categories['exploration'].count)"
Write-Host "  - Experiment files: $($kb.categories['experiments'].count)"
Write-Host "  - Memory files: $($kb.categories['memory'].count)"
