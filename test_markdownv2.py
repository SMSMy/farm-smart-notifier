#!/usr/bin/env python3
"""
اختبار تنسيق رسائل MarkdownV2
اختبار بسيط للتحقق من escape الأحرف الخاصة والروابط
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_messages_templates, escape_markdown_v2

def test_escape_function():
    """اختبار دالة escape"""
    print("=== اختبار دالة escape_markdown_v2 ===\n")

    test_cases = [
        ("Hello World", "Hello World"),
        ("Test (with) brackets", r"Test \(with\) brackets"),
        ("Test-with-dashes", r"Test\-with\-dashes"),
        ("Price: $10.99", r"Price: \$10\.99"),
    ]

    for input_text, expected in test_cases:
        result = escape_markdown_v2(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: '{input_text}'")
        print(f"   Expected: '{expected}'")
        print(f"   Got:      '{result}'")
        print()

def test_message_templates():
    """اختبار قوالب الرسائل"""
    print("\n=== اختبار قوالب الرسائل ===\n")

    templates = get_messages_templates()

    # اختبار رسالة تطهير الحظيرة
    print("1️⃣ إشعار تطهير الحظيرة (Sanitization):")
    print("-" * 60)
    sanitization_ar = templates['sanitization']['ar']({})
    print(sanitization_ar)
    print()

    # اختبار رسالة دواء الديدان
    print("2️⃣ إشعار دواء الديدان (Deworming):")
    print("-" * 60)
    deworming_ar = templates['deworming']['ar']({'drug': 'Fenbendazole'})
    print(deworming_ar)
    print()

    # اختبار رسالة تسميد
    print("3️⃣ إشعار تسميد الموز (Fertilizer):")
    print("-" * 60)
    fertilizer_ar = templates['fertilizer']['ar']({
        'tree': 'banana',
        'details': {
            'fertilizer': 'NPK 30-10-10',
            'amount_kg': 1.0
        }
    })
    print(fertilizer_ar)
    print()

def check_links():
    """التحقق من وجود الروابط في جميع القوالب"""
    print("\n=== التحقق من الروابط ===\n")

    templates = get_messages_templates()

    for task_type, template in templates.items():
        ar_message = ""
        try:
            # محاولة استدعاء القالب مع بيانات وهمية
            test_data = {
                'drug': 'Test Drug',
                'tree': 'banana',
                'details': {'fertilizer': 'NPK', 'amount_kg': 1},
                'reason_ar': 'اختبار',
                'reason_bn': 'test'
            }
            ar_message = template['ar'](test_data)
        except Exception as e:
            print(f"❌ خطأ في {task_type}: {e}")
            continue

        # التحقق من وجود رابط
        has_link = '[🔍' in ar_message and '](https://' in ar_message
        status = "✅" if has_link else "⚠️"

        print(f"{status} {task_type:30} - {'يحتوي على رابط' if has_link else 'لا يحتوي على رابط'}")

def main():
    """تشغيل جميع الاختبارات"""
    print("=" * 70)
    print("🧪 اختبار تنسيق رسائل Telegram بصيغة MarkdownV2")
    print("=" * 70)

    test_escape_function()
    test_message_templates()
    check_links()

    print("\n" + "=" * 70)
    print("✅ اكتمال الاختبارات")
    print("=" * 70)

if __name__ == "__main__":
    main()
