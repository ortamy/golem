# Нормализация имён файлов в docs: ВЕРХНИЙ РЕГИСТР + .md
$docs = 'c:\Users\DELL\Desktop\golem-main\docs'
$n = 0
$badExt = @()
Get-ChildItem $docs -Recurse -File | ForEach-Object {
  if ($_.Extension -ne '.md') { $badExt += $_.FullName }
  $newName = $_.BaseName.ToUpper() + '.md'
  if ($_.Name -cne $newName) {
    Rename-Item -Path $_.FullName -NewName $newName
    Write-Output "$($_.Name) -> $newName"
    $n++
  }
}
Write-Output "RENAMED: $n"
if ($badExt.Count -gt 0) { $badExt | ForEach-Object { Write-Output "NOT-MD: $_" } }
Write-Output "TOTAL FILES: $((Get-ChildItem $docs -Recurse -File).Count)"
$left = @(Get-ChildItem $docs -Recurse -File | Where-Object { $_.Name -cne ($_.BaseName.ToUpper() + '.md') })
if ($left.Count -eq 0) { Write-Output 'OK: ALL UPPERCASE .MD' } else { Write-Output "PROBLEM: $($left.Count)" }
