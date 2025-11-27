#!/usr/bin/env python3
"""إرسال تذكير دواء الديدان المتأخر"""

import os
import sys
from dotenv import load_dotenv

# تحميل البيئة
load_dotenv()

# استيراد المنطق
from telegram_notifier import TelegramNotifier

def send_deworming_reminder():
    """إرسال تذكير دواء الديدان"""

    # قراءة التوكنات
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("❌ لم يتم العثور على TELEGRAM_BOT_TOKEN أو TELEGRAM_CHAT_ID")
        print("💡 تأكد من وجود ملف .env")
        return False

    try:
        # إنشاء المُرسِل
        notifier = TelegramNotifier(bot_token, chat_id)

        # الرسالة
        message_ar = """🪱 *تذكير: دواء الديدان*

⚠️ فاتنا موعد دواء الديدان \\(15 نوفمبر \\- Albendazole\\)

يُرجى إعطاء الدواء في أقرب وقت ممكن\\.

📅 الموعد القادم: 15 فبراير 2026 \\- Fenbendazole

[📖 معلومات دواء الديدان](https://smsmy\\.github\\.io/farm\\-smart\\-notifier/deworming\\.html)"""

        message_bn = """🪱 *করমি ওষধ সতরকীকরণ*

⚠️ আমরা কৃমির ওষুধের সময়সূচী মিস করেছি \\(১৫ নভেম্বর \\- Albendazole\\)

যত তাড়াতাড়ি সম্ভব ওষুধ দিন\\.

📅 পরবর্তী সময়সূচী: ১৫ ফেব্রুয়ারি ২০২৬ \\- Fenbendazole

[📖 কৃমি ওষুধ তথ্য](https://smsmy\\.github\\.io/farm\\-smart\\-notifier/deworming\\.html)"""

        # إرسال
        import asyncio
        asyncio.run(notifier._send_single_message({
            'ar': message_ar,
            'bn': message_bn,
            'image': None
        }))

        print("✅ تم إرسال تذكير دواء الديدان بنجاح!")
        return True

    except Exception as e:
        print(f"❌ فشل إرسال التذكير: {e}")
        return False

if __name__ == "__main__":
    send_deworming_reminder()
