#!/usr/bin/env python3
"""
API لجلب أوقات الإشعارات القادمة للعداد الزمني
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS

# إضافة المجلد الحالي إلى المسار
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logic import FarmLogic
from weather import WeatherFetcher

app = Flask(__name__)
CORS(app)  # للسماح بطلبات من صفحات HTML

class NotificationScheduler:
    def __init__(self):
        self.logic = FarmLogic()

    def get_next_notifications(self, days_ahead: int = 30) -> List[Dict]:
        """جلب الإشعارات القادمة خلال فترة محددة"""
        notifications = []
        today = date.today()

        for i in range(days_ahead):
            check_date = today + timedelta(days=i)
            day_notifications = self._get_notifications_for_date(check_date)
            notifications.extend(day_notifications)

        # ترتيب حسب التاريخ والوقت
        notifications.sort(key=lambda x: x['datetime'])
        return notifications

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
                'time': '08:00',  # وقت افتراضي
                'datetime': datetime.combine(check_date, datetime.strptime('08:00', '%H:%M').time()),
                'priority': 'high',
                'icon': '🪱'
            })

        # فحص تطهير الحظيرة
        if self._should_sanitize_on_date(check_date):
            notifications.append({
                'type': 'sanitization',
                'title_ar': 'تطهير الحظيرة',
                'title_bn': 'খামার জীবাণুমুক্তকরণ',
                'date': check_date.isoformat(),
                'time': '09:00',
                'datetime': datetime.combine(check_date, datetime.strptime('09:00', '%H:%M').time()),
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
                'datetime': datetime.combine(check_date, datetime.strptime('10:00', '%H:%M').time()),
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
                'datetime': datetime.combine(check_date, datetime.strptime('11:00', '%H:%M').time()),
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
                'datetime': datetime.combine(check_date, datetime.strptime('12:00', '%H:%M').time()),
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
                'datetime': datetime.combine(check_date, datetime.strptime('13:00', '%H:%M').time()),
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
                'datetime': datetime.combine(check_date, datetime.strptime('14:00', '%H:%M').time()),
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
                'datetime': datetime.combine(check_date, datetime.strptime('15:00', '%H:%M').time()),
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
                'datetime': datetime.combine(check_date, datetime.strptime('16:00', '%H:%M').time()),
                'priority': 'medium',
                'icon': '🌳',
                'tree': task['tree_key'],
                'fertilizer': task['fertilizer']
            })

        return notifications

    def _should_deworm_on_date(self, check_date: date) -> bool:
        """فحص دواء الديدان لتاريخ محدد"""
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
        """جلب دواء الديدان لتاريخ محدد"""
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
        """فحص تطهير الحظيرة لتاريخ محدد"""
        try:
            start_date_str = self.logic.config['chicken_schedule']['sanitization']['start_date']
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            interval = self.logic.config['chicken_schedule']['sanitization']['interval_days']

            days_diff = (check_date - start_date).days
            return days_diff >= 0 and days_diff % interval == 0
        except:
            return False

    def _should_clean_water_station_on_date(self, check_date: date) -> bool:
        """فحص تنظيف محطة الماء لتاريخ محدد"""
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
        """فحص التنظيف الأسبوعي لتاريخ محدد"""
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
        """فحص تقليب التراب لتاريخ محدد"""
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
        """فحص التهوية لتاريخ محدد"""
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
        """فحص غسيل المعالف لتاريخ محدد"""
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
        """جلب مهام السقاية الأنبوبية لتاريخ محدد"""
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

            # فحص كل نوع صيانة (بنفس ترتيب الأولوية في logic.py)
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
        """أسماء مهام السقاية بالعربية"""
        names = {
            'change_water': 'تغيير الماء',
            'rinse': 'شطف',
            'sanitize': 'تعقيم',
            'deep_clean': 'تنظيف عميق'
        }
        return names.get(task, task)

    def _get_pipe_task_name_bn(self, task: str) -> str:
        """أسماء مهام السقاية بالبنغالية"""
        names = {
            'change_water': 'পানি পরিবর্তন',
            'rinse': 'ধোয়া',
            'sanitize': 'জীবাণুমুক্তকরণ',
            'deep_clean': 'গভীর পরিষ্কার'
        }
        return names.get(task, task)

    def _get_fertilizer_tasks_for_date(self, check_date: date) -> List[Dict]:
        """جلب مهام التسميد لتاريخ محدد"""
        tasks = []
        try:
            trees_schedule = self.logic.config.get('trees_fertilizer_schedule', {})

            # أسماء الأشجار
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

            for tree_key, tree_config in trees_schedule.items():
                should_fertilize = False

                # فحص التواريخ المحددة
                if 'dates' in tree_config:
                    check_date_str = check_date.strftime("%Y-%m-%d")
                    if check_date_str in tree_config['dates']:
                        should_fertilize = True

                # فحص المواسم (مبسط - يحتاج تحسين)
                elif 'seasons' in tree_config:
                    # هنا يمكن إضافة منطق فحص المواسم
                    # للبساطة، سنفحص فقط التواريخ المحددة
                    pass

                if should_fertilize:
                    fertilizer = tree_config.get('fertilizer', 'غير محدد')
                    if 'fertilizers' in tree_config:
                        # اختيار السماد الأول للبساطة
                        fertilizer = tree_config['fertilizers'][0]

                    tasks.append({
                        'tree_key': tree_key,
                        'tree_name_ar': tree_names_ar.get(tree_key, tree_key),
                        'tree_name_bn': tree_names_bn.get(tree_key, tree_key),
                        'fertilizer': fertilizer
                    })

            return tasks
        except:
            return []

# إنشاء مثيل من المجدول
scheduler = NotificationScheduler()

@app.route('/api/notifications/next', methods=['GET'])
def get_next_notifications():
    """API لجلب الإشعارات القادمة"""
    try:
        days_ahead = request.args.get('days', 30, type=int)
        notifications = scheduler.get_next_notifications(days_ahead)

        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/notifications/today', methods=['GET'])
def get_today_notifications():
    """API لجلب إشعارات اليوم"""
    try:
        today = date.today()
        notifications = scheduler._get_notifications_for_date(today)

        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications),
            'date': today.isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/notifications/countdown', methods=['GET'])
def get_countdown_data():
    """API لجلب بيانات العداد التنازلي"""
    try:
        notifications = scheduler.get_next_notifications(7)  # أسبوع قادم

        if not notifications:
            return jsonify({
                'success': True,
                'next_notification': None,
                'message_ar': 'لا توجد إشعارات مجدولة خلال الأسبوع القادم',
                'message_bn': 'আগামী সপ্তাহে কোনো বিজ্ঞপ্তি নির্ধারিত নেই'
            })

        next_notification = notifications[0]
        now = datetime.now()
        time_diff = next_notification['datetime'] - now

        # حساب الوقت المتبقي
        if time_diff.total_seconds() <= 0:
            # الإشعار قد مضى، ابحث عن التالي
            future_notifications = [n for n in notifications if n['datetime'] > now]
            if future_notifications:
                next_notification = future_notifications[0]
                time_diff = next_notification['datetime'] - now
            else:
                return jsonify({
                    'success': True,
                    'next_notification': None,
                    'message_ar': 'لا توجد إشعارات قادمة',
                    'message_bn': 'কোনো আসন্ন বিজ্ঞপ্তি নেই'
                })

        total_seconds = int(time_diff.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return jsonify({
            'success': True,
            'next_notification': next_notification,
            'countdown': {
                'total_seconds': total_seconds,
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            },
            'current_time': now.isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص صحة API"""
    return jsonify({
        'success': True,
        'message': 'Farm Notifier API is running',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("بدء تشغيل Farm Notifier API...")
    print("API متاح على: http://localhost:5000")
    print("العداد التنازلي: http://localhost:5000/api/notifications/countdown")
    app.run(debug=True, host='0.0.0.0', port=5000)
