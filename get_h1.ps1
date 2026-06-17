$files = Get-ChildItem -Recurse -Filter *.md content/tzel/ruach/ | Where-Object { $_.Name -ne README.md }  
