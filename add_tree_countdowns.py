import os
import re

DOCS_DIR = 'docs'
COUNTDOWN_CODE = """
      <!-- Countdown Timer Container -->
      <div id="countdown-container"></div>"""

SCRIPTS_CODE = """    <script src="countdown-timer-static.js" defer></script>
    <script src="card-countdown.js" defer></script>
    <script src="page-countdown.js" defer></script>
  </head>"""

def add_countdown_to_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already added
    if 'countdown-container' in content:
        print(f"Skipping {filepath} (already has countdown)")
        return

    # Add scripts before </head>
    if '</head>' in content:
        content = content.replace('</head>', SCRIPTS_CODE)

    # Add container after header
    header_pattern = re.compile(r'(</header>)', re.IGNORECASE)
    if header_pattern.search(content):
        content = header_pattern.sub(r'\1' + COUNTDOWN_CODE, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

def main():
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith('.html') and filename not in ['index.html', 'fertilizers.html']:
            filepath = os.path.join(DOCS_DIR, filename)
            add_countdown_to_file(filepath)

if __name__ == "__main__":
    main()
