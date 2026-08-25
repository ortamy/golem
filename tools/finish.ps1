# Финализация: DEREKH-ABBA из git, проверки, коммит
$res = New-Object System.Collections.ArrayList
$enc = New-Object System.Text.UTF8Encoding($false)
$root = 'c:\Users\DELL\Desktop\golem-main'

# --- DEREKH-ABBA из git-истории ---
cmd /c "git checkout HEAD -- docs/03-CONTENT/DEREKH-ABBA.md" 2>&1 | Out-Null
$src = "$root\docs\03-CONTENT\DEREKH-ABBA.md"
if (Test-Path $src) {
  $head = ([IO.File]::ReadAllLines($src, $enc) | Select-Object -First 2) -join ' '
  Move-Item $src "$root\docs\04-STANDARD\DEREKH-ABBA.md" -Force
  Remove-Item "$root\docs\03-CONTENT" -Recurse -Force -ErrorAction SilentlyContinue
  [void]$res.Add("DEREKH-ABBA -> 04-STANDARD | $head")
} else {
  [void]$res.Add('DEREKH-ABBA: not found in git')
}

# --- Проверка конфликтных файлов ---
$i1 = ([IO.File]::ReadAllLines("$root\docs\INDEX.md", $enc))[0]
$m1 = ([IO.File]::ReadAllLines("$root\docs\00-START\MANIFEST.md", $enc))[0]
[void]$res.Add("INDEX L1: $i1")
[void]$res.Add("MANIFEST L1: $m1")

# --- Коммит ---
cmd /c "git add -A" 2>&1 | Out-Null
$out = cmd /c "git -c user.name=golem -c user.email=golem@local commit -m `"docs: finalize restructure - resolve conflicts, remove legacy dirs, normalize names`" 2>&1"
[void]$res.Add("COMMIT OUT: $($out -join ' ')")
$log = cmd /c "git log --oneline -2"
[void]$res.Add("LOG: $($log -join ' >> ')")
[void]$res.Add("TOTAL: $((gci \"$root\docs\" -r -File).Count)")
$res | Out-File "$root\tools\fix-report.txt" -Encoding utf8
