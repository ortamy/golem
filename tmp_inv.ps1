[Console]::OutputEncoding=[Text.Encoding]::UTF8
$b='c:\Users\DELL\Desktop\golem-main\products\website\apps\researchlab\js'
'=== h1 locations ==='
foreach($m in @('timeline','paleo-linguistics','language-map','load-researches','scripture-reader','methodology','states')) {
  $p="$b\$m.js"
  if(Test-Path $p){
    '--- '+$m+'.js ---'
    $matches = Select-String -Path $p -Pattern '<h1' -Encoding UTF8
    foreach($m2 in $matches){ 'L'+$m2.LineNumber+': '+$m2.Line.Trim() }
    'LabHero refs = '+($matches2 = Select-String -Path $p -Pattern 'LabHero\.setView' -Encoding UTF8).Count
  }
}