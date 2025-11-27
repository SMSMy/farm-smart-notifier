# Script لتطبيق الألوان على جميع الصفحات
import os
import re

docs_dir = r"c:\Code\farm-notifier\docs"

# تصنيف الصفحات حسب الفئة
poultry_pages = [
    'deworming.html', 'vitamins.html', 'sanitization.html', 'coccidiosis.html',
    'weekly_cleaning.html', 'soil_turning.html', 'ventilation.html',
    'feeder_cleaning.html', 'water_station.html', 'pipe_waterer.html', 'quarantine.html'
]

tree_pages = [
    'henna.html', 'fig.html', 'banana.html', 'mango.html', 'pomegranate.html',
    'grape.html', 'jackfruit.html', 'acacia.html', 'bougainvillea.html',
    'mint.html', 'moringa.html', 'custard.html', 'fertilizers.html', 'fertilizer.html'
]

def add_category_class(filepath, category_class):
    """إضافة class للفئة في subtitle"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # إضافة الكلاس إلى subtitle
        updated = re.sub(
            r'<p class="subtitle"([^>]*)>',
            f'<p class="subtitle {category_class}"\\1>',
            content
        )

        # إذا كانت subtitle لديها classes أخرى بالفعل
        updated = re.sub(
            r'<p class="subtitle ((?!poultry-page|tree-page)[^"]*)"',
            f'<p class="subtitle \\1 {category_class}"',
            updated
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated)

        return True
    except Exception as e:
        print(f"Error in {filepath}: {e}")
        return False

# تطبيق على صفحات الدواجن
poultry_count = 0
for page in poultry_pages:
    filepath = os.path.join(docs_dir, page)
    if os.path.exists(filepath):
        if add_category_class(filepath, 'poultry-page'):
            poultry_count += 1
            print(f"✓ Poultry: {page}")

# تطبيق على صفحات الأشجار
tree_count = 0
for page in tree_pages:
    filepath = os.path.join(docs_dir, page)
    if os.path.exists(filepath):
        if add_category_class(filepath, 'tree-page'):
            tree_count += 1
            print(f"✓ Tree: {page}")

print(f"\n✨ تم التحديث: {poultry_count} صفحة دواجن، {tree_count} صفحة أشجار")
