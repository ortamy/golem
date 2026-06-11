# tools/update-paths.ps1 — обновление путей после переноса в utils/

Write-Host "📝 Обновление sys.path в utils/"
python tools/utils/code-injector.py -f tools/utils/rename-script.py --replace "sys.path.insert(0, str(Path(__file__).parent))" --code "sys.path.insert(0, str(Path(__file__).parent.parent))"
python tools/utils/code-injector.py -f tools/utils/code-injector.py --replace "sys.path.insert(0, str(Path(__file__).parent))" --code "sys.path.insert(0, str(Path(__file__).parent.parent))"
python tools/utils/code-injector.py -f tools/utils/search.py --replace "sys.path.insert(0, str(Path(__file__).parent))" --code "sys.path.insert(0, str(Path(__file__).parent.parent))"

Write-Host "📝 Обновление golem.py"
python tools/utils/code-injector.py -f tools/golem.py --replace '"rename_script": "tools/rename-script.py"' --code '"rename_script": "tools/utils/rename-script.py"'
python tools/utils/code-injector.py -f tools/golem.py --replace '"code_injector": "tools/code-injector.py"' --code '"code_injector": "tools/utils/code-injector.py"'
python tools/utils/code-injector.py -f tools/golem.py --after-pattern '"auto_clear_cache"' --code '    "search": "tools/utils/search.py",'

Write-Host "📝 Обновление ed-agent/tools.py"
python tools/utils/code-injector.py -f ed-agent/tools.py --replace '"path": "tools/rename-script.py"' --code '"path": "tools/utils/rename-script.py"'
python tools/utils/code-injector.py -f ed-agent/tools.py --replace '"path": "tools/code-injector.py"' --code '"path": "tools/utils/code-injector.py"'
python tools/utils/code-injector.py -f ed-agent/tools.py --replace '"path": "tools/search.py"' --code '"path": "tools/utils/search.py"'

Write-Host "✅ Готово"