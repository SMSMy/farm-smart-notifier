#!/usr/bin/env python3
"""
إضافة عدادات الصفحات الفردية لجميع صفحات HTML
"""

import os
import re
from pathlib import Path

def add_page_countdown_to_html(file_path):
    """إضافة سكريپت عداد الصفحة لملف HTML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # تخطي الصفحة الرئيسية
        if 'index.html' in str(file_path):
            print(f"تخطي {file_path} - الصفحة الرئيسية")
            return False

        # فحص إذا كان السكريپت موجود بالفعل
        if 'page-countdown.js' in content:
            print(f"تخطي {file_path} - عداد الصفحة موجود بالفعل")
            return False

        # فحص وجود card-countdown.js
        if 'card-countdown.js' not in content:
            print(f"تخطي {file_path} - لا يحتوي على العدادات الأساسية")
            return False

        # إضافة سكريپت عداد الصفحة
        pattern = r'(\s*<script src="card-countdown\.js" defer></script>\s*)'
        replacement = r'\1    <script src="page-countdown.js" defer></script>\n'

        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)

            # حفظ الملف المحدث
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"تم إضافة عداد الصفحة لـ {file_path}")
            return True
        else:
            print(f"لم يتم العثور على card-countdown.js في {file_path}")
            return False

    except Exception as e:
        print(f"خطأ في معالجة {file_path}: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("إضافة عدادات الصفحات الفردية لجميع صفحات HTML...")
    print("=" * 60)

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
        result = add_page_countdown_to_html(file_path)
        if result:
            updated_count += 1
        else:
            skipped_count += 1

    print("\n" + "=" * 60)
    print("تقرير نهائي:")
    print(f"   تم التحديث: {updated_count} ملف")
    print(f"   تم التخطي: {skipped_count} ملف")
    print(f"   إجمالي: {len(html_files)} ملف")

    if updated_count > 0:
        print(f"\nتم إضافة عدادات الصفحات لـ {updated_count} صفحة!")
        print("الآن كل صفحة فردية ستعرض عداد للمهمة الخاصة بها")

    print("\nانتهى!")

if __name__ == "__main__":
    main()

