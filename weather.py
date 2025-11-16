import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

class WeatherFetcher:
    def __init__(self, api_key: str, city: str, country: str):
        self.api_key = api_key
        self.city = city
        self.country = country
        self.base_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    def get_weather_data(self) -> Optional[Dict]:
        """جلب بيانات الطقس لـ 5 أيام كل 3 ساعات"""
        params = {
            'q': f'{self.city},{self.country}',
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'ar'
        }
        
        try:
            print(f"[Weather] جلب بيانات الطقس لـ {self.city}, {self.country}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في جلب الطقس: {e}")
            return None
    
    def analyze_conditions(self, weather_data: Optional[Dict]) -> Optional[Dict]:
        """تحليل الظروف الجوية وإرجاع تقرير"""
        if not weather_data:
            print("⚠️ تحذير: لا توجد بيانات طقس متاحة")
            return None
        
        try:
            forecast = weather_data.get('list', [])[:16]  # تقريباً 48 ساعة
            
            # استخراج البيانات
            temps_max = [item['main']['temp_max'] for item in forecast]
            temps_min = [item['main']['temp_min'] for item in forecast]
            humidity = [item['main']['humidity'] for item in forecast]
            rain_prob = [item.get('rain', {}).get('3h', 0) for item in forecast]
            
            # حساب المؤشرات
            heat_index = self._calculate_heat_index(temps_max, humidity)
            
            report = {
                'current_temp': forecast[0]['main']['temp'],
                'max_temp_48h': max(temps_max),
                'min_temp_48h': min(temps_min),
                'humidity_avg': sum(humidity) / len(humidity),
                'rain_48h': sum(rain_prob) > 0,
                'heat_wave': self._detect_heat_wave(temps_max, heat_index),
                'cold_wave': self._detect_cold_wave(temps_min),
                'high_humidity': (sum(humidity) / len(humidity)) > 80,
                'good_fertilizer_time': self._is_good_fertilizer_time(temps_max, rain_prob),
                'heat_index': round(heat_index, 1)
            }
            
            print(f"[Weather] تحليل الطقس - حرارة: {report['current_temp']}°C، رطوبة: {report['humidity_avg']:.1f}%")
            print(f"[Weather] حالة الطقس - موجة حر: {report['heat_wave']}، موجة برد: {report['cold_wave']}")
            
            return report
            
        except (KeyError, IndexError) as e:
            print(f"❌ خطأ في تحليل بيانات الطقس: {e}")
            return None
    
    def _calculate_heat_index(self, temps: list, humidity: list) -> float:
        """حساب Heat Index"""
        if not temps or not humidity:
            return 0
            
        temp = sum(temps) / len(temps)
        hum = sum(humidity) / len(humidity)
        
        # معادلة مبسطة للحرارة الحرارية
        if temp < 80:
            # للحرارة المعتدلة
            hi = temp + (0.555 * (6.11 * pow(2.718, 5417.7530 * ((1/273.16) - (1/(273.16 + temp)))) * hum / 100 - 10))
        else:
            # للحرارة العالية (معادلة NOAA مبسطة)
            hi = temp + 0.33 * ((6.11 * pow(2.718, 5417.7530 * ((1/273.16) - (1/(273.16 + temp)))) * hum / 100) - 10.0) + 4.0
        
        return hi
    
    def _detect_heat_wave(self, temps_max: list, heat_index: float) -> bool:
        """كشف موجة حر"""
        if not temps_max:
            return False
            
        # حرارة عالية لمدة يومين أو heat index عالي
        high_temp_days = sum(1 for t in temps_max if t > 38)
        return high_temp_days >= 2 or heat_index > 45
    
    def _detect_cold_wave(self, temps_min: list) -> bool:
        """كشف موجة برد"""
        if not temps_min:
            return False
        return min(temps_min) < 8
    
    def _is_good_fertilizer_time(self, temps_max: list, rain_prob: list) -> bool:
        """الوقت المثالي لتسميد: 15-32 درجة ولا مطر"""
        if not temps_max or not rain_prob:
            return False
            
        avg_temp = sum(temps_max) / len(temps_max)
        no_rain_24h = all(r == 0 for r in rain_prob[:8])  # 24 ساعة بدون مطر
        good_temp_range = 15 <= avg_temp <= 32
        
        return good_temp_range and no_rain_24h
    
    def get_seasonal_alert(self, weather_report: Optional[Dict]) -> Optional[str]:
        """تحديد التنبيهات الموسمية بناءً على الطقس"""
        if not weather_report:
            return None
        
        alerts = []
        
        if weather_report['heat_wave']:
            alerts.append("🔥 موجة حر - مراقبة الدجاج وإعطاء فيتنامينات")
        
        if weather_report['cold_wave']:
            alerts.append("❄️ موجة برد - حماية الدجاج من البرد")
        
        if weather_report['high_humidity']:
            alerts.append("💧 رطوبة عالية - زيادة خطر الكوكسيديا")
        
        if not weather_report['good_fertilizer_time']:
            if weather_report['max_temp_48h'] > 35:
                alerts.append("🌡️ حرارة مرتفعة - تجنب التسميد")
            elif weather_report['rain_48h']:
                alerts.append("🌧️ مطر متوقع - تأجيل التسميد")
        
        return " | ".join(alerts) if alerts else None
    
    def get_weekly_forecast(self, weather_data: Optional[Dict]) -> Optional[Dict]:
        """تقرير أسبوعي مفصل"""
        if not weather_data:
            return None
        
        try:
            forecast = weather_data.get('list', [])
            
            # تجميع البيانات أسبوعياً
            weekly_data = {}
            for i, item in enumerate(forecast[:8]):  # أول 24 ساعة
                date_key = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                
                if date_key not in weekly_data:
                    weekly_data[date_key] = {
                        'temps': [],
                        'humidity': [],
                        'rain': 0,
                        'description': item['weather'][0]['description'] if item['weather'] else 'غير محدد'
                    }
                
                weekly_data[date_key]['temps'].append(item['main']['temp'])
                weekly_data[date_key]['humidity'].append(item['main']['humidity'])
                weekly_data[date_key]['rain'] += item.get('rain', {}).get('3h', 0)
            
            # حساب المتوسطات
            for date_key in weekly_data:
                data = weekly_data[date_key]
                data['avg_temp'] = sum(data['temps']) / len(data['temps'])
                data['avg_humidity'] = sum(data['humidity']) / len(data['humidity'])
            
            return weekly_data
            
        except Exception as e:
            print(f"❌ خطأ في تحليل التوقع الأسبوعي: {e}")
            return None

def test_weather():
    """اختبار سريع للخدمة"""
    import os
    
    # قراءة المفتاح من environment أو config
    api_key = os.getenv('OPENWEATHER_API_KEY') or "your_api_key_here"
    
    if api_key == "your_api_key_here":
        print("⚠️ لم يتم العثور على OPENWEATHER_API_KEY في المتغيرات البيئية")
        return
    
    fetcher = WeatherFetcher(api_key, "Tabuk", "SA")
    weather_data = fetcher.get_weather_data()
    
    if weather_data:
        report = fetcher.analyze_conditions(weather_data)
        print("✅ تم جلب بيانات الطقس بنجاح")
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("❌ فشل في جلب بيانات الطقس")

if __name__ == "__main__":
    test_weather()