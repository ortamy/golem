param()
Set-StrictMode -Off
[Console]::OutputEncoding = [Text.Encoding]::UTF8

function FixH1ToDiv([string]$file, [string]$beforeRegex, [string]$after) {
  $txt = Get-Content $file -Encoding UTF8
  if ($txt -match $beforeRegex) {
    $txt = $txt -replace $beforeRegex, $after
    Set-Content -Path $file -Value ($txt -join "`n") -Encoding UTF8
    Write-Host "$([System.IO.Path]::GetFileName($file)): OK"
  } else { Write-Host "$([System.IO.Path]::GetFileName($file)): PATTERN NOT FOUND" }
}

function InsertAfter([string]$file, [string]$anchorRegex, [string]$insert) {
  $txt = Get-Content $file -Encoding UTF8
  if ($txt -match $anchorRegex) {
    $txt = $txt -replace $anchorRegex, "`$0`n$insert"
    Set-Content -Path $file -Value ($txt -join "`n") -Encoding UTF8
    Write-Host "$([System.IO.Path]::GetFileName($file)): insertion OK"
  } else { Write-Host "$([System.IO.Path]::GetFileName($file)): anchor NOT FOUND" }
}

$b = 'c:\Users\DELL\Desktop\golem-main\products\website\apps\researchlab\js'

# paleo-linguistics.js: h1 -> div in renderLangPage
$f = "$b\paleo-linguistics.js"
$before = [regex]::Escape("'<h1><img src=`"../../assets/icons/32/scribe/scroll.png`" class=`"lab-icon`" alt=`">`" + escapeHtml(lang.name) + '</h1>' +")
$after  = "'<div class=`"pl-lang-title-wrap`"><img src=`"../../assets/icons/32/scribe/scroll.png`" class=`"lab-icon`" alt=`">`" + escapeHtml(lang.name) + '</div>' +"
FixH1ToDiv $f $before $after

# paleo-linguistics.js: insert setView in showLanguage
InsertAfter $f 'container\.innerHTML = renderLangPage\(lang\);' @"
      // Шапка модуля подменяется на язык
      if (window.LabHero && window.LabHero.setView) {
        window.LabHero.setView('paleo-linguistics', 'detail', {
          kicker: 'ГОЛЕМ · ПАЛЕО-ЛИНГВИСТИКА',
          title: lang.name,
          subtitle: lang.role || '',
          icon: 'scribe/scroll.png'
        });
      }
"@

# language-map.js: h1 -> div in renderDetail
$f2 = "$b\language-map.js"
$before2 = [regex]::Escape("'<h1 id=`"language-map-detail-title`">' + escapeHtml(language.name) + '</h1>' +")
$after2  = "'<div id=`"language-map-detail-title`">' + escapeHtml(language.name) + '</div>' +"
FixH1ToDiv $f2 $before2 $after2

# language-map.js: insert setView in renderDetail
InsertAfter $f2 'container\.innerHTML = .+language-map-detail' @"
      if (window.LabHero && window.LabHero.setView) {
        window.LabHero.setView('language-map', 'detail', {
          kicker: 'ГОЛЕМ · КАРТА ЯЗЫКОВ',
          title: language.name,
          subtitle: language.type || '',
          icon: 'paleo/track.png'
        });
      }
"@