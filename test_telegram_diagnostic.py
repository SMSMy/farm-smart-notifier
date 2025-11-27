#!/usr/bin/env python3
"""
اختبار تفصيلي لإرسال إشعار Telegram مع معلومات تشخيصية
Detailed Telegram notification test with diagnostic information
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من .env
load_dotenv()

def main():
    print("=" * 60)
    print("🧪 اختبار Telegram - تشخيص تفصيلي")
    print("=" * 60)

    # قراءة التوكنات من البيئة
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    print(f"\n📋 معلومات البيئة:")
    print(f"   TELEGRAM_BOT_TOKEN: {bot_token[:20]}...{bot_token[-10:] if bot_token else 'NONE'}")
    print(f"   TELEGRAM_CHAT_ID: {chat_id}")

    if not bot_token or not chat_id:
        print("\n❌ فشل: التوكنات مفقودة في ملف .env")
        return

    # التحقق من صحة chat_id
    expected_chat_id = "1003443250446"
    if chat_id != expected_chat_id:
        print(f"\n⚠️ تحذير: TELEGRAM_CHAT_ID غير متطابق!")
        print(f"   المتوقع: {expected_chat_id}")
        print(f"   الموجود: {chat_id}")
    else:
        print(f"\n✅ TELEGRAM_CHAT_ID صحيح: {chat_id}")

    try:
        # إرسال رسالة بسيطة جداً بدون async
        print("\n🔧 محاولة إرسال رسالة مباشرة...")

        import requests

        # إرسال رسالة بسيطة عبر HTTP API
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        message_text = (
            "🧪 اختبار نظام التنبيه للمزرعة\n\n"
            f"✅ تم الاتصال بنجاح\n"
            f"🕐 الوقت: {os.popen('echo %time%').read().strip()}\n"
            f"📱 Chat ID: {chat_id}\n\n"
            "إذا وصلتك هذه الرسالة، فالنظام يعمل بشكل صحيح!"
        )

        payload = {
            'chat_id': chat_id,
            'text': message_text
        }

        print(f"📤 إرسال إلى: {url}")
        print(f"📝 Chat ID: {chat_id}")

        response = requests.post(url, json=payload, timeout=10)

        print(f"\n📊 استجابة API:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:500]}")

        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("\n✅ تم إرسال الرسالة بنجاح!")
                print("📱 تحقق من تطبيق Telegram")
            else:
                print(f"\n❌ فشل: {result}")
        else:
            print(f"\n❌ خطأ HTTP: {response.status_code}")
            print(f"   الرسالة: {response.text}")

    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
