#!/usr/bin/env python3
"""
ملف تشغيل خادم API للعداد الزمني
Farm Notifier API Server Launcher
"""

import os
import sys
import subprocess
import threading
import time
from datetime import datetime

def check_requirements():
    """فحص المتطلبات المطلوبة"""
    required_packages = ['flask', 'flask_cors']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ المكتبات التالية مفقودة:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 لتثبيت المتطلبات:")
        print("   pip install -r requirements.txt")
        return False

    return True

def check_config():
    """فحص ملف الإعدادات"""
    if not os.path.exists('config.json'):
        print("❌ ملف config.json غير موجود!")
        return False

    try:
        import json
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        # فحص الأقسام المطلوبة
        required_sections = ['chicken_schedule', 'trees_fertilizer_schedule']
        for section in required_sections:
            if section not in config:
                print(f"❌ قسم {section} مفقود في config.json")
                return False

        print("✅ ملف الإعدادات صحيح")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ خطأ في تحليل config.json: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في قراءة config.json: {e}")
        return False

def start_api_server():
    """تشغيل خادم API"""
    try:
        print("🚀 بدء تشغيل خادم API...")
        print("📡 الخادم متاح على: http://localhost:5000")
        print("🔗 العداد التنازلي: http://localhost:5000/api/notifications/countdown")
        print("📊 إشعارات اليوم: http://localhost:5000/api/notifications/today")
        print("📋 الإشعارات القادمة: http://localhost:5000/api/notifications/next")
        print("💚 فحص الصحة: http://localhost:5000/api/health")
        print("-" * 60)

        # تشغيل الخادم
        from api import app
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الخادم بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل الخادم: {e}")

def open_browser():
    """فتح المتصفح تلقائياً"""
    time.sleep(2)  # انتظار حتى يبدأ الخادم

    try:
        import webbrowser

        # فتح صفحة الاختبار
        test_url = "http://localhost:5000/api/health"
        print(f"🌐 فتح المتصفح: {test_url}")
        webbrowser.open(test_url)

        # فتح صفحة HTML الرئيسية إذا وجدت
        if os.path.exists('docs/index.html'):
            html_path = os.path.abspath('docs/index.html')
            print(f"📄 فتح الصفحة الرئيسية: file://{html_path}")
            webbrowser.open(f"file://{html_path}")

    except Exception as e:
        print(f"⚠️ لا يمكن فتح المتصفح تلقائياً: {e}")

def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print("🌱 Farm Notifier API Server")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # فحص المتطلبات
    print("🔍 فحص المتطلبات...")
    if not check_requirements():
        return

    if not check_config():
        return

    print("✅ جميع المتطلبات متوفرة")
    print()

    # سؤال المستخدم عن فتح المتصفح
    try:
        open_browser_choice = input("هل تريد فتح المتصفح تلقائياً؟ (y/n): ").lower().strip()
        if open_browser_choice in ['y', 'yes', 'نعم', '']:
            # تشغيل فتح المتصفح في خيط منفصل
            browser_thread = threading.Thread(target=open_browser, daemon=True)
            browser_thread.start()
    except KeyboardInterrupt:
        print("\n⏹️ تم الإلغاء")
        return

    # تشغيل الخادم
    start_api_server()

if __name__ == "__main__":
    main()

