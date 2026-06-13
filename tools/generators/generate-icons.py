import os

icons = {}

icons['scroll'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="4" y="6" width="4" height="20" rx="2"/>
    <rect x="24" y="6" width="4" height="20" rx="2"/>
    <path d="M8 6 L24 6 L24 26 L8 26 Z"/>
    <line x1="12" y1="12" x2="20" y2="12"/>
    <line x1="12" y1="16" x2="20" y2="16"/>
    <line x1="12" y1="20" x2="20" y2="20"/>
  </g>
</svg>'''

icons['tablets'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="4" width="10" height="24" rx="2"/>
    <rect x="19" y="4" width="10" height="24" rx="2"/>
    <line x1="6" y1="10" x2="10" y2="10"/>
    <line x1="6" y1="14" x2="10" y2="14"/>
    <line x1="6" y1="18" x2="10" y2="18"/>
    <line x1="6" y1="22" x2="10" y2="22"/>
    <line x1="22" y1="10" x2="26" y2="10"/>
    <line x1="22" y1="14" x2="26" y2="14"/>
    <line x1="22" y1="18" x2="26" y2="18"/>
    <line x1="22" y1="22" x2="26" y2="22"/>
  </g>
</svg>'''

icons['fish'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <ellipse cx="16" cy="16" rx="10" ry="5"/>
    <path d="M26 16 L30 10 L30 22 Z"/>
    <circle cx="10" cy="15" r="1.5"/>
    <path d="M6 16 L4 16"/>
  </g>
</svg>'''

icons['lamp'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M10 20 L8 26 L24 26 L22 20 Z"/>
    <rect x="10" y="26" width="12" height="3" rx="1"/>
    <path d="M16 20 L16 12"/>
    <path d="M16 12 Q13 9 16 4 Q19 9 16 12"/>
  </g>
</svg>'''

icons['tree'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="16" y1="22" x2="16" y2="30"/>
    <path d="M16 30 Q12 30 10 28"/>
    <path d="M16 30 Q20 30 22 28"/>
    <path d="M16 30 L16 32"/>
    <path d="M16 22 Q8 16 12 8 Q16 2 20 8 Q24 16 16 22"/>
    <circle cx="12" cy="12" r="2" fill="currentColor"/>
    <circle cx="20" cy="10" r="2" fill="currentColor"/>
    <circle cx="16" cy="6" r="2" fill="currentColor"/>
  </g>
</svg>'''

icons['aleph'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M16 4 L6 28"/>
    <path d="M16 4 L26 28"/>
    <line x1="10" y1="18" x2="22" y2="18"/>
    <path d="M26 28 L22 28"/>
  </g>
</svg>'''

icons['temple'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="6" y="6" width="4" height="24"/>
    <rect x="22" y="6" width="4" height="24"/>
    <line x1="4" y1="30" x2="28" y2="30"/>
    <rect x="6" y="4" width="20" height="4" rx="1"/>
    <path d="M8 4 L16 1 L24 4"/>
  </g>
</svg>'''

icons['fire'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M8 28 Q6 20 10 14 Q10 8 8 4 Q12 10 12 16 Q12 24 8 28"/>
    <path d="M16 28 Q14 18 16 10 Q16 4 16 2 Q18 8 18 16 Q18 24 16 28"/>
    <path d="M24 28 Q22 20 24 14 Q24 8 22 4 Q26 10 26 16 Q26 24 24 28"/>
  </g>
</svg>'''

icons['sword'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M16 2 L16 22"/>
    <path d="M16 2 L10 8 L16 12"/>
    <path d="M16 2 L22 8 L16 12"/>
    <line x1="6" y1="20" x2="26" y2="20"/>
    <rect x="14" y="22" width="4" height="6" rx="1"/>
    <circle cx="16" cy="30" r="2"/>
  </g>
</svg>'''

icons['fruit'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M18 6 Q22 4 26 6 Q22 8 18 6"/>
    <line x1="18" y1="6" x2="16" y2="10"/>
    <circle cx="16" cy="18" r="8"/>
    <path d="M13 12 L14 10 L16 12 L18 10 L19 12"/>
  </g>
</svg>'''

icons['roots'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="2" y1="12" x2="30" y2="12"/>
    <path d="M8 12 Q8 22 4 28"/>
    <path d="M8 12 L8 12"/>
    <path d="M16 12 Q16 20 16 30"/>
    <path d="M12 18 Q10 20 10 22"/>
    <path d="M20 18 Q22 20 22 22"/>
    <path d="M24 12 Q24 22 28 28"/>
    <line x1="16" y1="4" x2="16" y2="12"/>
    <path d="M16 4 Q12 2 10 4"/>
    <path d="M16 4 Q20 2 22 4"/>
  </g>
</svg>'''

icons['book'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M16 4 L16 28"/>
    <path d="M4 6 L16 4 L16 28 L4 26 Z"/>
    <path d="M16 4 L28 6 L28 26 L16 28 Z"/>
    <line x1="16" y1="4" x2="16" y2="28"/>
    <line x1="7" y1="10" x2="13" y2="9.5"/>
    <line x1="7" y1="14" x2="13" y2="13.5"/>
    <line x1="7" y1="18" x2="13" y2="17.5"/>
    <line x1="19" y1="9.5" x2="25" y2="10"/>
    <line x1="19" y1="13.5" x2="25" y2="14"/>
    <line x1="19" y1="17.5" x2="25" y2="18"/>
  </g>
</svg>'''

icons['person'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="16" cy="5" r="4"/>
    <path d="M16 9 L16 20"/>
    <path d="M16 12 L6 10"/>
    <path d="M16 12 L26 10"/>
    <path d="M16 20 L8 30"/>
    <path d="M16 20 L24 30"/>
  </g>
</svg>'''

icons['event'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M18 2 L10 16 L16 16 L14 30 L24 14 L18 14 Z"/>
  </g>
</svg>'''

icons['practice'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="8" y="4" width="16" height="8" rx="2"/>
    <line x1="16" y1="12" x2="16" y2="28"/>
    <path d="M12 28 Q8 26 8 22 L12 22 L12 26 L14 26 L14 22 L18 22 L18 26 L20 26 L20 22 L24 22 Q24 26 20 28 Z"/>
  </g>
</svg>'''

icons['shield'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 6 L26 6 L26 16 Q26 26 16 30 Q6 26 6 16 Z"/>
    <path d="M10 10 L22 10 L22 16 Q22 23 16 26 Q10 23 10 16 Z"/>
    <line x1="10" y1="16" x2="22" y2="16"/>
    <line x1="16" y1="10" x2="16" y2="22"/>
  </g>
</svg>'''

icons['question'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="16" cy="16" r="12"/>
    <path d="M12 12 Q12 8 16 8 Q20 8 20 12 Q20 16 16 18 L16 22"/>
    <circle cx="16" cy="26" r="1.5" fill="currentColor"/>
  </g>
</svg>'''

icons['summary'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 4 L20 4 L26 10 L26 28 L6 28 Z"/>
    <path d="M20 4 L20 10 L26 10"/>
    <path d="M11 18 L15 22 L21 14"/>
    <line x1="10" y1="12" x2="18" y2="12"/>
  </g>
</svg>'''

icons['search'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="13" cy="13" r="9"/>
    <line x1="20" y1="20" x2="28" y2="28"/>
  </g>
</svg>'''

icons['bookmark'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M16 2 L19.5 11.5 L30 12 L22 19 L24 30 L16 24 L8 30 L10 19 L2 12 L12.5 11.5 Z"/>
  </g>
</svg>'''

icons['menu'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="4" y1="8" x2="28" y2="8"/>
    <line x1="4" y1="16" x2="28" y2="16"/>
    <line x1="4" y1="24" x2="28" y2="24"/>
  </g>
</svg>'''

icons['theme'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="16" cy="16" r="5"/>
    <line x1="16" y1="2" x2="16" y2="6"/>
    <line x1="16" y1="26" x2="16" y2="30"/>
    <line x1="2" y1="16" x2="6" y2="16"/>
    <line x1="26" y1="16" x2="30" y2="16"/>
    <line x1="6.5" y1="6.5" x2="9.5" y2="9.5"/>
    <line x1="22.5" y1="22.5" x2="25.5" y2="25.5"/>
    <line x1="6.5" y1="25.5" x2="9.5" y2="22.5"/>
    <line x1="22.5" y1="9.5" x2="25.5" y2="6.5"/>
  </g>
</svg>'''

icons['copy'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M10 6 L22 6 L28 12 L28 28 L10 28 Z"/>
    <path d="M22 6 L22 12 L28 12"/>
    <path d="M4 4 L18 4 L24 10 L24 26 L4 26 Z"/>
    <path d="M18 4 L18 10 L24 10"/>
  </g>
</svg>'''

icons['print'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="4" y="12" width="24" height="12" rx="2"/>
    <rect x="8" y="24" width="16" height="4" rx="1"/>
    <path d="M8 12 L8 6 L20 6 L24 10 L24 12"/>
    <line x1="12" y1="18" x2="20" y2="18"/>
    <line x1="12" y1="22" x2="18" y2="22"/>
  </g>
</svg>'''

icons['random'] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g fill="none" stroke="#d4a843" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="2" y="2" width="13" height="13" rx="2"/>
    <circle cx="5.5" cy="5.5" r="1.5" fill="currentColor"/>
    <circle cx="11.5" cy="5.5" r="1.5" fill="currentColor"/>
    <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
    <circle cx="5.5" cy="11.5" r="1.5" fill="currentColor"/>
    <circle cx="11.5" cy="11.5" r="1.5" fill="currentColor"/>
    <rect x="17" y="17" width="13" height="13" rx="2"/>
    <circle cx="23.5" cy="23.5" r="1.5" fill="currentColor"/>
    <circle cx="23.5" cy="20.5" r="1.5" fill="currentColor"/>
    <circle cx="23.5" cy="26.5" r="1.5" fill="currentColor"/>
  </g>
</svg>'''

base_path = 'web/icons/32'
os.makedirs(base_path, exist_ok=True)

for name, content in sorted(icons.items()):
    filepath = os.path.join(base_path, name + '.svg')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {name}.svg')

print(f'\nAll {len(icons)} icons created successfully!')