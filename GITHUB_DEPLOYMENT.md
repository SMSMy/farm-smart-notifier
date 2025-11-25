# رفع العداد الزمني على GitHub | GitHub Deployment Guide

## 🚀 رفع المشروع على GitHub

### الخطوة 1: إعداد المشروع للرفع

```bash
# إنشاء .gitignore
echo "__pycache__/" > .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo ".last_run" >> .gitignore
echo ".feed_changed_today" >> .gitignore
echo "terminals/" >> .gitignore

# إضافة الملفات
git add .
git commit -m "إضافة العداد الزمني للإشعارات"
git push origin main
```

### الخطوة 2: تفعيل GitHub Pages

1. اذهب إلى **Settings** في مستودع GitHub
2. اختر **Pages** من القائمة الجانبية
3. في **Source** اختر **Deploy from a branch**
4. اختر **main** branch و **/docs** folder
5. اضغط **Save**

### الخطوة 3: تحديث عنوان API

بعد رفع المشروع، ستحتاج لتحديث عنوان API في الملفات:

```javascript
// في docs/countdown-timer.js
apiUrl: 'https://your-username.github.io/farm-notifier/api'
```

## 🔄 التزامن مع إشعارات التليجرام

### الوضع الحالي:
العداد الزمني **يتزامن تماماً** مع نظام التليجرام لأنه:

1. **يستخدم نفس ملف الإعدادات** (`config.json`)
2. **يستخدم نفس منطق الحساب** (`logic.py`)
3. **يحسب نفس المواعيد** التي يرسلها التليجرام

### كيف يعمل التزامن:

```python
# في api.py - نفس منطق app.py
from logic import FarmLogic

# نفس الفحوصات المستخدمة في التليجرام
logic.should_deworm_today()
logic.should_sanitize_coop()
logic.get_all_fertilization_tasks()
```

### مثال على التزامن:

| الوقت | التليجرام | العداد الزمني |
|-------|-----------|---------------|
| 2025-02-15 | يرسل إشعار دواء الديدان | يعرض "0 أيام متبقية" |
| 2025-02-14 | لا يرسل شيء | يعرض "1 يوم متبقي" |
| 2025-02-13 | لا يرسل شيء | يعرض "2 أيام متبقية" |

## 🌐 للعمل على GitHub Pages

### المشكلة:
GitHub Pages لا يدعم Python/Flask مباشرة.

### الحلول:

#### الحل 1: API ثابت (مُوصى به)
إنشاء ملف JSON ثابت يحدث دورياً:

```javascript
// بدلاً من API حي، استخدام ملف JSON
fetch('notifications.json')
  .then(response => response.json())
  .then(data => updateCountdown(data));
```

#### الحل 2: GitHub Actions
استخدام GitHub Actions لتحديث البيانات:

```yaml
# .github/workflows/update-notifications.yml
name: Update Notifications
on:
  schedule:
    - cron: '0 */6 * * *'  # كل 6 ساعات
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate notifications
        run: python generate_notifications.py
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/notifications.json
          git commit -m "تحديث الإشعارات" || exit 0
          git push
```

#### الحل 3: خدمة خارجية
استخدام خدمات مثل Heroku أو Vercel للـ API.

## 📝 سأقوم بإعداد الحل الأول الآن

دعني أنشئ نسخة تعمل على GitHub Pages:

