# Скрипт массового обновления ссылок после реструктуризации docs
$root = 'c:\Users\DELL\Desktop\golem-main'

# Точные пары: старый путь -> новый путь
$exact = @(
  'docs/03-CONTENT/AI-MODELS.md|docs/03-AI/AI-MODELS.md',
  'docs/03-CONTENT/GLOSSARY-DEVELOPMENT.md|docs/04-STANDARD/GLOSSARY-DEVELOPMENT.md',
  'docs/03-CONTENT/GRAPH.md|docs/01-ARCHITECTURE/GRAPH.md',
  'docs/03-CONTENT/IDEAS.md|docs/02-MANAGEMENT/IDEAS.md',
  'docs/03-CONTENT/ML-COURSE.md|docs/03-AI/ML-COURSE.md',
  'docs/03-CONTENT/PALEO-READING-METHODS.md|docs/06-METHODOLOGY/PALEO-READING-METHODS.md',
  'docs/03-CONTENT/PALEO-STANDARD.md|docs/04-STANDARD/PALEO-STANDARD.md',
  'docs/03-CONTENT/STATS.md|docs/02-MANAGEMENT/STATS.md',
  'docs/03-CONTENT/STRATEGY.md|docs/02-MANAGEMENT/STRATEGY.md',
  'docs/03-CONTENT/MANIFEST.md|docs/00-START/MANIFEST.md',
  'docs/09-GUIDES/AGENT.md|docs/03-AI/AGENT.md',
  'docs/09-GUIDES/AI-WORKFLOW.md|docs/03-AI/AI-WORKFLOW.md',
  'docs/09-GUIDES/ASSISTANT.md|docs/03-AI/ASSISTANT.md',
  'docs/09-GUIDES/CLINE.md|docs/03-AI/CLINE.md',
  'docs/09-GUIDES/NEURO.md|docs/03-AI/NEURO.md',
  'docs/09-GUIDES/HEBREW.md|docs/04-STANDARD/HEBREW.md',
  'docs/09-GUIDES/TERMINOLOGY.md|docs/04-STANDARD/TERMINOLOGY.md',
  'docs/09-GUIDES/PALEO-TRANSLATION-PRINCIPLES.md|docs/04-STANDARD/PALEO-TRANSLATION-PRINCIPLES.md',
  'docs/09-GUIDES/PALEO-TRANSLATION-PROTOCOL.md|docs/04-STANDARD/PALEO-TRANSLATION-PROTOCOL.md',
  'docs/09-GUIDES/DAVAR.md|docs/06-METHODOLOGY/DAVAR.md',
  'docs/09-GUIDES/EXPOSURE.md|docs/06-METHODOLOGY/EXPOSURE.md',
  'docs/09-GUIDES/STATE-DIAGNOSTICS.md|docs/06-METHODOLOGY/STATE-DIAGNOSTICS.md',
  'docs/09-GUIDES/AUDIT.md|docs/08-AUDITS/AUDIT.md',
  'docs/09-GUIDES/CHECKERS.md|docs/08-AUDITS/CHECKERS.md',
  'docs/09-GUIDES/ICONS.md|docs/10-DESIGN/ICONS.md',
  'docs/09-GUIDES/ANALYZERS.md|docs/11-PRODUCTS/ANALYZERS.md',
  'docs/09-GUIDES/RESEARCHLAB-ANALYZERS.md|docs/11-PRODUCTS/RESEARCHLAB-ANALYZERS.md',
  'docs/09-GUIDES/SETTINGS.md|docs/11-PRODUCTS/SETTINGS.md',
  'docs/10-INSTRUCTIONS/RESEARCH-LAB-MAP.md|docs/11-PRODUCTS/RESEARCH-LAB-MAP.md',
  'docs/10-INSTRUCTIONS/products/ED-AGENT.md|docs/11-PRODUCTS/AGENT.md',
  'docs/10-INSTRUCTIONS/products/ED-ASSISTANT.md|docs/11-PRODUCTS/ASSISTANT.md',
  'docs/10-INSTRUCTIONS/products/ED-DAVAR.md|docs/11-PRODUCTS/DAVAR.md',
  'docs/10-INSTRUCTIONS/products/ED-NEURO.md|docs/11-PRODUCTS/NEURO.md',
  'docs/ED-AGENT.md|docs/11-PRODUCTS/AGENT.md',
  'docs/ED-ASSISTANT.md|docs/11-PRODUCTS/ASSISTANT.md',
  'docs/ED-DAVAR.md|docs/11-PRODUCTS/DAVAR.md',
  'docs/ED-NEURO.md|docs/11-PRODUCTS/NEURO.md'
)

# Папочные правила (от частного к общему): имя файла сохраняется, регистр -> UPPER
$dirs = @(
  'docs/10-INSTRUCTIONS/agent/|docs/03-AI/',
  'docs/10-INSTRUCTIONS/assistant/|docs/03-AI/',
  'docs/10-INSTRUCTIONS/checkers/|docs/08-AUDITS/',
  'docs/10-INSTRUCTIONS/products/|docs/11-PRODUCTS/',
  'docs/10-INSTRUCTIONS/|docs/11-PRODUCTS/',
  'docs/12-JOB/|docs/02-MANAGEMENT/',
  'docs/08-EXPOSURE/|docs/06-METHODOLOGY/',
  'docs/13-METHODOLOGY/|docs/06-METHODOLOGY/',
  'docs/07-DICTIONARIES/|docs/05-DICTIONARIES/',
  'docs/16-MECHANICS/|docs/07-MECHANICS/',
  'docs/05-AUDITS/|docs/08-AUDITS/',
  'docs/06-DESIGN/|docs/10-DESIGN/',
  'docs/14-REPORTS/|docs/13-REPORTS/',
  'docs/15-TEMPLATES/|docs/12-TEMPLATES/',
  'docs/11-AGENTS/|docs/03-AI/',
  'docs/AGENTS/|docs/03-AI/'
)

$pairs = New-Object System.Collections.ArrayList
foreach ($r in ($exact + $dirs)) {
  $parts = $r.Split('|')
  [void]$pairs.Add(@($parts[0], $parts[1]))
}

# Папочные упоминания без имени файла: простой Replace
$dirPlain = @(
  @('docs/10-INSTRUCTIONS/agent', 'docs/03-AI'),
  @('docs/10-INSTRUCTIONS/assistant', 'docs/03-AI'),
  @('docs/10-INSTRUCTIONS/checkers', 'docs/08-AUDITS'),
  @('docs/10-INSTRUCTIONS/products', 'docs/11-PRODUCTS'),
  @('docs/10-INSTRUCTIONS', 'docs/11-PRODUCTS'),
  @('docs/12-JOB', 'docs/02-MANAGEMENT'),
  @('docs/08-EXPOSURE', 'docs/06-METHODOLOGY'),
  @('docs/13-METHODOLOGY', 'docs/06-METHODOLOGY'),
  @('docs/07-DICTIONARIES', 'docs/05-DICTIONARIES'),
  @('docs/16-MECHANICS', 'docs/07-MECHANICS'),
  @('docs/05-AUDITS', 'docs/08-AUDITS'),
  @('docs/06-DESIGN', 'docs/10-DESIGN'),
  @('docs/14-REPORTS', 'docs/13-REPORTS'),
  @('docs/15-TEMPLATES', 'docs/12-TEMPLATES'),
  @('docs/11-AGENTS', 'docs/03-AI'),
  @('docs/AGENTS', 'docs/03-AI')
)

function Rewrite([string]$text) {
  # обратные слэши в docs-путях -> прямые
  $text = [regex]::Replace($text, 'docs\\(\d{2}-[A-Za-z\-]+)\\', 'docs/$1/')
  foreach ($pair in $script:pairs) {
    $p = $pair[0]; $q = $pair[1]
    if ($p.EndsWith('/')) {
      $pattern = [regex]::Escape($p) + '([\w\-]+\.md)'
      $text = [regex]::Replace($text, $pattern, { param($m) $q + $m.Groups[1].Value.ToUpper() + '.md' })
    } else {
      $text = $text.Replace($p, $q)
    }
  }
  foreach ($pair in $script:dirPlain) {
    $text = $text.Replace($pair[0], $pair[1])
  }
  # легаси-пути без docs/
  $text = $text.Replace('methodology/MANIFEST.md', 'docs/00-START/MANIFEST.md')
  $text = [regex]::Replace($text, 'instructions/(exposure|methodology)/([\w\-]+)\.md', { param($m) 'docs/06-METHODOLOGY/' + $m.Groups[2].Value.ToUpper() + '.md' })
  $text = [regex]::Replace($text, 'instructions/templates/([\w\-]+)\.md', { param($m) 'docs/12-TEMPLATES/' + $m.Groups[1].Value.ToUpper() + '.md' })
  $text = [regex]::Replace($text, '(?<![\w/])methodology/([\w\-]+)\.md', { param($m) 'docs/06-METHODOLOGY/' + $m.Groups[1].Value.ToUpper() + '.md' })
  # нормализация регистра имён файлов в docs-путях (все файлы теперь UPPERCASE)
  $text = [regex]::Replace($text, '(docs/\d{2}-[A-Za-z\-]+)/([a-z][\w\-]*\.md)', { param($m) $m.Groups[1].Value + '/' + $m.Groups[2].Value.ToUpper() })
  return $text
}

$targets = @(Get-ChildItem $root -Recurse -File | Where-Object { $_.FullName -notmatch '\\\.git\\' -and $_.FullName -notmatch 'node_modules' -and ($_.Extension -eq '.md' -or $_.Extension -eq '.json') })
$clinerules = Join-Path $root '.clinerules'
if (Test-Path $clinerules) { $targets += (Get-Item $clinerules) }

$changed = 0
foreach ($f in $targets) {
  $c = [IO.File]::ReadAllText($f.FullName)
  $n = Rewrite $c
  if ($n -ne $c) { [IO.File]::WriteAllText($f.FullName, $n); $changed++ }
}
Write-Output "FILES CHANGED: $changed"
