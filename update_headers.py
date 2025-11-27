import os
import re

# Directory containing HTML files
docs_dir = r"c:\Code\farm-notifier\docs"

# Skip index.html (already has the correct header)
skip_files = ["index.html", "جدول_الاسمدة_الشاملة.csv.html"]

# Get all HTML files
html_files = [f for f in os.listdir(docs_dir) if f.endswith('.html') and f not in skip_files]

print(f"Found {len(html_files)} HTML files to update")

for filename in html_files:
    filepath = os.path.join(docs_dir, filename)

    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace <header with <header class="header-with-image"
        # Using regex to find the header tag (may have attributes or not)
        updated_content = re.sub(
            r'<header(\s+[^>]*)?>',
            r'<header class="header-with-image"\1>',
            content,
            count=1
        )

        # Only write if there was a change
        if updated_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✓ Updated: {filename}")
        else:
            print(f"⊘ No change needed: {filename}")

    except Exception as e:
        print(f"✗ Error with {filename}: {e}")

print("\nAll files processed!")
