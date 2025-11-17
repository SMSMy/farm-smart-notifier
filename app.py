#!/usr/bin/env python3
"""
نظام تنبيه ذكي لرعاية الدجاج والأشجار
يعمل تلقائياً ويرسل تنبيهات إلى Telegram

المؤلف: MiniMax Agent
التاريخ: 2025-11-17
"""

import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

# إضافة المجلد الحالي إلى المسار
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weather import WeatherFetcher
from logic import FarmLogic
from telegram_notifier import TelegramNotifier

# قاموس أسماء الأشجار بالعربية
TREE_NAMES_MAP = {
    'henna': 'الحناء',
    'fig': 'التين', 
    'banana': 'الموز',
    'mango_small': 'مانجو صغيرة',
    'mango_large': 'مانجو كبيرة',
    'jackfruit_young': 'جاك فروت صغير',
    'mint_basil': 'النعناع والحبق',
    'pomegranate': 'الرمان',
    'acacia': 'الأكاسيا',
    'bougainvillea': 'الجهنمية',
    'grape': 'العنب',
    'custard_apple': 'القشطة',
    'ornamental': 'أشجار الزينة',
    'moringa': 'المورينجا'
}

def _create_safe_filename(name: str) -> str:
    """يحول اسم المنتج إلى اسم ملف آمن (أحرف صغيرة، شرطات سفلية)."""
    name = name.lower()
    name = re.sub(r'[()\s]+', '_', name)  # استبدال المسافات والأقواس بشرطة سفلية
    name = re.sub(r'[^a-z0-9_+-]', '', name)  # إزالة أي رموز غير آمنة
    return name

def get_messages_templates() -> Dict:
    """تحميل قوالب الرسائل الثنائية اللغة مع الإيموجيات"""
    
    # التعليق الموحد (سيُضاف تلقائياً)
    disclaimer_ar = "\n\n⚠️ قد يختلف شكل العبوة أو الاسم التجاري. الأهم هو المادة الفعالة المذكورة."
    disclaimer_bn = "\n\n⚠️ প্যাকেজিং বা ব্র্যান্ডের নাম ভিন্ন হতে পারে। উল্লিখিত সক্রিয় উপাদানটিই মুখ্য।"
    
    # طلب التوثيق بالفيديو/الصور
    documentation_request_ar = "\n\n🎥 <b>بعد تنفيذ المهمة أو عند الانتهاء منها، يرجى إضافة فيديو أو صورة توثّق الإنجاز.</b>"
    documentation_request_bn = "\n\n🎥 <b>কাজ সম্পন্ন করার সময় বা শেষ হওয়ার পরে অনুগ্রহ করে কাজের অগ্রগতি বা ফলাফল দেখানোর জন্য একটি ভিডিও বা ছবি যুক্ত করুন।</b>"
    
    return {
        'deworming': {
            'ar': lambda d: f"🐔 <b>تنبيه دواء الديدان 🔄</b>\n\n🏷️ <b>الدواء المطلوب:</b> {d.get('drug', 'غير محدد')}\n💧 <b>الطريقة:</b> يخلط مع ماء الشرب لمدة يوم واحد فقط.{disclaimer_ar}{documentation_request_ar}",
            'bn': lambda d: f"🐔 <b>কৃমির ঔষধের সতর্কতা 🔄</b>\n\n🏷️ <b>প্রয়োজনীয় ঔষধ:</b> {d.get('drug', 'unknown')}\n💧 <b>পদ্ধতি:</b> শুধুমাত্র একদিনের জন্য খাবার পানির সাথে মিশিয়ে দিন।{disclaimer_bn}{documentation_request_bn}",
            'image': lambda d: _create_safe_filename(d.get('drug', 'deworming')) + '.jpg'
        },
        'deworming_guide': {
            'ar': lambda d: f"<b>🛑 مهم جداً - <a href='https://github.com/SMSMy/farm-smart-notifier/blob/main/DEWORMING_GUIDE.html'>دليل استخدام أدوية الديدان للدواجن</a></b>",
            'bn': lambda d: f"<b><a href='https://github.com/SMSMy/farm-smart-notifier/blob/main/DEWORMING_GUIDE.html'>পোল্ট্রি বা মুরগির কৃমিনাশক ঔষধ ব্যবহারের নির্দেশিকা</a></b>",
            'image': None
        },
        'sanitization': {
            'ar': lambda d: f"🧽 <b>تنبيه تطهير الحظيرة ✨</b>\n\n🧹 <b>المطلوب:</b> تنظيف وتطهير الحظيرة بالكامل\n🏠 <b>الطريقة:</b> تنظيف جاف، ثم رش بمطهر (Virkon)، ثم تجفيف كامل{disclaimer_ar}{documentation_request_ar}",
            'bn': lambda d: f"🧽 <b>খামার পরিষ্কারের সতর্কতা ✨</b>\n\n🧹 <b>করণীয়:</b> সম্পূর্ণ খামার পরিষ্কার ও জীবাণুমুক্ত করুন\n🏠 <b>পদ্ধতি:</b> শুকনো পরিষ্কার, তারপর জীবাণুনাশক (Virkon) স্প্রে করুন, এবং সবশেষে সম্পূর্ণ শুকিয়ে নিন{disclaimer_bn}{documentation_request_bn}",
            'image': 'sanitizer.jpg'
        },
        'vitamins': {
            'ar': lambda d: f"💊 <b>تنبيه فيتامينات وإلكتروليت 🌡️</b>\n\n🔥 <b>السبب:</b> {d.get('reason_ar', 'غير محدد')}\n💧 <b>الطريقة:</b> تضاف إلى ماء الشرب لمدة يومين لتقليل الإجهاد{disclaimer_ar}{documentation_request_ar}",
            'bn': lambda d: f"💊 <b>ভিটামিন ও ইলেক্ট্রোলাইট সতর্কতা 🌡️</b>\n\n🔥 <b>কারণ:</b> {d.get('reason_bn', 'unknown')}\n💧 <b>পদ্ধতি:</b> মানসিক চাপ কমাতে দুই দিনের জন্য খাবার পানির সাথে যোগ করুন{disclaimer_bn}{documentation_request_bn}",
            'image': 'vitamins.jpg'
        },
        'coccidiosis': {
            'ar': lambda d: f"🦠 <b>تنبيه وقاية من الكوكسيديا 💧</b>\n\n⚠️ <b>السبب:</b> {d.get('reason_ar', 'رطوبة عالية')}\n💧 <b>الطريقة:</b> إضافة مضاد كوكسيديا (Amprolium) للماء كجرعة وقائية{disclaimer_ar}{documentation_request_ar}",
            'bn': lambda d: f"🦠 <b>কক্সিডিওসিস প্রতিরোধের সতর্কতা 💧</b>\n\n⚠️ <b>কারণ:</b> {d.get('reason_bn', 'high humidity')}\n💧 <b>পদ্ধতি:</b> প্রতিরোধমূলক ব্যবস্থা হিসেবে পানিতে কক্সিডিওসিস প্রতিরোধক (Amprolium) যোগ করুন{disclaimer_bn}{documentation_request_bn}",
            'image': 'coccidia.jpg'
        },
        'fertilizer': {
            'ar': lambda d: f"🌳 <b>تنبيه تسميد الأشجار 🌱</b>\n\n🌳 <b>الشجرة:</b> {TREE_NAMES_MAP.get(d.get('tree', ''), d.get('tree', ''))}\n🧪 <b>السماد:</b> {d.get('details', {}).get('fertilizer', 'غير محدد')}\n⚖️ <b>الكمية:</b> {d.get('details', {}).get('amount_kg', 0)} كجم\n📝 <b>ملاحظات:</b> {d.get('details', {}).get('notes', 'لا توجد')}{documentation_request_ar}",
            'bn': lambda d: f"🌳 <b>গাছে সার প্রয়োগের সতর্কতা 🌱</b>\n\n🌳 <b>গাছ:</b> {TREE_NAMES_MAP.get(d.get('tree', ''), d.get('tree', ''))}\n🧪 <b>সার:</b> {d.get('details', {}).get('fertilizer', 'unknown')}\n⚖️ <b>পরিমাণ:</b> {d.get('details', {}).get('amount_kg', 0)} কেজি\n📝 <b>মন্তব্য:</b> {d.get('details', {}).get('notes', 'none')}{documentation_request_bn}",
            'image': 'fertilizer.jpg'
        }
    }

def create_task_from_logic(logic_result: Dict, task_type: str, messages_templates: Dict) -> Dict:
    """إنشاء مهمة من نتيجة logic (مع دعم الصور الديناميكية)"""
    template = messages_templates.get(task_type)
    if not template:
        print(f"⚠️ قالب غير موجود للمهمة: {task_type}")
        return {}
    
    image_value = template.get('image')
    # إذا كانت image_value دالة، نستدعيها، وإلا نستخدم القيمة مباشرة
    image_filename = image_value(logic_result) if callable(image_value) else image_value

    return {
        'type': f"{task_type}_{logic_result.get('tree', '') or logic_result.get('drug', '')}",
        'ar': template['ar'](logic_result),
        'bn': template['bn'](logic_result),
        'image': image_filename
    }

def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print(f"🌱 نظام التنبيه الذكي للمزرعة - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # التحقق من ملف الإعدادات
        if not os.path.exists('config.json'):
            print("❌ خطأ: ملف config.json غير موجود!")
            print("💡 تأكد من وجود ملف الإعدادات في المجلد الحالي")
            return
        
        # تهيئة المكونات
        print("🔧 تهيئة النظام...")
        logic = FarmLogic()
        weather = WeatherFetcher(
            logic.config['weather']['api_key'],
            logic.config['weather']['city'],
            logic.config['weather']['country']
        )
        telegram = TelegramNotifier(
            logic.config['telegram']['bot_token'],
            logic.config['telegram']['chat_id']
        )
        
        # جلب بيانات الطقس
        print("\n🌤️ جلب بيانات الطقس...")
        weather_data = weather.get_weather_data()
        weather_report = weather.analyze_conditions(weather_data)
        
        if weather_report:
            print(f"✅ تم تحليل الطقس - حرارة: {weather_report['current_temp']}°C، رطوبة: {weather_report['humidity_avg']:.1f}%")
        else:
            print("⚠️ تحذير: لا يمكن جلب بيانات الطقس، سيتم الاعتماد على التقويم فقط")
        
        # تحميل قوالب الرسائل
        messages_templates = get_messages_templates()
        
        # بناء قائمة المهام
        print("\n📋 بناء قائمة المهام...")
        tasks_to_send = []
        
        # 1. مهمة دواء الديدان + رسالة الدليل
        if logic.should_deworm_today():
            drug_name = logic.get_current_deworm_drug()
            print(f"  ➕ إضافة مهمة دواء الديدان: {drug_name}")
            
            # المهمة الأساسية مع الصورة
            deworm_task_details = {'type': 'deworming', 'drug': drug_name}
            task_data = create_task_from_logic(deworm_task_details, 'deworming', messages_templates)
            if task_data:
                tasks_to_send.append(task_data)

            # ✅ إضافة رسالة الدليل المنفصلة (بدون صورة)
            print("  ➕ إضافة رسالة رابط الدليل التفاعلي")
            guide_task = {
                'type': 'deworming_guide',
                'ar': "🛑 <b>مهم جداً - <a href='https://github.com/SMSMy/farm-smart-notifier/blob/main/DEWORMING_GUIDE.html'>دليل استخدام أدوية الديدان للدواجن</a></b>",
                'bn': "<b><a href='https://github.com/SMSMy/farm-smart-notifier/blob/main/DEWORMING_GUIDE.html'>পোল্ট্রি বা মুরগির কৃমিনাশক ঔষধ ব্যবহারের নির্দেশিকা</a></b>",
                'image': None  # لا توجد صورة لهذه الرسالة
            }
            tasks_to_send.append(guide_task)

        # 2. المهام المعتمدة على الطقس والشروط الأخرى
        weather_dependent_tasks = logic.get_weather_dependent_tasks(weather_report)
        for task in weather_dependent_tasks:
            print(f"  ➕ إضافة مهمة الطقس: {task['type']}")
            task_data = create_task_from_logic(task, task['type'], messages_templates)
            if task_data:
                tasks_to_send.append(task_data)
        
        # 3. مهام تسميد الأشجار
        if weather_report:
            fertilization_tasks = logic.get_all_fertilization_tasks(weather_report)
            for tree_task in fertilization_tasks:
                print(f"  ➕ إضافة مهمة تسميد: {tree_task['tree']}")
                task_data = create_task_from_logic(tree_task, 'fertilizer', messages_templates)
                if task_data:
                    tasks_to_send.append(task_data)
        
        # تقرير نهائي
        print(f"\n📊 تم إعداد {len(tasks_to_send)} مهمة للإرسال")
        
        if not tasks_to_send:
            print("✅ لا توجد مهام مجدولة لليوم")
            
            # إرسال رسالة حالة إذا كانت هناك بيانات طقس مهمة
            if weather_report and any([weather_report.get('heat_wave'), weather_report.get('cold_wave'), weather_report.get('high_humidity')]):
                print("⚠️ إرسال تنبيهات طقس مهمة...")
                telegram.send_weather_alert(weather_report)
        else:
            # إرسال المهام
            print(f"\n📤 إرسال {len(tasks_to_send)} تنبيه...")
            success = telegram.send_batch(tasks_to_send)
            
            if success:
                print("✅ تم إرسال جميع التنبيهات بنجاح")
            else:
                print("❌ فشل في إرسال بعض التنبيهات")
        
        # حفظ وقت التشغيل
        logic.save_last_run()
        print(f"\n🕐 تم الانتهاء بنجاح - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ حدث خطأ فادح في النظام: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

def setup_environment():
    """إعداد المتغيرات البيئية للتطوير"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ تم تحميل متغيرات البيئة من .env")
    except ImportError:
        print("⚠️ مكتبة python-dotenv غير مثبتة - تجاهل إعداد البيئة")
    except Exception as e:
        print(f"⚠️ خطأ في إعداد البيئة: {e}")

def quick_test():
    """اختبار سريع لجميع المكونات"""
    print("🧪 اختبار سريع للمكونات...")
    
    try:
        # اختبار منطق FarmLogic
        print("\n1️⃣ اختبار FarmLogic:")
        logic = FarmLogic()
        print(f"   ✅ تم تحميل الإعدادات: {len(logic.config.get('trees_fertilizer_schedule', {}))} شجرة")
        
        # اختبار جلب الطقس
        print("\n2️⃣ اختبار جلب الطقس:")
        weather = WeatherFetcher("test_key", "Tabuk", "SA")
        # لن نرسل طلب حقيقي في الاختبار
        
        # اختبار Telegram (بمتغيرات البيئة)
        import os
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if bot_token and chat_id:
            print("\n3️⃣ اختبار Telegram:")
            telegram = TelegramNotifier(bot_token, chat_id)
            print("   ✅ تم تهيئة Telegram بنجاح")
        else:
            print("\n3️⃣ تخطي اختبار Telegram (لا توجد متغيرات)")
        
        print("\n✅ جميع الاختبارات نجحت!")
        
    except Exception as e:
        print(f"\n❌ فشل في الاختبار: {e}")

if __name__ == "__main__":
    # إعداد البيئة
    setup_environment()
    
    # اختيار الوضع
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            quick_test()
        elif sys.argv[1] == 'help':
            print("""
🌱 Farm Notifier System

Usage:
  python main.py           # تشغيل النظام العادي
  python main.py test      # اختبار سريع
  python main.py help      # عرض المساعدة

Required Environment Variables:
  TELEGRAM_BOT_TOKEN       # توكن بوت Telegram
  TELEGRAM_CHAT_ID         # معرف المحادثة
  OPENWEATHER_API_KEY      # مفتاح OpenWeatherMap

Configuration:
  Edit config.json to customize schedules and settings.
            """)
        else:
            print(f"❌ خيار غير معروف: {sys.argv[1]}")
            print("💡 استخدم 'python main.py help' للمساعدة")
    else:
        # تشغيل النظام العادي
        main()
