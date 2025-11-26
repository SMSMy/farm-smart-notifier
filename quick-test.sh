#!/bin/bash

# 🧪 اختبار سريع لنظام التنبيه الذكي للمزرعة
# Quick test script for Farm Smart Notifier

set -e

echo "🧪 بدء اختبار نظام التنبيه الذكي للمزرعة..."
echo "🧪 Starting Farm Smart Notifier test..."

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت."
    echo "❌ Python3 is not installed."
    exit 1
fi

echo "✅ Python3 متوفر."

# التحقق من وجود الملفات المطلوبة
required_files=("app.py" "telegram_notifier.py" "weather.py" "logic.py" ".env.example")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ ملفات مفقودة:"
    echo "❌ Missing files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

echo "✅ جميع الملفات المطلوبة موجودة."

# التحقق من ملف .env
if [ ! -f ".env" ]; then
    echo "⚠️ ملف .env غير موجود."
    echo "⚠️ .env file not found."

    echo "📝 الرجاء إدخال TELEGRAM_BOT_TOKEN:"
    echo "📝 Please enter TELEGRAM_BOT_TOKEN:"
    read -r bot_token

    if [ -z "$bot_token" ]; then
        echo "❌ لم يتم إدخال التوكن. الخروج..."
        echo "❌ No token entered. Exiting..."
        exit 1
    fi

    echo "📝 جاري إنشاء ملف .env..."
    echo "📝 Creating .env file..."

    cat > .env << EOF
# ملف اختبار للنظام
TELEGRAM_BOT_TOKEN=$bot_token
TELEGRAM_CHAT_ID=1003443250446
OPENWEATHER_API_KEY=dbe40b3b9ff7646fb726a1a1bde13aba
WEATHER_CITY=Tabuk
WEATHER_COUNTRY=SA
DEBUG_MODE=true
LOG_FILE=test_farm_notifier.log
TIMEZONE=Asia/Dhaka
EOF

    echo "✅ تم إنشاء ملف .env."
else
    echo "✅ ملف .env موجود."
fi

# تثبيت المكتبات إذا لزم الأمر
echo "📦 التحقق من المكتبات المطلوبة..."
if python3 -c "import telegram, requests, dotenv" 2>/dev/null; then
    echo "✅ جميع المكتبات مثبتة."
else
    echo "⚠️ تثبيت المكتبات المطلوبة..."
    pip3 install python-telegram-bot requests python-dotenv pytz
fi

# تشغيل الاختبار
echo ""
echo "🚀 تشغيل اختبار النظام..."
echo "🚀 Running system test..."

python3 -c "
import sys
import os
from datetime import datetime

print('📋 اختبار تحميل المكونات...')
print('📋 Testing component loading...')

# اختبار تحميل weather
try:
    from weather import WeatherFetcher
    print('✅ WeatherFetcher محمّل بنجاح')
except Exception as e:
    print(f'❌ خطأ في WeatherFetcher: {e}')
    sys.exit(1)

# اختبار تحميل logic
try:
    from logic import FarmLogic
    print('✅ FarmLogic محمّل بنجاح')
except Exception as e:
    print(f'❌ خطأ في FarmLogic: {e}')
    sys.exit(1)

# اختبار تحميل telegram_notifier
try:
    from telegram_notifier import TelegramNotifier
    print('✅ TelegramNotifier محمّل بنجاح')
except Exception as e:
    print(f'❌ خطأ في TelegramNotifier: {e}')
    sys.exit(1)

# اختبار إعداد البيئة
try:
    from dotenv import load_dotenv
    load_dotenv()
    print('✅ متغيرات البيئة محمّلة')
except Exception as e:
    print(f'❌ خطأ في متغيرات البيئة: {e}')

# اختبار إعداد FarmLogic
try:
    farm_logic = FarmLogic()
    print(f'✅ FarmLogic مُعدّ بنجاح - {len(farm_logic.trees)} شجرة')
except Exception as e:
    print(f'❌ خطأ في إعداد FarmLogic: {e}')
    sys.exit(1)

# اختبار إعداد Telegram
try:
    from telegram_notifier import TelegramNotifier
    telegram = TelegramNotifier()
    print('✅ TelegramNotifier مُعدّ بنجاح')
except Exception as e:
    print(f'❌ خطأ في إعداد TelegramNotifier: {e}')
    sys.exit(1)

print('')
print('🎉 جميع الاختبارات نجحت!')
print('🎉 All tests passed!')
print('')
print('📱 معلومات البوت:')
print('📱 Bot information:')
try:
    bot_info = telegram.get_bot_info()
    if bot_info:
        print(f'  🤖 الاسم: {bot_info.get(\"first_name\", \"غير معروف\")}')
        print(f'  📱 Username: @{bot_info.get(\"username\", \"غير معروف\")}')
    else:
        print('  ⚠️ لم يتم الحصول على معلومات البوت')
except Exception as e:
    print(f'  ❌ خطأ في الحصول على معلومات البوت: {e}')

print('')
print('⚠️ ملاحظة:')
print('⚠️ Note:')
print('  📝 الاختبار المحلي تم بنجاح')
print('  📝 Local test completed successfully')
print('  🌐 لإرسال الرسائل فعلياً، تأكد من:')
print('  🌐 To send actual messages, ensure:')
print('     1. إضافة البوت للمجموعة')
print('     1. Bot is added to the group')
print('     2. صحة Chat ID')
print('     2. Correct Chat ID')
print('     3. صلاحيات البوت للإرسال')
print('     3. Bot has send permissions')
"

echo ""
echo "🏁 اكتمل اختبار النظام!"
echo "🏁 System test completed!"

# تنظيف ملف .env إذا كان اختبار فقط
if [ -f ".env" ] && ! grep -q "خقيقي" .env > /dev/null; then
    echo ""
    read -p "🗑️ هل تريد حذف ملف .env الاختبار؟ (y/n): " delete_env
    if [ "$delete_env" = "y" ] || [ "$delete_env" = "Y" ]; then
        rm .env
        echo "✅ تم حذف ملف .env الاختبار."
    fi
fi

echo ""
echo "🎯 الخطوة التالية:"
echo "🎯 Next step:"
echo "   📤 ارفع المشروع إلى GitHub باستخدام:"
echo "   📤 Upload to GitHub using:"
echo "   bash deploy-to-github.sh"
