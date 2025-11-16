#!/bin/bash

# 🚀 سكريبت نشر نظام التنبيه الذكي للمزرعة على GitHub
# Farm Smart Notifier GitHub Deployment Script

set -e

echo "🚀 بدء عملية نشر نظام التنبيه الذكي للمزرعة..."
echo "Starting Farm Smart Notifier deployment process..."

# تحقق من وجود Git
if ! command -v git &> /dev/null; then
    echo "❌ Git غير مثبت. يرجى تثبيت Git أولاً."
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# تحقق من وجود gh CLI
if ! command -v gh &> /dev/null; then
    echo "⚠️ GitHub CLI غير مثبت. سأستخدم GitHub Web Interface بدلاً من ذلك."
    echo "⚠️ GitHub CLI is not installed. Will use GitHub Web Interface instead."
fi

# إنشاء Git repository إذا لم يكن موجوداً
if [ ! -d ".git" ]; then
    echo "📁 إنشاء Git repository..."
    echo "📁 Creating Git repository..."
    git init
    git branch -M main
fi

# التحقق من الملفات المطلوبة
required_files=("app.py" "requirements.txt" "telegram_notifier.py" "weather.py" ".github/workflows/farm-notifier.yml")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ] && [ ! -d "$file" ]; then
        echo "❌ الملف المطلوب غير موجود: $file"
        echo "❌ Required file not found: $file"
        exit 1
    fi
done

echo "✅ جميع الملفات المطلوبة موجودة."
echo "✅ All required files are present."

# إعداد git config إذا لم يكن محدداً
if [ -z "$(git config user.name)" ]; then
    echo "📝 إعداد معلومات المستخدم..."
    echo "📝 Setting up user information..."
    read -p "اسمك (Your name): " username
    read -p "إيميلك (Your email): " email
    git config user.name "$username"
    git config user.email "$email"
fi

# إضافة الملفات
echo "📁 إضافة الملفات إلى Git..."
echo "📁 Adding files to Git..."
git add .

# التحقق من وجود .env وتجنب إضافته
if [ -f ".env" ]; then
    echo "⚠️ تم العثور على ملف .env. سيتم تجاهله لأسباب أمنية."
    echo "⚠️ .env file found. It will be ignored for security reasons."
fi

# إنشاء commit
echo "💾 إنشاء commit..."
echo "💾 Creating commit..."
git commit -m "Initial commit: نظام التنبيه الذكي للمزرعة مع GitHub Actions
- Farm Smart Notifier with GitHub Actions
- دعم الإيموجيات والرسائل الثنائية اللغة
- Emoji support and bilingual messages
- تشغيل تلقائي كل 12 ساعة
- Automatic execution every 12 hours"

# التحقق من وجود remote origin
if git remote get-url origin &> /dev/null; then
    echo "✅ تم العثور على remote origin."
    echo "✅ Remote origin found."
else
    echo "📋 يحتاج repository جديد في GitHub:"
    echo "📋 New GitHub repository required:"
    echo ""
    echo "1. اذهب إلى: https://github.com/new"
    echo "   Go to: https://github.com/new"
    echo ""
    echo "2. أدخل اسم المشروع: farm-smart-notifier"
    echo "   Enter repository name: farm-smart-notifier"
    echo ""
    echo "3. لا تضف README أو .gitignore (لأنها موجودة بالفعل)"
    echo "   Don't add README or .gitignore (they already exist)"
    echo ""
    echo "4. إنشاء Repository الخاص"
    echo "   Create Private Repository"
    echo ""
    
    read -p "📋 URL الـ repository الجديد: " repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "✅ تم ربط الـ remote origin."
        echo "✅ Remote origin connected."
    fi
fi

# رفع المشروع
if git remote get-url origin &> /dev/null; then
    echo "🚀 رفع المشروع إلى GitHub..."
    echo "🚀 Uploading project to GitHub..."
    git push -u origin main
    echo "✅ تم رفع المشروع بنجاح!"
    echo "✅ Project uploaded successfully!"
    
    # إرشادات إضافية
    echo ""
    echo "🎯 الخطوات التالية:"
    echo "🎯 Next steps:"
    echo ""
    echo "1. اذهب إلى GitHub repository الذي أنشأته"
    echo "   Go to your created GitHub repository"
    echo ""
    echo "2. انقر على Settings > Secrets and variables > Actions"
    echo ""
    echo "3. أضف الـ 3 secrets التالية:"
    echo "   Add these 3 secrets:"
    echo ""
    echo "   📱 TELEGRAM_BOT_TOKEN = 8570871156:AAEuu5MCXstCTRBXNYyNXta7cxInWCIeHZM"
    echo "   📱 TELEGRAM_CHAT_ID = 1003443250446"
    echo "   🌤️ OPENWEATHER_API_KEY = dbe40b3b9ff7646fb726a1a1bde13aba"
    echo ""
    echo "4. اذهب إلى Actions tab وانقر على 'Run workflow' للاختبار"
    echo "   Go to Actions tab and click 'Run workflow' to test"
    echo ""
    echo "5. أضف البوت @DadFarmBot إلى مجموعة Telegram"
    echo "   Add bot @DadFarmBot to your Telegram group"
    echo ""
    echo "📖 راجع ملف GITHUB_DEPLOYMENT_GUIDE.md للتفاصيل الكاملة"
    echo "📖 See GITHUB_DEPLOYMENT_GUIDE.md for full details"
    
else
    echo "⚠️ لم يتم العثور على remote origin. يرجى ربط الـ repository أولاً."
    echo "⚠️ No remote origin found. Please connect your repository first."
fi

echo ""
echo "🎉 انتهت عملية النشر!"
echo "🎉 Deployment process completed!"