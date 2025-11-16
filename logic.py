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
        """هل اليوم موعد دواء الديدان؟"""
        try:
            start_date_str = self.config['chicken_schedule']['deworming']['start_date']
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            interval = self.config['chicken_schedule']['deworming']['interval_days']
            
            today = date.today()
            days_diff = (today - start_date).days
            
            should_deworm = days_diff % interval == 0
            
            if should_deworm:
                print(f"[Logic] موعد دواء الديدان اليوم - آخر مرة: {start_date}, الفاصل: {interval} يوم")
            
            return should_deworm
            
        except Exception as e:
            print(f"❌ خطأ في حساب دواء الديدان: {e}")
            return False
    
    def get_current_deworm_drug(self) -> str:
        """الدواء الحالي في التناوب"""
        try:
            start_date_str = self.config['chicken_schedule']['deworming']['start_date']
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            drugs = self.config['chicken_schedule']['deworming']['drugs_rotation']
            
            today = date.today()
            cycles = (today - start_date).days // 90
            current_drug = drugs[cycles % len(drugs)]
            
            print(f"[Logic] الدواء الحالي: {current_drug}")
            return current_drug
            
        except Exception as e:
            print(f"❌ خطأ في اختيار الدواء: {e}")
            return drugs[0] if 'drugs' in locals() else "Fenbendazole"
    
    def should_fertilize_tree(self, tree_key: str, weather_report: Optional[Dict] = None) -> bool:
        """هل يجب تسميد الشجرة اليوم؟"""
        try:
            tree = self.config['trees_fertilizer_schedule'].get(tree_key)
            if not tree:
                print(f"⚠️ شجرة {tree_key} غير موجودة في الإعدادات")
                return False
            
            print(f"[Logic] فحص تسميد {tree_key}...")
            
            # شرط 1: الموسم
            season_ok = False
            if 'seasons' in tree:
                for season in tree['seasons']:
                    if self.is_date_in_season(season):
                        season_ok = True
                        print(f"[Logic] {tree_key} في موسم {season}")
                        break
            
            # شرط 2: التاريخ المحدد
            date_ok = False
            if 'dates' in tree:
                today_str = date.today().strftime("%Y-%m-%d")
                if today_str in tree['dates']:
                    date_ok = True
                    print(f"[Logic] {tree_key} في التاريخ المحدد: {today_str}")
            
            # شرط 3: ظروف الطقس
            weather_ok = True
            if weather_report and not weather_report.get('good_fertilizer_time', True):
                weather_ok = False
                print(f"[Logic] طقس غير مناسب للتسميد")
            
            # شرط 4: درجة الحرارة القصوى
            temp_ok = True
            if 'max_temp' in tree and weather_report:
                max_temp = weather_report.get('max_temp_48h', 0)
                if max_temp > tree['max_temp']:
                    temp_ok = False
                    print(f"[Logic] درجة الحرارة {max_temp}°C أعلى من الحد المسموح {tree['max_temp']}°C")
            
            # نتيجة نهائية
            result = (season_ok or date_ok) and weather_ok and temp_ok
            
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
        """هل نرسل تنبيه الفيتامينات؟"""
        try:
            if not weather_report:
                print("[Logic] لا توجد بيانات طقس - تجاهل تنبيه الفيتامينات")
                return False
            
            triggers = self.config['chicken_schedule']['vitamins']['trigger_conditions']
            reasons = []
            
            # فحص الظروف الجوية
            if 'heat_wave' in triggers and weather_report.get('heat_wave'):
                reasons.append("heat_wave")
                print("[Logic] تم كشف موجة حر")
            
            if 'cold_wave' in triggers and weather_report.get('cold_wave'):
                reasons.append("cold_wave")
                print("[Logic] تم كشف موجة برد")
            
            # بعد الدواء بيوم
            if self._was_deworming_yesterday():
                reasons.append("post_deworming")
                print("[Logic] أمس كان موعد دواء الديدان")
            
            return len(reasons) > 0
            
        except Exception as e:
            print(f"❌ خطأ في فحص الفيتامينات: {e}")
            return False
    
    def _was_deworming_yesterday(self) -> bool:
        """هل أمس كان موعد دواء الديدان؟"""
        try:
            yesterday = date.today() - timedelta(days=1)
            start_date_str = self.config['chicken_schedule']['deworming']['start_date']
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            interval = self.config['chicken_schedule']['deworming']['interval_days']
            
            days_diff = (yesterday - start_date).days
            return days_diff % interval == 0
            
        except Exception:
            return False
    
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
    
    def get_tasks_for_today(self) -> List[Dict[str, Any]]:
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
        """المهام التي تعتمد على الطقس"""
        tasks = []
        
        if not weather_report:
            return tasks
        
        # الفيتامينات بناءً على الطقس
        if self.should_send_vitamins(weather_report):
            reason_ar = "موجة حر" if weather_report.get('heat_wave') else "موجة برد"
            reason_bn = "heat wave" if weather_report.get('heat_wave') else "cold wave"
            
            tasks.append({
                'type': 'vitamins',
                'reason_ar': reason_ar,
                'reason_bn': reason_bn
            })
        
        # الوقاية من الكوكسيديا
        if self.should_prevent_coccidiosis(weather_report):
            tasks.append({
                'type': 'coccidiosis',
                'reason_ar': "رطوبة عالية",
                'reason_bn': "high humidity"
            })
        
        # تطهير الحظيرة
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