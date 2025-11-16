#!/usr/bin/env python3
"""
Setup script for Farm Smart Notifier System
"""

from setuptools import setup, find_packages
import os

# قراءة المتطلبات من requirements.txt
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# قراءة README
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="farm-smart-notifier",
    version="1.0.0",
    description="نظام تنبيه ذكي لإدارة المزرعة - دواء الدجاج وتسميد الأشجار",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="MiniMax Agent",
    author_email="farm@example.com",
    url="https://github.com/your-username/farm-notifier",
    packages=find_packages(),
    py_modules=[
        "app",
        "weather", 
        "logic",
        "telegram_notifier"
    ],
    install_requires=read_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Agriculture",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Agriculture",
    ],
    keywords="farming agriculture automation telegram weather scheduling",
    entry_points={
        "console_scripts": [
            "farm-notifier=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yml", "*.yaml", "*.md"],
        "images": ["*.jpg", "*.png", "*.jpeg", "*.webp"],
    },
    data_files=[
        ("", ["config.json", "requirements.txt", ".env.example"]),
        ("images", ["images/deworming.jpg", "images/vitamins.png", "images/coccidia.jpg", 
                    "images/sanitizer.png", "images/fertilizer.png"]),
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/farm-notifier/issues",
        "Source": "https://github.com/your-username/farm-notifier",
        "Documentation": "https://github.com/your-username/farm-notifier#readme",
    },
)

# رسالة ما بعد التثبيت
print("""
🌱 تم تثبيت نظام التنبيه الذكي للمزرعة بنجاح!

📋 الخطوات التالية:
1. انسخ .env.example إلى .env وأدخل التوكنات
2. حدث config.json حسب احتياجاتك
3. اختبر النظام: python main.py test
4. للاستخدام التلقائي: اضبط GitHub Actions

💡 للمساعدة: python main.py help
""")