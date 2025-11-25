#!/usr/bin/env python3
"""
تحديث جميع صفحات HTML لاستخدام النسخة الثابتة من العداد
"""

import os
import re
from pathlib import Path

def update_html_to_static(file_path):
    """تحديث ملف HTML لاستخدام العداد الثابت"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # استبدال countdown-timer.js بـ countdown-timer-static.js
        old_script = 'countdown-timer.js'
        new_script = 'countdown-timer-static.js'

        if old_script in content:
            content = content.replace(old_script, new_script)

            # حفظ الملف المحدث
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"تم تحديث {file_path}")
            return True
        else:
            print(f"تخطي {file_path} - لا يحتوي على العداد")
            return False

    except Exception as e:
        print(f"خطأ في معالجة {file_path}: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("تحديث جميع صفحات HTML للنسخة الثابتة...")
    print("=" * 50)

    # البحث عن ملفات HTML في مجلد docs
    docs_dir = 'docs'
    if not os.path.exists(docs_dir):
        print(f"مجلد {docs_dir} غير موجود!")
        return

    html_files = list(Path(docs_dir).rglob('*.html'))

    if not html_files:
        print("لم يتم العثور على ملفات HTML")
        return

    print(f"تم العثور على {len(html_files)} ملف HTML")

    updated_count = 0
    skipped_count = 0

    for file_path in html_files:
        result = update_html_to_static(file_path)
        if result:
            updated_count += 1
        else:
            skipped_count += 1

    print("\n" + "=" * 50)
    print("تقرير نهائي:")
    print(f"   تم التحديث: {updated_count} ملف")
    print(f"   تم التخطي: {skipped_count} ملف")
    print(f"   إجمالي: {len(html_files)} ملف")

    if updated_count > 0:
        print(f"\nتم تحديث {updated_count} صفحة للنسخة الثابتة!")
        print("الآن العداد سيعمل على GitHub Pages بدون خادم")

    print("\nانتهى!")

if __name__ == "__main__":
    main()

