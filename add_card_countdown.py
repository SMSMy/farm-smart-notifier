#!/usr/bin/env python3
"""
إضافة عدادات البطاقات لجميع صفحات HTML
"""

import os
import re
from pathlib import Path

def add_card_countdown_to_html(file_path):
    """إضافة سكريپت عدادات البطاقات لملف HTML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # فحص إذا كان السكريپت موجود بالفعل
        if 'card-countdown.js' in content:
            print(f"تخطي {file_path} - عدادات البطاقات موجودة بالفعل")
            return False

        # فحص وجود countdown-timer-static.js
        if 'countdown-timer-static.js' not in content:
            print(f"تخطي {file_path} - لا يحتوي على العداد الأساسي")
            return False

        # إضافة سكريپت عدادات البطاقات
        pattern = r'(\s*<script src="countdown-timer-static\.js" defer></script>\s*)'
        replacement = r'\1    <script src="card-countdown.js" defer></script>\n'

        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)

            # حفظ الملف المحدث
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"تم إضافة عدادات البطاقات لـ {file_path}")
            return True
        else:
            print(f"لم يتم العثور على countdown-timer-static.js في {file_path}")
            return False

    except Exception as e:
        print(f"خطأ في معالجة {file_path}: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("إضافة عدادات البطاقات لجميع صفحات HTML...")
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
        result = add_card_countdown_to_html(file_path)
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
        print(f"\nتم إضافة عدادات البطاقات لـ {updated_count} صفحة!")
        print("الآن كل بطاقة ستعرض الوقت المتبقي لإشعارها")

    print("\nانتهى!")

if __name__ == "__main__":
    main()

