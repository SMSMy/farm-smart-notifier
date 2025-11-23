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

def escape_markdown_v2(text: str) -> str:
    """Escape special characters for MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def get_messages_templates() -> Dict:
    """تحميل قوالب الرسائل الثنائية اللغة مع الإيموجيات بتنسيق MarkdownV2"""

    # الرابط الأساسي لصفحات GitHub Pages
    BASE_URL = "https://smsmy.github.io/farm-smart-notifier/docs"

    # التعليق الموحد (سيُضاف تلقائياً)
    disclaimer_ar = escape_markdown_v2("\n\n⚠️ قد يختلف شكل العبوة أو الاسم التجاري. الأهم هو المادة الفعالة المذكورة.")
    disclaimer_bn = escape_markdown_v2("\n\n⚠️ প্যাকেজিং বা ব্র্যান্ডের নাম ভিন্ন হতে পারে। উল্লিখিত সক্রিয় উপাদানটিই মুখ্য।")

    # طلب التوثيق بالفيديو/الصور
    documentation_request_ar = escape_markdown_v2("\n\n🎥 *بعد تنفيذ المهمة، يرجى إضافة فيديو أو صورة توثّق الإنجاز.*")
    documentation_request_bn = escape_markdown_v2("\n\n🎥 *কাজ সম্পন্ন করার পরে অনুগ্রহ করে একটি ভিডিও বা ছবি যুক্ত করুন।*")

    return {
        'deworming': {
            'ar': lambda d: f"🐔 *تنبيه دواء الديدان* 🔄\n\n🏷️ *الدواء المطلوب:* {escape_markdown_v2(d.get('drug', 'غير محدد'))}\n💧 *الطريقة:* {escape_markdown_v2('يخلط مع ماء الشرب لمدة يوم واحد فقط.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/deworming.html){disclaimer_ar}{documentation_request_ar}",
            'bn': lambda d: f"🐔 *কৃমির ঔষধের সতর্কতা* 🔄\n\n🏷️ *প্রয়োজনীয় ঔষধ:* {escape_markdown_v2(d.get('drug', 'unknown'))}\n💧 *পদ্ধতি:* {escape_markdown_v2('শুধুমাত্র একদিনের জন্য খাবার পানির সাথে মিশিয়ে দিন।')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/deworming.html){disclaimer_bn}{documentation_request_bn}",
            'image': lambda d: _create_safe_filename(d.get('drug', 'deworming')) + '.jpg'
        },
        'deworming_guide': {
            'ar': lambda d: f"🛑 *مهم جداً \\- دليل استخدام أدوية الديدان للدواجن*\n\n[🔍 اضغط هنا للمزيد من التفاصيل]({BASE_URL}/deworming.html)",
            'bn': lambda d: f"🛑 *গুরুত্বপূর্ণ \\- পোল্ট্রি কৃমিনাশক ঔষধ ব্যবহারের নির্দেশিকা*\n\n[🔍 বিস্তারিত দেখুন]({BASE_URL}/deworming.html)",
            'image': None
        },
        'sanitization': {
            'ar': lambda d: f"🧹 *تنبيه تطهير الحظيرة* 🧹\n\n{escape_markdown_v2('حان وقت تطهير وتعقيم الحظيرة لضمان بيئة نظيفة وصحية للطيور.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/sanitization.html){disclaimer_ar}{documentation_request_ar}",
            'bn': lambda d: f"🧹 *খামার পরিষ্কারের সতর্কতা* 🧹\n\n{escape_markdown_v2('পাখিদের জন্য পরিষ্কার এবং স্বাস্থ্যকর পরিবেশ নিশ্চিত করতে খামার পরিষ্কার এবং জীবাণুমুক্ত করার সময়।')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/sanitization.html){disclaimer_bn}{documentation_request_bn}",
            'image': 'sanitizer.jpg'
        },
        'vitamins': {
            'ar': lambda d: f"💊 *تنبيه فيتامينات وإלكتروليت* 🌡️\n\n🔥 *السبب:* {escape_markdown_v2(d.get('reason_ar', 'غير محدد'))}\n💧 *الطريقة:* {escape_markdown_v2('تضاف إلى ماء الشرب لمدة يومين.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/vitamins.html){disclaimer_ar}{documentation_request_ar}",
            'bn': lambda d: f"💊 *ভিটামিন ও ইলেক্ট্রোলাইট সতর্কতা* 🌡️\n\n🔥 *কারণ:* {escape_markdown_v2(d.get('reason_bn', 'unknown'))}\n💧 *পদ্ধতি:* {escape_markdown_v2('দুই দিনের জন্য পানির সাথে যোগ করুন।')}\n\n[🔍 আরও বিস্তारিত]({BASE_URL}/vitamins.html){disclaimer_bn}{documentation_request_bn}",
            'image': 'vitamins.jpg'
        },
        'coccidiosis': {
            'ar': lambda d: f"🦠 *تنبيه وقاية من الكوكسيديا* 💧\n\n⚠️ *السبب:* {escape_markdown_v2(d.get('reason_ar', 'رطوبة عالية'))}\n💧 *الطريقة:* {escape_markdown_v2('إضافة مضاد كوكسيديا للماء.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/coccidiosis.html){disclaimer_ar}{documentation_request_ar}",
            'bn': lambda d: f"🦠 *কক্সিডিওসিস প্রতিরোধের সতর্কতা* 💧\n\n⚠️ *কারণ:* {escape_markdown_v2(d.get('reason_bn', 'high humidity'))}\n💧 *পদ্ধতি:* {escape_markdown_v2('পানিতে কক্সিডিওসিস প্রতিরোধক যোগ করুন।')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/coccidiosis.html){disclaimer_bn}{documentation_request_bn}",
            'image': 'coccidia.jpg'
        },
        'fertilizer': {
            'ar': lambda d: f"🍌 *تنبيه تسميد {escape_markdown_v2(TREE_NAMES_MAP.get(d.get('tree', ''), d.get('tree', '')))}* 🍌\n\n{escape_markdown_v2('حان موعد تسميد المحصول للحصول على أفضل جودة وكمية. تفقّد النباتات الآن.')}\n\n🧪 *السماد:* {escape_markdown_v2(d.get('details', {}).get('fertilizer', 'غير محدد'))}\n⚖️ *الكمية:* {escape_markdown_v2(str(d.get('details', {}).get('amount_kg', 0)) + ' كجم')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/{d.get('tree', 'fertilizer')}.html){documentation_request_ar}",
            'bn': lambda d: f"🍌 *{escape_markdown_v2(TREE_NAMES_MAP.get(d.get('tree', ''), d.get('tree', '')))} সার প্রয়োগের সতর্কতা* 🍌\n\n{escape_markdown_v2('সেরা মানের ও পরিমাণের জন্য ফসলে সার দেওয়ার সময়। এখনই গাছ পরীক্ষা করুন।')}\n\n🧪 *সার:* {escape_markdown_v2(d.get('details', {}).get('fertilizer', 'unknown'))}\n⚖️ *পরিমাণ:* {escape_markdown_v2(str(d.get('details', {}).get('amount_kg', 0)) + ' কেজি')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/{d.get('tree', 'fertilizer')}.html){documentation_request_bn}",
            'image': 'fertilizer.jpg'
        },
        'water_station': {
            'ar': lambda d: f"🚰 *تنبيه تنظيف محطة الماء* 💧\n\n{escape_markdown_v2('حان وقت تنظيف نظام المياه.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/water_station.html){disclaimer_ar}{documentation_request_ar}",
            'bn': lambda d: f"🚰 *পানি সরবরাহ সিস্টেম পরিষ্কার সতর্কতা* 💧\n\n{escape_markdown_v2('পানি ব্যবস্থা পরিষ্কার করার সময়।')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/water_station.html){disclaimer_bn}{documentation_request_bn}",
            'image': 'water_station.jpg'
        },
        'pipe_waterer_change_water': {
            'ar': lambda d: f"🚰 *تنبيه السقاية الأنبوبية: تغيير الماء* 💧\n\n⏱️ {escape_markdown_v2('كل 3 أيام')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/pipe_waterer.html){documentation_request_ar}",
            'bn': lambda d: f"🚰 *পাইপ ওয়াটারার: পانি পরিবর্তন* 💧\n\n⏱️ {escape_markdown_v2('প্রতি ৩ দিন')}\n\n[🔍 আরও বিস্تারিত]({BASE_URL}/pipe_waterer.html){documentation_request_bn}",
            'image': 'pipe_waterer.jpg'
        },
        'pipe_waterer_rinse': {
            'ar': lambda d: f"🚰 *تنبيه السقاية الأنبوبية: شطف أسبوعي* 🚿\n\n{escape_markdown_v2('تنظيف الأنابيب من الرواسב.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/pipe_waterer.html){documentation_request_ar}",
            'bn': lambda d: f"🚰 *পাইপ ওয়াটারার: সাপ্তাহিক ধোয়া* 🚿\n\n{escape_markdown_v2('পাইপ পরিষ্কার করুন।')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/pipe_waterer.html){documentation_request_bn}",
            'image': 'pipe_waterer.jpg'
        },
        'pipe_waterer_sanitize': {
            'ar': lambda d: f"🚰 *تنبيه السقاية الأنبوبية: تعقيم* 🧪\n\n{escape_markdown_v2('تعقيم الأنابيب.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/pipe_waterer.html){documentation_request_ar}",
            'bn': lambda d: f"🚰 *পাইপ ওয়াটারার: জীবাণুমুক্তকরণ* 🧪\n\n{escape_markdown_v2('পাইপ জীবاণুমুক্ত করুন।')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/pipe_waterer.html){documentation_request_bn}",
            'image': 'pipe_waterer.jpg'
        },
        'pipe_waterer_deep_clean': {
            'ar': lambda d: f"🚰 *تنبيه السقاية الأنبوبية: تنظيف عميق* 🧽\n\n{escape_markdown_v2('إزالة البكتيريا المتراكمة.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/pipe_waterer.html){documentation_request_ar}",
            'bn': lambda d: f"🚰 *পাইপ ওয়াটারার: গভীর পরিষ্কার* 🧽\n\n{escape_markdown_v2('জমে থাকা ব্যাকটেরিয়া দূর করুন।')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/pipe_waterer.html){documentation_request_bn}",
            'image': 'pipe_waterer_deep.jpg'
        },
        'weekly_cleaning': {
            'ar': lambda d: f"🧹 *تنبيه التنظيف الأسبوعي للحظيرة* ✨\n\n{escape_markdown_v2('تنظيف الحظيرة الأسبوعي.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/weekly_cleaning.html){documentation_request_ar}",
            'bn': lambda d: f"🧹 *সাপ্তাহিক খামার পরিষ্কার সতর্কতা* ✨\n\n{escape_markdown_v2('সাপ্তাহিক খামার পরিষ্কার।')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/weekly_cleaning.html){documentation_request_bn}",
            'image': 'coop_cleaning.jpg'
        },
        'soil_turning': {
            'ar': lambda d: f"🌾 *تنبيه تقليب التراب داخل الحظيرة* 🔄\n\n{escape_markdown_v2('تقليب التربة لتقليل الرطوبة.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/soil_turning.html){documentation_request_ar}",
            'bn': lambda d: f"🌾 *মাটি নাড়াচাড়া সতর্কতা* 🔄\n\n{escape_markdown_v2('আদ্রতা কমাতে মাটি আলগা করুন।')}\n\n[🔍 আরও বিস্তারিত]({BASE_URL}/soil_turning.html){documentation_request_bn}",
            'image': 'soil_turning.jpg'
        },
        'ventilation': {
            'ar': lambda d: f"🌬️ *تنبيه فحص التهوية* 💨\n\n{escape_markdown_v2('فحص التهوية وتدفق الهواء.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/ventilation.html){documentation_request_ar}",
            'bn': lambda d: f"🌬️ *বায়ুচলাচল பরীক্ষা সতর্কতা* 💨\n\n{escape_markdown_v2('বায়ুচলাচل পরীক্ষা করুন।')}\n\n[🔍 আরও বিস্তारিত]({BASE_URL}/ventilation.html){documentation_request_bn}",
            'image': 'ventilation.jpg'
        },
        'feeder_cleaning': {
            'ar': lambda d: f"🍽️ *تنبيه غسيل المعالف العميق* 🧼\n\n{escape_markdown_v2('تنظيف وتطهير المعالف.')}\n\n[🔍 المزيد من التفاصيل]({BASE_URL}/feeder_cleaning.html){documentation_request_ar}",
            'bn': lambda d: f"🍽️ *খাবার পাত্রের গভীর পরিষ্কার* 🧼\n\n{escape_markdown_v2('খাবার পাত্র পরিষ্কার করুন।')}\n\n[🔍 আরও بਿস্তারিত]({BASE_URL}/feeder_cleaning.html){documentation_request_bn}",
            'image': 'feeder_cleaning.jpg'
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

        # استخدام مفتاح API من متغيرات البيئة إذا وجد
        api_key = os.getenv('OPENWEATHER_API_KEY') or logic.config['weather']['api_key']

        weather = WeatherFetcher(
            api_key,
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
                'ar': "🛑 <b>مهم جداً - <a href='https://smsmy.github.io/farm-smart-notifier/docs/deworming.html'>دليل استخدام أدوية الديدان للدواجن</a></b>",
                'bn': "<b><a href='https://smsmy.github.io/farm-smart-notifier/docs/deworming.html'>পোল্ট্রি বা মুরগি কৃমিনাশক ঔষধ ব্যবহারের নির্দেশিকা</a></b>",
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
