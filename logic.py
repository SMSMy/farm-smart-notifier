from datetime import datetime, date, timedelta
import json
import os
from typing import Dict, List, Optional, Any

class FarmLogic:
    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)
        self.last_run_file = '.last_run'

    def _load_config(self, path: str) -> Dict:
        """تحميل ملف الإعدادات"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"[Logic] تم تحميل الإعدادات من {path}")
                return config
        except FileNotFoundError:
            raise Exception(f"ملف {path} غير موجود!")
        except json.JSONDecodeError as e:
            raise Exception(f"خطأ في تحليل ملف الإعدادات: {e}")

    def is_date_in_season(self, season_name: str, check_date: Optional[date] = None) -> bool:
        """هل التاريخ داخل الموسم؟"""
        if check_date is None:
            check_date = date.today()

        season_ranges = self.config['seasons'].get(season_name, [])

        for start_str, end_str in season_ranges:
            try:
                start = datetime.strptime(start_str, "%Y-%m-%d").date()
                end = datetime.strptime(end_str, "%Y-%m-%d").date()

                if start <= check_date <= end:
                    return True
            except ValueError as e:
                print(f"⚠️ خطأ في تحليل تواريخ الموسم {season_name}: {e}")
                continue

        return False

    def should_deworm_today(self) -> bool:
        """هل اليوم هو أحد المواعيد الموسمية المحددة لدواء الديدان؟"""
        try:
            today = date.today()
            today_str = today.strftime("%m-%d")

            deworming_config = self.config['chicken_schedule']['deworming']
            seasonal_schedule = deworming_config.get('seasonal_schedule', [])

            # البحث عن موعد اليوم في الجدول الموسمي
            for schedule_item in seasonal_schedule:
                if schedule_item['date'] == today_str:
                    drug = schedule_item['drug']
                    print(f"[Logic] موعد دواء الديدان اليوم - الدواء: {drug}")
                    return True

            return False

        except Exception as e:
            print(f"❌ خطأ في حساب دواء الديدان: {e}")
            return False

    def get_current_deworm_drug(self) -> str:
        """يعيد الدواء المحدد لليوم الحالي من الجدول الموسمي"""
        try:
            today = date.today()
            today_str = today.strftime("%m-%d")

            deworming_config = self.config['chicken_schedule']['deworming']
            seasonal_schedule = deworming_config.get('seasonal_schedule', [])

            # البحث عن الدواء المطابق لاليوم
            for schedule_item in seasonal_schedule:
                if schedule_item['date'] == today_str:
                    drug = schedule_item['drug']
                    print(f"[Logic] الدواء الحالي: {drug}")
                    return drug

            # إذا لم يوجد، إرجع الدواء الأول (قيمة افتراضية)
            if seasonal_schedule:
                default_drug = seasonal_schedule[0]['drug']
                print(f"[Logic] لم يوجد دواء لليوم، الدواء الافتراضي: {default_drug}")
                return default_drug

            return "Fenbendazole"  # قيمة افتراضية نهائية

        except Exception as e:
            print(f"❌ خطأ في اختيار الدواء: {e}")
            return "Fenbendazole"

    def should_fertilize_tree(self, tree_key: str, weather_report: Optional[Dict] = None) -> bool:
        """هل يجب تسميد الشجرة اليوم؟"""
        try:
            tree = self.config['trees_fertilizer_schedule'].get(tree_key)
            if not tree:
                print(f"⚠️ شجرة {tree_key} غير موجودة في الإعدادات")
                return False

            print(f"[Logic] فحص تسميد {tree_key}...")

            # شرط 1: الفاصل الزمني (Interval)
            date_ok = False
            if 'start_date' in tree and 'interval_days' in tree:
                start_date = datetime.strptime(tree['start_date'], "%Y-%m-%d").date()
                interval = tree['interval_days']
                days_diff = (date.today() - start_date).days

                if days_diff >= 0 and days_diff % interval == 0:
                    date_ok = True
                    print(f"[Logic] {tree_key} موعد التسميد الدوري (كل {interval} يوم)")

            # دعم التواريخ المحددة يدوياً (Legacy)
            elif 'dates' in tree:
                today_str = date.today().strftime("%Y-%m-%d")
                if today_str in tree['dates']:
                    date_ok = True
                    print(f"[Logic] {tree_key} في التاريخ المحدد: {today_str}")

            # شرط 2: ظروف الطقس
            weather_ok = True
            if weather_report and not weather_report.get('good_fertilizer_time', True):
                weather_ok = False
                print(f"[Logic] طقس غير مناسب للتسميد")

            # شرط 3: درجة الحرارة القصوى
            temp_ok = True
            if 'max_temp' in tree and weather_report:
                max_temp = weather_report.get('max_temp_48h', 0)
                if max_temp > tree['max_temp']:
                    temp_ok = False
                    print(f"[Logic] درجة الحرارة {max_temp}°C أعلى من الحد المسموح {tree['max_temp']}°C")

            # نتيجة نهائية
            result = date_ok and weather_ok and temp_ok

            if result:
                print(f"✅ يجب تسميد {tree_key} اليوم")
            else:
                print(f"❌ لا يجب تسميد {tree_key} اليوم")

            return result

        except Exception as e:
            print(f"❌ خطأ في فحص تسميد {tree_key}: {e}")
            return False

    def get_fertilizer_details(self, tree_key: str) -> Dict:
        """جلب تفاصيل السماد للشجرة"""
        tree = self.config['trees_fertilizer_schedule'].get(tree_key, {})

        # إرجاع السماد المناسب
        if 'fertilizer' in tree:
            return tree
        elif 'fertilizers' in tree:
            # اختيار السماد بناءً على الموسم الحالي
            current_season = self._get_current_season()
            fertilizer_index = {'spring_season': 0, 'summer': 1, 'autumn_season': 2}.get(current_season, 0)
            selected_fertilizer = tree['fertilizers'][fertilizer_index % len(tree['fertilizers'])]

            result = tree.copy()
            result['fertilizer'] = selected_fertilizer
            return result

        return tree

    def _get_current_season(self) -> str:
        """تحديد الموسم الحالي"""
        today = date.today()

        if self.is_date_in_season('spring_season', today):
            return 'spring_season'
        elif self.is_date_in_season('summer', today):
            return 'summer'
        elif self.is_date_in_season('autumn_season', today):
            return 'autumn_season'
        elif self.is_date_in_season('cold_season', today):
            return 'cold_season'
        else:
            return 'unknown'

    def should_send_vitamins(self, weather_report: Optional[Dict] = None) -> bool:
        """هل نرسل تنبيه الفيتامينات؟ (تعمل حتى بدون بيانات طقس)"""
        try:
            triggers = self.config['chicken_schedule']['vitamins']['trigger_conditions']
            reasons = []

            # التحقق من الشروط التي تعتمد على الطقس (فقط إذا توفر التقرير)
            if weather_report:
                if 'heat_wave' in triggers and weather_report.get('heat_wave'):
                    reasons.append("heat_wave")
                    print("[Logic] تم كشف موجة حر")

                if 'cold_wave' in triggers and weather_report.get('cold_wave'):
                    reasons.append("cold_wave")
                    print("[Logic] تم كشف موجة برد")

            # التحقق من الشروط التي لا تعتمد على الطقس
            if 'post_deworming' in triggers and self._was_deworming_yesterday():
                reasons.append("post_deworming")
                print("[Logic] أمس كان موعد دواء الديدان")

            # التحقق من شرط تغيير الغذاء (الجديد والمكتمل)
            if 'feed_change' in triggers and self._was_feed_changed_today():
                reasons.append("feed_change")
                print("[Logic] تم تسجيل تغيير الغذاء اليوم")

            if len(reasons) > 0:
                print(f"[Logic] سيتم إرسال تنبيه الفيتامينات - الأسباب: {reasons}")
                return True

            return False

        except Exception as e:
            print(f"❌ خطأ في فحص الفيتامينات: {e}")
            return False

    def _was_deworming_yesterday(self) -> bool:
        """هل أمس كان موعد دواء الديدان؟"""
        try:
            yesterday = date.today() - timedelta(days=1)
            yesterday_str = yesterday.strftime("%m-%d")

            deworming_config = self.config['chicken_schedule']['deworming']
            seasonal_schedule = deworming_config.get('seasonal_schedule', [])

            # البحث عن موعد أمس في الجدول الموسمي
            for schedule_item in seasonal_schedule:
                if schedule_item['date'] == yesterday_str:
                    print(f"[Logic] أمس كان موعد دواء الديدان: {schedule_item['drug']}")
                    return True

            return False

        except Exception as e:
            print(f"⚠️ خطأ في التحقق من دواء الديدان بالأمس: {e}")
            return False

    def _was_feed_changed_today(self) -> bool:
        """هل تم تسجيل تغيير الغذاء لليوم الحالي؟"""
        try:
            flag_file = '.feed_changed_today'
            if os.path.exists(flag_file):
                with open(flag_file, 'r') as f:
                    last_change_date = f.read().strip()

                # يتحقق إذا كان التاريخ المسجل هو تاريخ اليوم
                if last_change_date == date.today().strftime('%Y-%m-%d'):
                    return True
        except Exception as e:
            print(f"⚠️ خطأ في التحقق من تغيير الغذاء: {e}")
        return False

    def mark_feed_changed(self):
        """تقوم بإنشاء ملف علامة لتسجيل أن الغذاء قد تغير اليوم."""
        try:
            flag_file = '.feed_changed_today'
            with open(flag_file, 'w') as f:
                f.write(date.today().strftime('%Y-%m-%d'))
            print(f"[Logic] تم تسجيل تغيير الغذاء بتاريخ اليوم.")
        except Exception as e:
            print(f"❌ خطأ في تسجيل تغيير الغذاء: {e}")

    def should_prevent_coccidiosis(self, weather_report: Optional[Dict] = None) -> bool:
        """هل يجب الوقاية من الكوكسيديا؟"""
        try:
            if not weather_report:
                return False

            triggers = self.config['chicken_schedule']['coccidiosis']['trigger_conditions']

            # فحص الرطوبة العالية
            if 'high_humidity' in triggers and weather_report.get('high_humidity'):
                print("[Logic] رطوبة عالية - خطر الكوكسيديا")
                return True

            # فحص ليالي باردة
            if 'cold_night' in triggers:
                min_temp = weather_report.get('min_temp_48h', 20)
                if min_temp < 5:
                    print("[Logic] ليالي باردة - خطر الكوكسيديا")
                    return True

            return False

        except Exception as e:
            print(f"❌ خطأ في فحص الكوكسيديا: {e}")
            return False

    def should_sanitize_coop(self) -> bool:
        """هل اليوم موعد تطهير الحظيرة؟"""
        try:
            start_date_str = self.config['chicken_schedule']['sanitization']['start_date']
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            interval = self.config['chicken_schedule']['sanitization']['interval_days']

            today = date.today()
            days_diff = (today - start_date).days

            should_sanitize = days_diff % interval == 0

            if should_sanitize:
                print(f"[Logic] موعد تطهير الحظيرة اليوم - آخر مرة: {start_date}, الفاصل: {interval} يوم")

            return should_sanitize

        except Exception as e:
            print(f"❌ خطأ في حساب تطهير الحظيرة: {e}")
            return False

    def should_clean_water_station(self, weather_report: Optional[Dict] = None) -> bool:
        """هل يجب تنظيف محطة الماء؟"""
        try:
            config = self.config['chicken_schedule'].get('water_station', {})
            if not config: return False

            # شرط 1: الفاصل الزمني
            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (date.today() - start_date).days
            is_time = days_diff % interval == 0

            if is_time:
                print(f"[Logic] موعد تنظيف محطة الماء (كل {interval} يوم)")
                return True

            # شرط 2: موجة حر قوية (طحالب)
            if weather_report and weather_report.get('heat_wave'):
                print("[Logic] موجة حر - تنظيف محطة الماء ضروري (طحالب)")
                return True

            return False
        except Exception as e:
            print(f"❌ خطأ في فحص محطة الماء: {e}")
            return False

    def get_pipe_waterer_maintenance(self) -> List[str]:
        """ما هي صيانة السقاية الأنبوبية اليوم؟"""
        tasks = []
        try:
            config = self.config['chicken_schedule'].get('pipe_waterer', {})
            if not config: return []

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            intervals = config.get('intervals', {})
            days_diff = (date.today() - start_date).days

            # فحص كل نوع صيانة
            if days_diff % intervals.get('deep_clean', 30) == 0:
                tasks.append('deep_clean')
            elif days_diff % intervals.get('sanitize', 15) == 0:
                tasks.append('sanitize')
            elif days_diff % intervals.get('rinse', 7) == 0:
                tasks.append('rinse')
            elif days_diff % intervals.get('change_water', 3) == 0:
                tasks.append('change_water')

            return tasks
        except Exception as e:
            print(f"❌ خطأ في فحص السقاية الأنبوبية: {e}")
            return []

    def should_clean_coop_weekly(self, weather_report: Optional[Dict] = None) -> bool:
        """هل يجب التنظيف الأسبوعي للحظيرة؟"""
        try:
            config = self.config['chicken_schedule'].get('weekly_cleaning', {})
            if not config: return False

            # إلغاء إذا كانت الرطوبة عالية جداً (طين)
            if weather_report and weather_report.get('high_humidity'):
                print("[Logic] تأجيل التنظيف الأسبوعي بسبب الرطوبة العالية")
                return False

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (date.today() - start_date).days

            if days_diff % interval == 0:
                print(f"[Logic] موعد التنظيف الأسبوعي (كل {interval} يوم)")
                return True

            return False
        except Exception as e:
            print(f"❌ خطأ في فحص التنظيف الأسبوعي: {e}")
            return False

    def should_turn_soil(self) -> bool:
        """هل يجب تقليب التراب؟"""
        try:
            config = self.config['chicken_schedule'].get('soil_turning', {})
            if not config: return False

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (date.today() - start_date).days

            if days_diff % interval == 0:
                print(f"[Logic] موعد تقليب التراب (كل {interval} يوم)")
                return True
            return False
        except Exception as e:
            print(f"❌ خطأ في فحص تقليب التراب: {e}")
            return False

    def should_check_ventilation(self, weather_report: Optional[Dict] = None) -> bool:
        """هل يجب فحص التهوية؟"""
        try:
            config = self.config['chicken_schedule'].get('ventilation', {})
            if not config: return False

            # شرط الطقس الحار جداً أو البارد جداً (إغلاق/فتح)
            if weather_report and (weather_report.get('heat_wave') or weather_report.get('cold_wave')):
                print("[Logic] فحص التهوية ضروري بسبب الطقس المتطرف")
                return True

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (date.today() - start_date).days

            if days_diff % interval == 0:
                print(f"[Logic] موعد فحص التهوية الدوري (كل {interval} يوم)")
                return True
            return False
        except Exception as e:
            print(f"❌ خطأ في فحص التهوية: {e}")
            return False

    def should_deep_clean_feeders(self) -> bool:
        """هل يجب غسيل المعالف العميق؟"""
        try:
            config = self.config['chicken_schedule'].get('feeder_cleaning', {})
            if not config: return False

            start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").date()
            interval = config['interval_days']
            days_diff = (date.today() - start_date).days

            if days_diff % interval == 0:
                print(f"[Logic] موعد غسيل المعالف العميق (كل {interval} يوم)")
                return True
            return False
        except Exception as e:
            print(f"❌ خطأ في فحص غسيل المعالف: {e}")
            return False

    def get_tasks_for_today(self, weather_report: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """تجميع جميع المهام لليوم"""
        tasks = []

        # مهمة دواء الديدان
        if self.should_deworm_today():
            tasks.append({
                'type': 'deworming',
                'drug': self.get_current_deworm_drug()
            })

        # مهمة الفيتامينات
        # تأخير إرسال الفيتامينات حتى يوم بعد دواء الديدان
        if not self.should_deworm_today() and self._was_deworming_yesterday():
            # سيتم إرسال الفيتامينات بناءً على ظروف الأمس
            pass

        # المهام الجديدة
        if self.should_clean_water_station(weather_report):
            tasks.append({'type': 'water_station'})

        pipe_tasks = self.get_pipe_waterer_maintenance()
        for p_task in pipe_tasks:
            tasks.append({'type': f'pipe_waterer_{p_task}'})

        if self.should_clean_coop_weekly(weather_report):
            tasks.append({'type': 'weekly_cleaning'})

        if self.should_turn_soil():
            tasks.append({'type': 'soil_turning'})

        if self.should_check_ventilation(weather_report):
            tasks.append({'type': 'ventilation'})

        if self.should_deep_clean_feeders():
            tasks.append({'type': 'feeder_cleaning'})

        return tasks

    def get_all_fertilization_tasks(self, weather_report: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """جميع مهام التسميد لليوم"""
        tasks = []
        trees_schedule = self.config.get('trees_fertilizer_schedule', {})

        for tree_key in trees_schedule.keys():
            if self.should_fertilize_tree(tree_key, weather_report):
                details = self.get_fertilizer_details(tree_key)
                tasks.append({
                    'type': 'fertilizer',
                    'tree': tree_key,
                    'details': details
                })

        return tasks

    def save_last_run(self):
        """حفظ وقت آخر تشغيل"""
        try:
            with open(self.last_run_file, 'w') as f:
                f.write(datetime.now().isoformat())
            print(f"[Logic] تم حفظ وقت آخر تشغيل: {datetime.now()}")
        except Exception as e:
            print(f"⚠️ خطأ في حفظ وقت التشغيل: {e}")

    def load_last_run(self) -> Optional[datetime]:
        """قراءة وقت آخر تشغيل"""
        try:
            if os.path.exists(self.last_run_file):
                with open(self.last_run_file, 'r') as f:
                    return datetime.fromisoformat(f.read().strip())
        except Exception as e:
            print(f"⚠️ خطأ في قراءة وقت التشغيل: {e}")
        return None

    def get_weather_dependent_tasks(self, weather_report: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """المهام التي تعتمد على الطقس والشروط الأخرى"""
        tasks = []

        # الفيتامينات (المنطق الكامل)
        if self.should_send_vitamins(weather_report):
            reason_ar = "دعم وقائي"
            reason_bn = "Preventive support"

            # تحديد السبب بدقة أكبر
            if weather_report and weather_report.get('heat_wave'):
                reason_ar, reason_bn = 'موجة حر', 'heat wave'
            elif weather_report and weather_report.get('cold_wave'):
                reason_ar, reason_bn = 'موجة برد', 'cold wave'
            elif self._was_deworming_yesterday():
                reason_ar, reason_bn = 'دعم بعد دواء الديدان', 'post-deworming support'
            elif self._was_feed_changed_today():
                reason_ar, reason_bn = 'تغيير نوع الغذاء', 'feed change'

            tasks.append({
                'type': 'vitamins',
                'reason_ar': reason_ar,
                'reason_bn': reason_bn
            })

        # الوقاية من الكوكسيديا (تتطلب بيانات طقس)
        if weather_report and self.should_prevent_coccidiosis(weather_report):
            tasks.append({
                'type': 'coccidiosis',
                'reason_ar': "رطوبة عالية",
                'reason_bn': "high humidity"
            })

        # تطهير الحظيرة (لا يتطلب طقس)
        if self.should_sanitize_coop():
            tasks.append({
                'type': 'sanitization'
            })

        return tasks

def test_logic():
    """اختبار سريع للمحرك"""
    try:
        logic = FarmLogic()

        print("=== اختبار Farm Logic ===")

        # اختبار دواء الديدان
        if logic.should_deworm_today():
            print(f"✅ اليوم موعد دواء الديدان: {logic.get_current_deworm_drug()}")

        # اختبار تطهير الحظيرة
        if logic.should_sanitize_coop():
            print("✅ اليوم موعد تطهير الحظيرة")

        # اختبار التسميد
        weather_data = {'good_fertilizer_time': True}
        fertilization_tasks = logic.get_all_fertilization_tasks(weather_data)
        print(f"مهام التسميد اليوم: {len(fertilization_tasks)}")

        for task in fertilization_tasks:
            print(f"  - {task['tree']}: {task['details'].get('fertilizer', 'غير محدد')}")

    except Exception as e:
        print(f"❌ خطأ في اختبار المحرك: {e}")

if __name__ == "__main__":
    test_logic()
