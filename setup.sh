#!/bin/bash

# ===============================================
# 🌱 Farm Notifier System - Setup Script
# نظام التنبيه الذكي للمزرعة - سكريبت الإعداد
# ===============================================

echo "🌱 🌱 🌱 نظام التنبيه الذكي للمزرعة 🌱 🌱 🌱"
echo "=============================================="

# التحقق من Python
echo "🔍 التحقق من Python..."
if command -v python3 &> /dev/null; then
    echo "✅ Python متوفر: $(python3 --version)"
else
    echo "❌ Python غير مثبت!"
    echo "💡 قم بتثبيت Python من https://python.org"
    exit 1
fi

# التحقق من Git
echo "🔍 التحقق من Git..."
if command -v git &> /dev/null; then
    echo "✅ Git متوفر: $(git --version)"
else
    echo "❌ Git غير مثبت!"
    echo "💡 قم بتثبيت Git من https://git-scm.com"
    exit 1
fi

echo ""
echo "📦 تثبيت المكتبات المطلوبة..."

# إنشاء بيئة افتراضية (اختياري)
read -p "هل تريد إنشاء بيئة Python افتراضية؟ (y/N): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "🔧 إنشاء بيئة افتراضية..."
    python3 -m venv farm-notifier-env
    source farm-notifier-env/bin/activate
    echo "✅ تم تفعيل البيئة الافتراضية"
fi

# تثبيت المكتبات
echo "📦 تثبيت المكتبات..."
pip install python-telegram-bot requests python-dotenv pytz

if [ $? -eq 0 ]; then
    echo "✅ تم تثبيت المكتبات بنجاح"
else
    echo "❌ فشل في تثبيت المكتبات"
    exit 1
fi

echo ""
echo "🔧 إعداد ملفات التكوين..."

# التحقق من وجود ملف .env
if [ ! -f .env ]; then
    echo "📝 إنشاء ملف .env..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ تم إنشاء ملف .env من القالب"
    else
        cat > .env << EOF
# === TELEGRAM ===
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE

# === WEATHER ===
WEATHER_API_KEY=YOUR_WEATHER_API_KEY
EOF
        echo "✅ تم إنشاء ملف .env جديد"
    fi
    
    echo ""
    echo "⚠️  تحديث ملف .env مطلوب!"
    echo "   افتح ملف .env وأضف مفاتيحك الحقيقية:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_ID" 
    echo "   - WEATHER_API_KEY"
    echo ""
    read -p "هل تريد فتح ملف .env الآن للتعديل؟ (y/N): " open_env
    if [[ $open_env =~ ^[Yy]$ ]]; then
        if command -v code &> /dev/null; then
            code .env
        elif command -v nano &> /dev/null; then
            nano .env
        else
            echo "لا يمكن فتح محرر تلقائياً. يرجى فتح .env يدوياً"
        fi
    fi
fi

echo ""
echo "🧪 اختبار النظام..."

# اختبار سريع
echo "🔍 اختبار المكونات..."
python3 app.py test

echo ""
echo "🎯 الخطوات التالية:"
echo "1️⃣ تحديث ملف .env بالمفاتيح الحقيقية"
echo "2️⃣ إنشاء Telegram Bot عبر @BotFather"
echo "3️⃣ إضافة البوت للمحادثة/المجموعة"
echo "4️⃣ الحصول على مفتاح Weather API من OpenWeatherMap"
echo ""
echo "📖 اقرأ INSTALLATION_GUIDE.md للتفاصيل الكاملة"

echo ""
echo "🎉 تم إعداد النظام بنجاح!"
echo "   للاستفسارات، راجع الدليل في INSTALLATION_GUIDE.md"
echo "=============================================="
