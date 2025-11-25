#!/usr/bin/env python3
"""
إنشاء ملف JSON للإشعارات القادمة للاستخدام على GitHub Pages
Generate notifications JSON file for GitHub Pages
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List

# استيراد منطق المزرعة
from logic import FarmLogic

class StaticNotificationGenerator:
    def __init__(self):
        self.logic = FarmLogic()

    def generate_notifications_json(self, days_ahead: int = 30) -> Dict:
        """إنشاء ملف JSON للإشعارات القادمة"""
        notifications = []
        today = date.today()

        for i in range(days_ahead):
            check_date = today + timedelta(days=i)
            day_notifications = self._get_notifications_for_date(check_date)
            notifications.extend(day_notifications)

        # ترتيب حسب التاريخ والوقت
        notifications.sort(key=lambda x: x['datetime'])

        # إنشاء بيانات العداد التنازلي
        countdown_data = self._generate_countdown_data(notifications)

        return {
            'generated_at': datetime.now().isoformat(),
            'notifications': notifications,
            'countdown': countdown_data,
            'total_count': len(notifications)
        }

    def _get_notifications_for_date(self, check_date: date) -> List[Dict]:
        """جلب إشعارات يوم محدد"""
        notifications = []

        # فحص دواء الديدان
        if self._should_deworm_on_date(check_date):
            drug = self._get_deworm_drug_for_date(check_date)
            notifications.append({
                'type': 'deworming',
                'title_ar': f'دواء الديدان - {drug}',
                'title_bn': f'কৃমির ঔষধ - {drug}',
                'date': check_date.isoformat(),
                'time': '08:00',
                'datetime': datetime.combine(check_date, datetime.strptime('08:00', '%H:%M').time()).isoformat(),
                'priority': 'high',
                'icon': '🪱',
                'drug': drug
            })

            # إضافة الفيتامينات بعد يوم من دواء الديدان
            next_day = check_date + timedelta(days=1)
            notifications.append({
                'type': 'vitamins',
                'title_ar': 'فيتامينات وإلكتروليت - دعم بعد دواء الديدان',
                'title_bn': 'ভিটামিন ও ইলেক্ট্রোলাইট - কৃমির ঔষধের পর সহায়তা',
                'date': next_day.isoformat(),
                'time': '08:30',
                'datetime': datetime.combine(next_day, datetime.strptime('08:30', '%H:%M').time()).isoformat(),
                'priority': 'medium',
                'icon': '💊',
                'reason_ar': 'دعم بعد دواء الديدان',
                'reason_bn': 'কৃমির ঔষধের পর সহায়তা'
            })

        # إضافة فيتامينات في حالات الطقس القاسي (مثال)
        if check_date.day % 15 == 0:  # كل 15 يوم كمثال
            notifications.append({
                'type': 'vitamins',
                'title_ar': 'فيتامينات وإلكتروليت - دعم وقائي',
                'title_bn': 'ভিটামিন ও ইলেক্ট্রোলাইট - প্রতিরোধমূলক সহায়তা',
                'date': check_date.isoformat(),
                'time': '09:00',
                'datetime': datetime.combine(check_date, datetime.strptime('09:00', '%H:%M').time()).isoformat(),
                'priority': 'medium',
                'icon': '💊',
                'reason_ar': 'دعم وقائي',
                'reason_bn': 'প্রতিরোধমূলক সহায়তা'
            })

        # إضافة الكوكسيديا في الأيام الرطبة (مثال)
        if check_date.day % 20 == 0:  # كل 20 يوم كمثال
            notifications.append({
                'type': 'coccidiosis',
                'title_ar': 'وقاية من الكوكسيديا - رطوبة عالية',
                'title_bn': 'কক্সিডিওসিস প্রতিরোধ - উচ্চ আর্দ্রতা',
                'date': check_date.isoformat(),
                'time': '09:30',
                'datetime': datetime.combine(check_date, datetime.strptime('09:30', '%H:%M').time()).isoformat(),
                'priority': 'high',
                'icon': '🦠',
                'reason_ar': 'رطوبة عالية',
                'reason_bn': 'উচ্চ আর্দ্রতা'
            })

        # فحص تطهير الحظيرة
        if self._should_sanitize_on_date(check_date):
            notifications.append({
                'type': 'sanitization',
                'title_ar': 'تطهير الحظيرة',
                'title_bn': 'খামার জীবাণুমুক্তকরণ',
                'date': check_date.isoformat(),
                'time': '09:00',
                'datetime': datetime.combine(check_date, datetime.strptime('09:00', '%H:%M').time()).isoformat(),
                'priority': 'medium',
                'icon': '🧹'
            })

        # فحص تنظيف محطة الماء
        if self._should_clean_water_station_on_date(check_date):
            notifications.append({
                'type': 'water_station',
                'title_ar': 'تنظيف محطة الماء',
                'title_bn': 'পানি স্টেশন পরিষ্কার',
                'date': check_date.isoformat(),
                'time': '10:00',
                'datetime': datetime.combine(check_date, datetime.strptime('10:00', '%H:%M').time()).isoformat(),
                'priority': 'medium',
                'icon': '💧'
            })

        # فحص التنظيف الأسبوعي
        if self._should_clean_weekly_on_date(check_date):
            notifications.append({
                'type': 'weekly_cleaning',
                'title_ar': 'التنظيف الأسبوعي',
                'title_bn': 'সাপ্তাহিক পরিষ্কার',
                'date': check_date.isoformat(),
                'time': '11:00',
                'datetime': datetime.combine(check_date, datetime.strptime('11:00', '%H:%M').time()).isoformat(),
                'priority': 'medium',
                'icon': '🧽'
            })

        # فحص تقليب التراب
        if self._should_turn_soil_on_date(check_date):
            notifications.append({
                'type': 'soil_turning',
                'title_ar': 'تقليب التراب',
                'title_bn': 'মাটি নাড়াচাড়া',
                'date': check_date.isoformat(),
                'time': '12:00',
                'datetime': datetime.combine(check_date, datetime.strptime('12:00', '%H:%M').time()).isoformat(),
                'priority': 'low',
                'icon': '🌱'
            })

        # فحص التهوية
        if self._should_check_ventilation_on_date(check_date):
            notifications.append({
                'type': 'ventilation',
                'title_ar': 'فحص التهوية',
                'title_bn': 'বায়ুচলাচল পরীক্ষা',
                'date': check_date.isoformat(),
                'time': '13:00',
                'datetime': datetime.combine(check_date, datetime.strptime('13:00', '%H:%M').time()).isoformat(),
                'priority': 'medium',
                'icon': '💨'
            })

        # فحص غسيل المعالف
        if self._should_clean_feeders_on_date(check_date):
            notifications.append({
                'type': 'feeder_cleaning',
                'title_ar': 'غسيل المعالف',
                'title_bn': 'খাবার পাত্র পরিষ্কার',
                'date': check_date.isoformat(),
                'time': '14:00',
                'datetime': datetime.combine(check_date, datetime.strptime('14:00', '%H:%M').time()).isoformat(),
                'priority': 'medium',
                'icon': '🪣'
            })

        # فحص السقاية الأنبوبية
        pipe_tasks = self._get_pipe_waterer_tasks_for_date(check_date)
        for task in pipe_tasks:
            notifications.append({
                'type': f'pipe_waterer_{task}',
                'title_ar': f'السقاية الأنبوبية - {self._get_pipe_task_name_ar(task)}',
                'title_bn': f'পাইপ ওয়াটারার - {self._get_pipe_task_name_bn(task)}',
                'date': check_date.isoformat(),
                'time': '15:00',
                'datetime': datetime.combine(check_date, datetime.strptime('15:00', '%H:%M').time()).isoformat(),
                'priority': 'medium',
                'icon': '🚰'
            })

        # فحص تسميد الأشجار
        fertilizer_tasks = self._get_fertilizer_tasks_for_date(check_date)
        for task in fertilizer_tasks:
            notifications.append({
                'type': 'fertilizer',
                'title_ar': f'تسميد {task["tree_name_ar"]}',
                'title_bn': f'{task["tree_name_bn"]} সার প্রয়োগ',
                'date': check_date.isoformat(),
                'time': '16:00',
                'datetime': datetime.combine(check_date, datetime.strptime('16:00', '%H:%M').time()).isoformat(),
                'priority': 'medium',
                'icon': '🌳',
                'tree': task['tree_key'],
                'fertilizer': task['fertilizer']
            })

        return notifications

    def _generate_countdown_data(self, notifications: List[Dict]) -> Dict:
        """إنشاء بيانات العداد التنازلي"""
        if not notifications:
            return {
                'next_notification': None,
                'message_ar': 'لا توجد إشعارات مجدولة خلال الشهر القادم',
                'message_bn': 'আগামী মাসে কোনো বিজ্ঞপ্তি নির্ধারিত নেই'
            }

        now = datetime.now()

        # البحث عن أول إشعار في المستقبل
        future_notifications = [
            n for n in notifications
            if datetime.fromisoformat(n['datetime']) > now
        ]

        if not future_notifications:
            return {
                'next_notification': None,
                'message_ar': 'لا توجد إشعارات قادمة',
                'message_bn': 'কোনো আসন্ন বিজ্ঞপ্তি নেই'
            }

        next_notification = future_notifications[0]
        target_time = datetime.fromisoformat(next_notification['datetime'])
        time_diff = target_time - now

        total_seconds = int(time_diff.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return {
            'next_notification': next_notification,
            'countdown': {
                'total_seconds': max(0, total_seconds),
                'days': max(0, days),
                'hours': max(0, hours),
                'minutes': max(0, minutes),
                'seconds': max(0, seconds)
            },
            'current_time': now.isoformat()
        }

    # نسخ الدوال المساعدة من api.py
    def _should_deworm_on_date(self, check_date: date) -> bool:
        try:
            check_date_str = check_date.strftime("%m-%d")
            deworming_config = self.logic.config['chicken_schedule']['deworming']
            seasonal_schedule = deworming_config.get('seasonal_schedule', [])

            for schedule_item in seasonal_schedule:
                if schedule_item['date'] == check_date_str:
                    return True
            return False
        except:
            return False

    def _get_deworm_drug_for_date(self, check_date: date) -> str:
        try:
            check_date_str = check_date.strftime("%m-%d")
            deworming_config = self.logic.config['chicken_schedule']['deworming']
            seasonal_schedule = deworming_config.get('seasonal_schedule', [])

            for schedule_item in seasonal_schedule:
                if schedule_item['date'] == check_date_str:
                    return schedule_item['drug']
            return "Fenbendazole"
        except:
            return "Fenbendazole"

    def _should_sanitize_on_date(self, check_date: date) -> bool:
        try:
            start_date_str = self.logic.config['chicken_schedule']['sanitization']['start_date']
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            interval = self.logic.config['chicken_schedule']['sanitization']['interval_days']

            days_diff = (check_date - start_date).days
            return days_diff >= 0 and days_diff % interval == 0
        except:
            return False

    def _should_clean_water_station_on_date(self, check_date: date) -> bool:
        try:
            config = self.logic.config['chicken_schedule'].get('water_station', {})
            if not config:
                return False

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (check_date - start_date).days

            return days_diff >= 0 and days_diff % interval == 0
        except:
            return False

    def _should_clean_weekly_on_date(self, check_date: date) -> bool:
        try:
            config = self.logic.config['chicken_schedule'].get('weekly_cleaning', {})
            if not config:
                return False

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (check_date - start_date).days

            return days_diff >= 0 and days_diff % interval == 0
        except:
            return False

    def _should_turn_soil_on_date(self, check_date: date) -> bool:
        try:
            config = self.logic.config['chicken_schedule'].get('soil_turning', {})
            if not config:
                return False

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (check_date - start_date).days

            return days_diff >= 0 and days_diff % interval == 0
        except:
            return False

    def _should_check_ventilation_on_date(self, check_date: date) -> bool:
        try:
            config = self.logic.config['chicken_schedule'].get('ventilation', {})
            if not config:
                return False

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (check_date - start_date).days

            return days_diff >= 0 and days_diff % interval == 0
        except:
            return False

    def _should_clean_feeders_on_date(self, check_date: date) -> bool:
        try:
            config = self.logic.config['chicken_schedule'].get('feeder_cleaning', {})
            if not config:
                return False

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (check_date - start_date).days

            return days_diff >= 0 and days_diff % interval == 0
        except:
            return False

    def _get_pipe_waterer_tasks_for_date(self, check_date: date) -> List[str]:
        tasks = []
        try:
            config = self.logic.config['chicken_schedule'].get('pipe_waterer', {})
            if not config:
                return []

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            intervals = config.get('intervals', {})
            days_diff = (check_date - start_date).days

            if days_diff < 0:
                return []

            if days_diff % intervals.get('deep_clean', 30) == 0:
                tasks.append('deep_clean')
            elif days_diff % intervals.get('sanitize', 15) == 0:
                tasks.append('sanitize')
            elif days_diff % intervals.get('rinse', 7) == 0:
                tasks.append('rinse')
            elif days_diff % intervals.get('change_water', 3) == 0:
                tasks.append('change_water')

            return tasks
        except:
            return []

    def _get_pipe_task_name_ar(self, task: str) -> str:
        names = {
            'change_water': 'تغيير الماء',
            'rinse': 'شطف',
            'sanitize': 'تعقيم',
            'deep_clean': 'تنظيف عميق'
        }
        return names.get(task, task)

    def _get_pipe_task_name_bn(self, task: str) -> str:
        names = {
            'change_water': 'পানি পরিবর্তন',
            'rinse': 'ধোয়া',
            'sanitize': 'জীবাণুমুক্তকরণ',
            'deep_clean': 'গভীর পরিষ্কার'
        }
        return names.get(task, task)

    def _get_fertilizer_tasks_for_date(self, check_date: date) -> List[Dict]:
        tasks = []
        try:
            tree_names_ar = {
                'henna': 'الحناء', 'fig': 'التين', 'banana': 'الموز',
                'mango_small': 'مانجو صغيرة', 'mango_large': 'مانجو كبيرة',
                'jackfruit_young': 'جاك فروت صغير', 'mint_basil': 'النعناع والحبق',
                'pomegranate': 'الرمان', 'acacia': 'الأكاسيا', 'bougainvillea': 'الجهنمية',
                'grape': 'العنب', 'custard_apple': 'القشطة', 'ornamental': 'أشجار الزينة',
                'moringa': 'المورينجا'
            }

            tree_names_bn = {
                'henna': 'মেহেদি', 'fig': 'ডুমুর', 'banana': 'কলা',
                'mango_small': 'ছোট আম', 'mango_large': 'বড় আম',
                'jackfruit_young': 'ছোট কাঁঠাল', 'mint_basil': 'পুদিনা ও তুলসী',
                'pomegranate': 'ডালিম', 'acacia': 'বাবলা', 'bougainvillea': 'বাগানবিলাস',
                'grape': 'আঙ্গুর', 'custard_apple': 'আতা', 'ornamental': 'শোভাবর্ধনকারী গাছ',
                'moringa': 'সজনে'
            }

            # إضافة جدولة تسميد مبسطة للأشجار
            fertilizer_schedule = {
                'henna': {'interval': 45, 'fertilizer': 'NPK 20-20-20'},
                'fig': {'interval': 60, 'fertilizer': 'NPK متوازن'},
                'banana': {'interval': 30, 'fertilizer': 'NPK 30-10-10'},
                'mango_small': {'interval': 90, 'fertilizer': 'NPK 20-20-20'},
                'mango_large': {'interval': 75, 'fertilizer': 'NPK 15-15-15'},
                'pomegranate': {'interval': 80, 'fertilizer': 'NPK 15-15-15'},
                'grape': {'interval': 70, 'fertilizer': 'NPK 12-12-17'},
                'jackfruit_young': {'interval': 120, 'fertilizer': 'NPK 20-20-20'},
                'acacia': {'interval': 180, 'fertilizer': 'Organic'},
                'bougainvillea': {'interval': 50, 'fertilizer': 'High Phosphorus'},
                'mint_basil': {'interval': 25, 'fertilizer': 'NPK 20-20-20'},
                'moringa': {'interval': 90, 'fertilizer': 'Low Nitrogen'},
                'custard_apple': {'interval': 18, 'fertilizer': 'NPK 20-20-20'}  # تم تحديثها من 150 إلى 18 يوماً
            }

            # فحص كل شجرة
            base_date = date(2025, 11, 1)  # تاريخ البداية
            for tree_key, schedule in fertilizer_schedule.items():
                days_diff = (check_date - base_date).days
                if days_diff >= 0 and days_diff % schedule['interval'] == 0:
                    tasks.append({
                        'tree_key': tree_key,
                        'tree_name_ar': tree_names_ar.get(tree_key, tree_key),
                        'tree_name_bn': tree_names_bn.get(tree_key, tree_key),
                        'fertilizer': schedule['fertilizer']
                    })

            return tasks
        except Exception as e:
            print(f"خطأ في جلب مهام التسميد: {e}")
            return []

def main():
    """الدالة الرئيسية"""
    print("إنشاء ملف الإشعارات للاستخدام على GitHub Pages...")

    try:
        generator = StaticNotificationGenerator()
        data = generator.generate_notifications_json()

        # حفظ الملف في مجلد docs
        output_file = 'docs/notifications.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"تم إنشاء {output_file} بنجاح!")
        print(f"عدد الإشعارات: {data['total_count']}")

        if data['countdown']['next_notification']:
            next_notif = data['countdown']['next_notification']
            print(f"الإشعار القادم: {next_notif['title_ar']}")
            print(f"التاريخ: {next_notif['date']} في {next_notif['time']}")
        else:
            print("لا توجد إشعارات قادمة")

    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    main()
