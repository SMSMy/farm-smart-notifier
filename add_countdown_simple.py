#!/usr/bin/env python3
"""
سكريپت لإضافة العداد الزمني لجميع صفحات HTML
"""

import os
import re
from pathlib import Path

def add_countdown_to_html_file(file_path):
    """إضافة العداد لملف HTML واحد"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # فحص إذا كان العداد موجود بالفعل
        if 'countdown-timer.js' in content:
            print(f"تخطي {file_path} - العداد موجود بالفعل")
            return False

        # إضافة سكريپت العداد في head
        head_pattern = r'(\s*<link rel="stylesheet" href="styles\.css" />\s*)'
        head_replacement = r'\1    <script src="countdown-timer.js" defer></script>\n'

        if re.search(head_pattern, content):
            content = re.sub(head_pattern, head_replacement, content)
            print(f"تم إضافة سكريپت العداد في head لـ {file_path}")
        else:
            print(f"لم يتم العثور على styles.css في {file_path}")
            return False

        # إضافة حاوية العداد بعد header
        header_pattern = r'(\s*</header>\s*)'
        header_replacement = r'\1\n      <!-- Countdown Timer Container -->\n      <div id="countdown-container"></div>\n'

        if re.search(header_pattern, content):
            content = re.sub(header_pattern, header_replacement, content)
            print(f"تم إضافة حاوية العداد بعد header لـ {file_path}")
        else:
            print(f"لم يتم العثور على </header> في {file_path}")
            return False

        # حفظ الملف المحدث
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"تم حفظ التحديثات في {file_path}")
        return True

    except Exception as e:
        print(f"خطأ في معالجة {file_path}: {e}")
        return False

def find_html_files(directory):
    """البحث عن جميع ملفات HTML"""
    html_files = []

    for file_path in Path(directory).rglob('*.html'):
        # تجاهل ملفات معينة
        if file_path.name in ['index.html']:  # index.html تم تحديثه بالفعل
            continue

        html_files.append(file_path)

    return html_files

def main():
    """الدالة الرئيسية"""
    print("بدء إضافة العداد الزمني لجميع صفحات HTML...")
    print("=" * 60)

    # البحث عن ملفات HTML في مجلد docs
    docs_dir = 'docs'
    if not os.path.exists(docs_dir):
        print(f"مجلد {docs_dir} غير موجود!")
        return

    html_files = find_html_files(docs_dir)

    if not html_files:
        print("لم يتم العثور على ملفات HTML للتحديث")
        return

    print(f"تم العثور على {len(html_files)} ملف HTML:")
    for file_path in html_files:
        print(f"   - {file_path}")

    print("\nبدء التحديث...")
    print("-" * 40)

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in html_files:
        print(f"\nمعالجة: {file_path}")

        result = add_countdown_to_html_file(file_path)

        if result:
            updated_count += 1
        elif result is False:
            error_count += 1
        else:
            skipped_count += 1

    # تقرير نهائي
    print("\n" + "=" * 60)
    print("تقرير نهائي:")
    print(f"   تم التحديث: {updated_count} ملف")
    print(f"   تم التخطي: {skipped_count} ملف")
    print(f"   أخطاء: {error_count} ملف")
    print(f"   إجمالي: {len(html_files)} ملف")

    if updated_count > 0:
        print(f"\nتم إضافة العداد الزمني بنجاح لـ {updated_count} صفحة!")
        print("لتشغيل العداد:")
        print("   1. python start_server.py")
        print("   2. افتح أي صفحة HTML في المتصفح")

    print("\nانتهى!")

if __name__ == "__main__":
    main()

