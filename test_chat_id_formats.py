#!/usr/bin/env python3
"""
اختبار Chat ID مع تنسيقات مختلفة
Test Chat ID with different formats
"""

import requests
import time

def test_chat_id(bot_token, chat_id, description):
    """اختبار chat_id محدد"""
    print(f"\n{'='*60}")
    print(f"🧪 اختبار: {description}")
    print(f"📱 Chat ID: {chat_id}")
    print(f"{'='*60}")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    message_text = f"🧪 اختبار {description}\n📱 Chat ID المستخدم: {chat_id}"

    payload = {
        'chat_id': str(chat_id),
        'text': message_text
    }

    try:
        print("📤 إرسال الطلب...")
        response = requests.post(url, json=payload, timeout=15)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ تم الإرسال بنجاح!")
                print(f"📋 معلومات الرسالة: {result.get('result', {}).get('message_id', 'N/A')}")
                return True
            else:
                print(f"❌ فشل: {result}")
                return False
        else:
            print(f"❌ خطأ HTTP: {response.status_code}")
            result = response.json() if response.text else {}
            print(f"📝 الرد: {result}")

            if 'description' in result:
                print(f"💬 الوصف: {result['description']}")

            return False

    except requests.exceptions.Timeout:
        print("⏱️ انتهت مهلة الطلب (Timeout)")
        return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def main():
    # معلومات البوت
    bot_token = "8570871156:AAHmHPx715silUtWbir-y3N8IJVjxIuGcQQ"

    print("=" * 60)
    print("🔍 اختبار تنسيقات Chat ID المختلفة")
    print("=" * 60)

    # تنسيقات مختلفة لاختبارها
    chat_ids = [
        (1003443250446, "رقم موجب (كما هو)"),
        (-1003443250446, "رقم سالب (للمجموعات/القنوات)"),
        ("1003443250446", "نص موجب"),
        ("-1003443250446", "نص سالب"),
    ]

    results = []

    for chat_id, description in chat_ids:
        success = test_chat_id(bot_token, chat_id, description)
        results.append((description, success))
        time.sleep(2)  # تأخير بين الطلبات

    # ملخص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج")
    print("=" * 60)

    for description, success in results:
        status = "✅ نجح" if success else "❌ فشل"
        print(f"{status} - {description}")

    print("\n💡 ملاحظة:")
    print("   - إذا نجح الرقم السالب، استخدم: -1003443250446")
    print("   - إذا نجح الرقم الموجب، استخدم: 1003443250446")
    print("   - المجموعات والقنوات عادةً تحتاج رقم سالب")

if __name__ == "__main__":
    main()
