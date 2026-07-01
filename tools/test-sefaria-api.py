#!/usr/bin/env python3
"""Test Sefaria API response structure."""
import urllib.request
import json

url = "https://www.sefaria.org/api/v3/texts/Genesis%201"
req = urllib.request.Request(url, headers={"User-Agent": "Golem/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode("utf-8"))

print("Keys:", list(data.keys()))
print("\n'text' type:", type(data.get("text")))
print("'text' len:", len(data.get("text", [])))
print("\n'he' type:", type(data.get("he")))
print("'he' len:", len(data.get("he", "")))
print("\nFirst 3 items of 'text':", data.get("text", [None, None, None])[:3])
print("\nFirst 200 chars of 'he':", data.get("he", "")[:200])