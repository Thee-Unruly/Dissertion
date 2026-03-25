import re

file_path = r'c:\Users\ibrahim.fadhili\OneDrive - Agile Business Solutions\Desktop\Dissertion\src\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace :root
old_root = r"""        :root \{
            --bg-deep: #05070a;
            --accent-glow: #00f2ff;
            --off-glow: #ffcc00;
            --eval-glow: #00ff99;
            --alert-red: #ff3366;
            --warn-gold: #ffcc00;
            --safe-green: #00ff99;
            --glass: rgba\(255, 255, 255, 0.05\);
            --glass-border: rgba\(255, 255, 255, 0.1\);
        \}"""

new_root = """        :root {
            --bg-deep: #f8fafc;
            --accent-glow: #3b82f6;
            --off-glow: #f97316;
            --eval-glow: #10b981;
            --alert-red: #ef4444;
            --warn-gold: #f59e0b;
            --safe-green: #10b981;
            --glass: rgba(255, 255, 255, 0.7);
            --glass-border: rgba(203, 213, 225, 0.5);
            --text-main: #0f172a;
            --text-muted: #64748b;
            --text-light: #94a3b8;
            --list-bg: rgba(0, 0, 0, 0.02);
            --list-hover: rgba(0, 0, 0, 0.04);
            --list-active: rgba(59, 130, 246, 0.08);
            --code-bg: rgba(0, 0, 0, 0.05);
            --shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        }"""
content = re.sub(old_root, new_root, content)

# Replace body styles
content = content.replace("color: #fff;", "color: var(--text-main);", 1)
content = content.replace("rgba(0, 242, 255, 0.05)", "rgba(59, 130, 246, 0.08)")
content = content.replace("rgba(255, 51, 102, 0.05)", "rgba(249, 115, 22, 0.08)")

# Replace header box-shadow
content = content.replace("box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);", "box-shadow: var(--shadow);")

# Replace h1 gradient
content = content.replace("background: linear-gradient(to right, var(--accent-glow), #fff);", "background: linear-gradient(to right, var(--accent-glow), var(--text-main));")

# Replace stat-label color
content = content.replace("color: #888;", "color: var(--text-muted);")

# Replace email-item background
content = content.replace("background: rgba(255, 255, 255, 0.02);", "background: var(--list-bg);")
content = content.replace("background: rgba(255, 255, 255, 0.05);", "background: var(--list-hover);")
content = content.replace("background: rgba(0, 242, 255, 0.05);", "background: var(--list-active);")

# Replace nav-tab styling
content = content.replace("color: #888;", "color: var(--text-muted);") # this will match multiple, we already did one above, but we can just use re.sub for all color: #888;
content = re.sub(r'color:\s*#888;?', 'color: var(--text-muted);', content)

content = content.replace("color: #fff;", "color: var(--text-main);") # this will replace any remaining #fff to text-main
content = content.replace("box-shadow: 0 0 15px rgba(0, 242, 255, 0.2);", "box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);")
content = content.replace("background: rgba(255, 255, 255, 0.08);", "background: rgba(0, 0, 0, 0.04);")

# Replace scrollbar styling
content = content.replace("rgba(255, 255, 255, 0.3)", "rgba(0, 0, 0, 0.2)")

# Replace hardcoded #ccc to text-muted or light
content = re.sub(r'color:\s*#ccc;?', 'color: var(--text-muted);', content)

# Replace code blocks background
content = re.sub(r'background:\s*rgba\(0,0,0,0.3\);?', 'background: var(--code-bg);', content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Theme updated!")
