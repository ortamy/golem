# Полная очистка docs после возврата старой структуры из GitHub
$res = New-Object System.Collections.ArrayList
$enc = New-Object System.Text.UTF8Encoding($false)
$docs = 'c:\Users\DELL\Desktop\golem-main\docs'

# --- 1. Разрешение конфликтов: оставить HEAD-блоки ---
$cf = @(gci $docs -r -File | Select-String -Pattern '^<{7} ' -List | % Path)
[void]$res.Add("CONFLICT FILES: $($cf.Count)")
foreach ($f in $cf) {
  $lines = [IO.File]::ReadAllLines($f, $enc)
  $out = New-Object System.Collections.Generic.List[string]
  $state = 0
  foreach ($line in $lines) {
    if ($state -eq 0 -and $line -match '^<{7}') { $state = 1; continue }
    if ($state -eq 1 -and $line -match '^={7}\s*$') { $state = 2; continue }
    if ($state -eq 2 -and $line -match '^>{7}') { $state = 0; continue }
    if ($state -ne 2) { $out.Add($line) }
  }
  [IO.File]::WriteAllLines($f, $out.ToArray(), $enc)
  [void]$res.Add("RESOLVED: " + (Split-Path $f -Leaf))
}

# --- 2. Уникальные имена в старых папках (что не попадало в миграцию) ---
$oldDirs = @('03-CONTENT','05-AUDITS','06-DESIGN','07-DICTIONARIES','08-EXPOSURE','10-INSTRUCTIONS','11-AGENTS','12-JOB','13-METHODOLOGY','14-REPORTS','15-TEMPLATES','16-MECHANICS')
$newNames = @{}
gci $docs -r -File | Where-Object { $p = $_.Directory.Name; $oldDirs -notcontains $p } | ForEach-Object { $newNames[$_.BaseName.ToUpper()] = 1 }
if (Test-Path "$docs\INDEX.md") { $newNames['INDEX'] = 1 }
$unique = @()
foreach ($d in $oldDirs) {
  $dp = Join-Path $docs $d
  if (-not (Test-Path $dp)) { continue }
  gci $dp -r -File | ForEach-Object {
    if (-not $newNames.ContainsKey($_.BaseName.ToUpper())) { $unique += $_.FullName }
  }
}
[void]$res.Add("UNIQUE IN OLD DIRS: $($unique.Count)")
$unique | % { [void]$res.Add("UNIQUE: $_") }

# --- 3. Удаление старых папок-дубликатов ---
foreach ($d in $oldDirs) {
  $dp = Join-Path $docs $d
  if (Test-Path $dp) { Remove-Item $dp -Recurse -Force; [void]$res.Add("DELETED DIR: $d") }
}

# --- 4. Дубли в 09-GUIDES: имя уже есть в другой папке docs -> удалить ---
$alias = @{ 'WRITTING' = 'WRITING' }
$guides = Join-Path $docs '09-GUIDES'
if (Test-Path $guides) {
  gci $guides -File | ForEach-Object {
    $b = $_.BaseName.ToUpper()
    if ($alias.ContainsKey($b)) { $b = $alias[$b] }
    $found = gci $docs -r -File | Where-Object { $_.Directory.Name -ne '09-GUIDES' -and $_.BaseName.ToUpper() -eq $b }
    if ($found) { Remove-Item $_.FullName -Force; [void]$res.Add("DUP REMOVED: 09-GUIDES/$($_.Name)") }
  }
}

# --- 5. Восстановление RELIGIONISM-THEORY из git ---
$r = "$docs\06-METHODOLOGY\RELIGIONISM-THEORY.md"
if (-not (Test-Path $r)) {
  cmd /c "git checkout -- `"docs/06-METHODOLOGY/RELIGIONISM-THEORY.md`" 2>&1" | Out-Null
  [void]$res.Add("RESTORED FROM GIT: RELIGIONISM-THEORY=$(Test-Path $r)")
}

# --- 6. Нормализация регистра ---
$n = 0
gci $docs -r -File | ForEach-Object {
  $newName = $_.BaseName.ToUpper() + '.md'
  if ($_.Name -cne $newName) { Rename-Item $_.FullName -NewName $newName; $n++ }
}
[void]$res.Add("RENAMED TO UPPER: $n")

# --- 7. Итог ---
$total = (gci $docs -r -File).Count
$badLeft = @(gci $docs -r -File | Where-Object { $_.Name -cne ($_.BaseName.ToUpper() + '.md') }).Count
$marks = @(gci $docs -r -File | Select-String -Pattern '^<{7} ' -List).Count
[void]$res.Add("TOTAL FILES: $total")
[void]$res.Add("BAD NAMES LEFT: $badLeft")
[void]$res.Add("CONFLICT MARKS LEFT: $marks")
$res | Out-File 'c:\Users\DELL\Desktop\golem-main\tools\fix-report.txt' -Encoding utf8
