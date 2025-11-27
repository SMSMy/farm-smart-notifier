#!/usr/bin/env python3
"""
اختبار بسيط لإرسال إشعار Telegram
Simple Telegram notification test
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من .env
load_dotenv()

# استيراد telegram_notifier
from telegram_notifier import TelegramNotifier

def main():
    print("=" * 60)
    print("🧪 اختبار إرسال إشعار Telegram")
    print("=" * 60)

    # قراءة التوكنات من البيئة
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    print(f"\n📋 TELEGRAM_BOT_TOKEN: {'✅ موجود' if bot_token else '❌ مفقود'}")
    print(f"📋 TELEGRAM_CHAT_ID: {'✅ موجود' if chat_id else '❌ مفقود'}")

    if not bot_token or not chat_id:
        print("\n❌ فشل: التوكنات مفقودة في ملف .env")
        return

    try:
        # إنشاء كائن TelegramNotifier
        print("\n🔧 إنشاء TelegramNotifier...")
        notifier = TelegramNotifier(bot_token, chat_id)

        # إرسال رسالة اختبار
        print("📤 إرسال رسالة اختبار...\n")
        success = notifier.test_connection()

        if success:
            print("\n✅ تم إرسال الإشعار بنجاح!")
            print("📱 تحقق من تطبيق Telegram الخاص بك")
        else:
            print("\n❌ فشل الإرسال")

    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
