#!/usr/bin/env python3
"""
اختبار سريع للعداد الزمني
Quick test for countdown timer
"""

import subprocess
import time
import webbrowser
import os
from threading import Thread

def start_api_server():
    """تشغيل خادم API"""
    try:
        print("بدء تشغيل خادم API...")
        subprocess.run(['python', 'api.py'], check=True)
    except KeyboardInterrupt:
        print("تم إيقاف الخادم")
    except Exception as e:
        print(f"خطأ في تشغيل الخادم: {e}")

def open_test_page():
    """فتح صفحة اختبار"""
    time.sleep(3)  # انتظار حتى يبدأ الخادم

    try:
        # اختبار API أولاً
        import requests
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ خادم API يعمل بشكل صحيح")

            # فتح صفحة HTML
            html_path = os.path.abspath('docs/index.html')
            if os.path.exists(html_path):
                print(f"فتح الصفحة: {html_path}")
                webbrowser.open(f"file://{html_path}")
            else:
                print("ملف index.html غير موجود")
        else:
            print("خادم API لا يستجيب")

    except Exception as e:
        print(f"خطأ في الاختبار: {e}")

def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("اختبار العداد الزمني للإشعارات")
    print("=" * 50)

    # فحص المتطلبات
    try:
        import flask
        import flask_cors
        print("✅ المتطلبات متوفرة")
    except ImportError as e:
        print(f"❌ مكتبة مفقودة: {e}")
        print("تشغيل: pip install -r requirements.txt")
        return

    # فحص ملف الإعدادات
    if not os.path.exists('config.json'):
        print("❌ ملف config.json غير موجود")
        return

    print("✅ ملف الإعدادات موجود")

    # تشغيل فتح الصفحة في خيط منفصل
    browser_thread = Thread(target=open_test_page, daemon=True)
    browser_thread.start()

    # تشغيل الخادم
    print("\n🚀 تشغيل الخادم...")
    print("📡 http://localhost:5000")
    print("⏹️ اضغط Ctrl+C للإيقاف")
    print("-" * 30)

    start_api_server()

if __name__ == "__main__":
    main()

