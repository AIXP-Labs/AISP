param(
  [string]$Root = (Split-Path -Parent $PSScriptRoot),
  [switch]$RequireClean,
  [switch]$IncludePytest
)

$ErrorActionPreference = "Stop"

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$oldPythonDontWriteBytecode = $env:PYTHONDONTWRITEBYTECODE
$env:PYTHONDONTWRITEBYTECODE = "1"

function Invoke-Checked([string]$Label, [scriptblock]$Command) {
  Write-Host "==> $Label"
  $global:LASTEXITCODE = 0
  & $Command
  if ($LASTEXITCODE -ne 0) {
    throw "$Label failed with exit code $LASTEXITCODE"
  }
}

function Invoke-JsonSyntaxCheck {
  Get-ChildItem -LiteralPath $rootPath -Recurse -Force -File -Filter "*.json" |
    Where-Object {
      $rel = $_.FullName.Substring($rootPath.Length + 1)
      -not ($rel -split '[\\/]' | Where-Object { $_ -eq ".git" })
    } |
    ForEach-Object {
      try {
        Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
      } catch {
        throw "Invalid JSON in $($_.FullName): $($_.Exception.Message)"
      }
    }
  Write-Host "json syntax ok"
}

function Assert-NoForbiddenResidue {
  $names = @(
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".execution_cache",
    ".evolution_snapshot",
    ".version_history",
    "build",
    "dist"
  )
  $dirs = @(Get-ChildItem -LiteralPath $rootPath -Recurse -Force -Directory |
    Where-Object { $names -contains $_.Name })
  $files = @(Get-ChildItem -LiteralPath $rootPath -Recurse -Force -File |
    Where-Object { $_.Extension -in @(".pyc", ".pyo") })
  if ($dirs.Count -or $files.Count) {
    $items = @($dirs.FullName + $files.FullName)
    throw "Forbidden generated residue found:`n$($items -join "`n")"
  }
  Write-Host "No forbidden generated residue found."
}

function Assert-NoPrivatePathLeak {
  $patterns = @(
    @{ Label = "Windows user profile path"; Value = ("C:" + [char]92 + "Users" + [char]92) },
    @{ Label = "Windows user profile path with forward slashes"; Value = ("C:" + [char]47 + "Users" + [char]47) },
    @{ Label = "local D-drive absolute path"; Value = ("D:" + [char]92) },
    @{ Label = "local D-drive absolute path with forward slash"; Value = ("D:" + [char]47) },
    @{ Label = "local username"; Value = ("lg" + "uoc") },
    @{ Label = "private key marker"; Value = ("BEGIN " + "PRIVATE KEY") },
    @{ Label = "RSA private key marker"; Value = ("BEGIN " + "RSA " + "PRIVATE KEY") },
    @{ Label = "OpenSSH private key marker"; Value = ("BEGIN " + "OPENSSH " + "PRIVATE KEY") }
  )
  $hits = @()
  Get-ChildItem -LiteralPath $rootPath -Recurse -Force -File |
    Where-Object {
      $rel = $_.FullName.Substring($rootPath.Length + 1)
      -not ($rel -split '[\\/]' | Where-Object { $_ -eq ".git" }) -and
      $_.Length -lt 5MB
    } |
    ForEach-Object {
      try {
        $text = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
      } catch {
        return
      }
      foreach ($pattern in $patterns) {
        if ($text.IndexOf($pattern.Value, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
          $hits += "$($_.FullName): contains $($pattern.Label)"
        }
      }
    }
  if ($hits.Count) {
    throw "Potential private path/key leak found:`n$($hits -join "`n")"
  }
  Write-Host "No private path/key leak found outside .git."
}

function Assert-NoForbiddenAiapFiles {
  $names = @("AIAP.md", "agent_card.json", "quality_baseline.json", "main.aisop.json", "node_engine.aisop.json")
  $found = @(Get-ChildItem -LiteralPath $rootPath -Recurse -Force -File |
    Where-Object {
      $rel = $_.FullName.Substring($rootPath.Length + 1)
      -not ($rel -split '[\\/]' | Where-Object { $_ -eq ".git" }) -and
      $names -contains $_.Name
    })
  if ($found.Count) {
    throw "Forbidden AIAP-structure files found:`n$($found.FullName -join "`n")"
  }
  Write-Host "No forbidden AIAP-structure files found."
}

function Assert-CleanWorkingTree {
  $status = @(git status --porcelain=v1 --untracked-files=all)
  if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE"
  }
  if ($status.Count) {
    throw "Working tree is not clean:`n$($status -join "`n")"
  }
  Write-Host "Working tree is clean."
}

Push-Location $rootPath
try {
  Invoke-Checked "JSON syntax" { Invoke-JsonSyntaxCheck }
  Invoke-Checked "unit tests" { python -B -m unittest discover -s tests }
  if ($IncludePytest) {
    Invoke-Checked "pytest tests" { python -B -m pytest -q -p no:cacheprovider }
  }
  Invoke-Checked "generated per-skill READMEs" { python -B tools/aisp_readme.py examples --check-all }
  Invoke-Checked "generated Agent Skills sidecars" { python -B tools/aisp_skill_md.py examples --check-all }
  Invoke-Checked "Agent Skills bridge validation" { python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme }
  Invoke-Checked "example AISP directory validation" { python -B tools/aisp_validate.py examples/aisp }
  Invoke-Checked "JSON report output validation" { python -B tools/aisp_validate.py --json examples/aisp/yijing_aisp }
  Invoke-Checked "strict README validation" { python -B tools/aisp_validate.py --strict-readme examples/aisp }
  Invoke-Checked "stock hard tool-enforcement evidence" { python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json examples/aisp/stock_analysis_aisp }
  Invoke-Checked "creator hard tool-enforcement evidence" { python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json examples/aisp/aisp_creator_evolution_aisp }
  Invoke-Checked "runtime trace fixture" { python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json }
  Invoke-Checked "creator runtime trace fixture" { python -B tools/aisp_check_runtime_trace.py examples/aisp/aisp_creator_evolution_aisp examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json }
  Invoke-Checked "provenance hashes" { python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp }
  Invoke-Checked "generated AISP index" { python -B examples/aisp/aisp_list.py --check }
  Invoke-Checked "docs command synchronization" { python -B tools/check_doc_sync.py --root . }
  Invoke-Checked "local Markdown links" { python -B tools/check_markdown_links.py --root . }
  Invoke-Checked "whitespace errors" { git diff --check }

  Write-Host "==> generated residue scan"
  Assert-NoForbiddenResidue
  Write-Host "==> private path/key scan"
  Assert-NoPrivatePathLeak
  Write-Host "==> forbidden AIAP-structure scan"
  Assert-NoForbiddenAiapFiles

  if ($RequireClean) {
    Invoke-Checked "clean working tree" { Assert-CleanWorkingTree }
  }

  Write-Host "AISP release check passed."
}
finally {
  Pop-Location
  if ($null -eq $oldPythonDontWriteBytecode) {
    Remove-Item Env:PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue
  } else {
    $env:PYTHONDONTWRITEBYTECODE = $oldPythonDontWriteBytecode
  }
}
