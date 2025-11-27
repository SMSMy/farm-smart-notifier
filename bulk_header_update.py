import re

# Remaining files to update
files = [
    'bougainvillea.html', 'custard.html', 'fertilizer.html', 'henna.html',
    'jackfruit.html', 'mint.html', 'moringa.html', 'pomegranate.html'
]

for file in files:
    path = f'c:\\Code\\farm-notifier\\docs\\{file}'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace <header with <header class="header-with-image"
        updated = re.sub(
            r'(\s+)<header\s+',
            r'\1<header class="header-with-image" ',
            content,
            count=1
        )

        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f'✓ {file}')
    except Exception as e:
        print(f'✗ {file}: {e}')
