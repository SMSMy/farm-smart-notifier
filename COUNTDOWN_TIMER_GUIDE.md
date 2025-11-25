# دليل العداد الزمني للإشعارات | Countdown Timer Guide

## نظرة عامة | Overview

تم إضافة عداد زمني تفاعلي لصفحات HTML يعرض الوقت المتبقي حتى الإشعار التالي بناءً على جدولة التليجرام.

An interactive countdown timer has been added to HTML pages showing time remaining until the next notification based on Telegram scheduling.

## المكونات الجديدة | New Components

### 1. خادم API | API Server
- **الملف**: `api.py`
- **الوظيفة**: يوفر endpoints لجلب بيانات الإشعارات القادمة
- **المنافذ**:
  - `/api/notifications/countdown` - بيانات العداد التنازلي
  - `/api/notifications/today` - إشعارات اليوم
  - `/api/notifications/next` - الإشعارات القادمة
  - `/api/health` - فحص صحة الخادم

### 2. مكون JavaScript | JavaScript Component
- **الملف**: `docs/countdown-timer.js`
- **الوظيفة**: عداد زمني تفاعلي مع دعم اللغتين العربية والبنغالية
- **المميزات**:
  - تحديث تلقائي كل ثانية
  - تصميم متجاوب
  - دعم ثنائي اللغة
  - معالجة الأخطاء

### 3. ملف التشغيل | Launcher Script
- **الملف**: `start_server.py`
- **الوظيفة**: تشغيل الخادم مع فحص المتطلبات

## طريقة التشغيل | How to Run

### الخطوة 1: تثبيت المتطلبات | Step 1: Install Requirements
```bash
pip install -r requirements.txt
```

### الخطوة 2: تشغيل الخادم | Step 2: Start Server
```bash
python start_server.py
```

أو مباشرة:
```bash
python api.py
```

### الخطوة 3: فتح الصفحات | Step 3: Open Pages
افتح `docs/index.html` في المتصفح وستجد العداد الزمني في أعلى الصفحة.

Open `docs/index.html` in browser and you'll see the countdown timer at the top of the page.

## API Endpoints

### 1. العداد التنازلي | Countdown Data
```
GET /api/notifications/countdown
```

**الاستجابة | Response:**
```json
{
  "success": true,
  "next_notification": {
    "type": "deworming",
    "title_ar": "دواء الديدان - Fenbendazole",
    "title_bn": "কৃমির ঔষধ - Fenbendazole",
    "date": "2025-12-15",
    "time": "08:00",
    "datetime": "2025-12-15T08:00:00",
    "priority": "high",
    "icon": "🪱"
  },
  "countdown": {
    "total_seconds": 86400,
    "days": 1,
    "hours": 0,
    "minutes": 0,
    "seconds": 0
  },
  "current_time": "2025-12-14T08:00:00"
}
```

### 2. إشعارات اليوم | Today's Notifications
```
GET /api/notifications/today
```

### 3. الإشعارات القادمة | Upcoming Notifications
```
GET /api/notifications/next?days=30
```

### 4. فحص الصحة | Health Check
```
GET /api/health
```

## التخصيص | Customization

### تغيير عنوان API | Change API URL
في `docs/countdown-timer.js`:
```javascript
window.farmCountdown = new FarmNotifierCountdown({
    language: currentLang,
    apiUrl: 'http://your-server:5000/api'  // غير هذا العنوان
});
```

### تخصيص التصميم | Customize Styling
يمكن تعديل CSS في `docs/countdown-timer.js` في دالة `addStyles()`.

### إضافة العداد لصفحات أخرى | Add Timer to Other Pages
1. أضف `<script src="countdown-timer.js" defer></script>` في `<head>`
2. أضف `<div id="countdown-container"></div>` حيث تريد ظهور العداد

## الجدولة المدعومة | Supported Schedules

العداد يدعم جميع أنواع الإشعارات المجدولة في `config.json`:

- **دواء الديدان** | Deworming (موسمي | seasonal)
- **تطهير الحظيرة** | Sanitization (كل 60 يوم | every 60 days)
- **تنظيف محطة الماء** | Water station cleaning (كل 14 يوم | every 14 days)
- **السقاية الأنبوبية** | Pipe waterer maintenance (متعدد الفترات | multiple intervals)
- **التنظيف الأسبوعي** | Weekly cleaning (كل 7 أيام | every 7 days)
- **تقليب التراب** | Soil turning (كل 7 أيام | every 7 days)
- **فحص التهوية** | Ventilation check (كل 7 أيام | every 7 days)
- **غسيل المعالف** | Feeder cleaning (كل 14 يوم | every 14 days)
- **تسميد الأشجار** | Tree fertilization (حسب التواريخ والمواسم | by dates and seasons)

## استكشاف الأخطاء | Troubleshooting

### العداد لا يظهر | Timer Not Showing
1. تأكد من تشغيل خادم API
2. افحص console في المتصفح للأخطاء
3. تأكد من صحة عنوان API

### خطأ CORS | CORS Error
تأكد من أن `Flask-CORS` مثبت:
```bash
pip install Flask-CORS
```

### بيانات خاطئة | Wrong Data
1. افحص `config.json` للتأكد من صحة التواريخ
2. تأكد من تطابق المنطق في `logic.py` و `api.py`

## الأمان | Security

⚠️ **تحذير**: هذا الخادم مخصص للاستخدام المحلي فقط. لا تعرضه على الإنترنت بدون تأمين إضافي.

⚠️ **Warning**: This server is for local use only. Don't expose it to the internet without additional security.

## التطوير المستقبلي | Future Development

- [ ] إضافة إشعارات المتصفح
- [ ] حفظ الحالة في localStorage
- [ ] دعم المناطق الزمنية
- [ ] واجهة إدارة الجدولة
- [ ] تصدير التقويم
- [ ] تكامل مع تطبيقات التقويم

---

**تم التطوير بواسطة**: Claude Sonnet 4
**التاريخ**: نوفمبر 2025
**الإصدار**: 1.0.0

