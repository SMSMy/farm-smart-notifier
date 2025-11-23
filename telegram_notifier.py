import asyncio
import os
from typing import List, Dict, Optional
from telegram import Bot, InputFile
from telegram.error import TelegramError

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
            raise ValueError("❌ يجب إدخال bot_token صالح في config.json")
        if not chat_id or chat_id == "YOUR_CHAT_ID_HERE":
            raise ValueError("❌ يجب إدخال chat_id صالح في config.json")

        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

        print(f"[Telegram] تم تهيئة البوت للتواصل مع {chat_id}")

    def send_batch(self, tasks: List[Dict]) -> bool:
        """إرسال جميع المهام دفعة واحدة في حلقة أحداث واحدة"""
        if not tasks:
            print("[Telegram] لا توجد مهام للإرسال")
            return True

        print(f"[Telegram] بدء إرسال {len(tasks)} مهمة...")

        try:
            asyncio.run(self._send_batch_async(tasks))
            print("✅ تم إرسال جميع المهام بنجاح")
            return True
        except Exception as e:
            print(f"❌ فشل في إرسال المهام: {e}")
            return False

    async def _send_batch_async(self, tasks: List[Dict]):
        """حلقة أحداث واحدة لكل المهام"""
        for i, task in enumerate(tasks, 1):
            try:
                print(f"  > إرسال المهمة {i}/{len(tasks)}: {task.get('type', 'unknown')}")

                # إرسال العربية
                await self._send_message_async(
                    task.get('ar', ''),
                    task.get('image'),
                    False  # لا أزرار
                )

                # إرسال البنغالية
                await self._send_message_async(
                    task.get('bn', ''),
                    None,  # لا صورة للبنغالية
                    False
                )

                print(f"    ✅ تم إرسال المهمة {i} بنجاح")

                # انتظار قصير بين الرسائل لتجنب rate limiting
                await asyncio.sleep(1)

            except TelegramError as e:
                print(f"    ❌ فشل إرسال المهمة {i} ({task.get('type')}): {e}")
                continue  # المتابعة للمهمة التالية
            except Exception as e:
                print(f"    ⚠️ خطأ غير متوقع في المهمة {i}: {e}")
                continue

    async def _send_message_async(self, text: str, image_name: Optional[str] = None, add_buttons: bool = False):
        """إرسال رسالة فردية (داخل الحلقة)"""
        if not text:
            print("    ⚠️ رسالة فارغة - تخطي الإرسال")
            return

        # العثور على مسار الصورة
        image_path = self._find_image_path(image_name)

        try:
            if image_path and os.path.exists(image_path):
                await self._send_photo_with_caption(image_path, text)
            else:
                if image_name:
                    print(f"    ⚠️ الصورة '{image_name}' غير موجودة، سيتم إرسال نص فقط")
                await self._send_text_only(text, add_buttons)

        except Exception as e:
            print(f"    ❌ فشل إرسال الرسالة: {e}")
            raise

    def _find_image_path(self, image_name: Optional[str]) -> Optional[str]:
        """العثور على مسار الصورة"""
        if not image_name:
            return None

        # البحث في مجلد الصور مع امتدادات مختلفة
        base_paths = [
            f'images/{image_name}',
            f'images/fertilizers/{image_name}',
            f'../images/{image_name}',
            f'./images/{image_name}'
        ]

        # إضافة امتدادات مختلفة
        extensions = ['', '.jpg', '.png', '.jpeg', '.webp']

        for base_path in base_paths:
            for ext in extensions:
                full_path = base_path + ext
                if os.path.exists(full_path):
                    print(f"    📷 تم العثور على الصورة: {full_path}")
                    return full_path

        print(f"    ⚠️ لم يتم العثور على صورة: {image_name}")
        return None

    async def _send_photo_with_caption(self, image_path: str, caption: str):
        """إرسال صورة مع نص"""
        try:
            with open(image_path, 'rb') as photo_file:
                await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=InputFile(photo_file),
                    caption=caption[:1024],  # حد أقصى للصورة
                    parse_mode='MarkdownV2'
                )

                # إذا كان النص طويلاً جداً، إرسال الباقي
                if len(caption) > 1024:
                    await asyncio.sleep(0.5)  # تأخير قصير
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=caption[1024:],
                        parse_mode='MarkdownV2'
                    )

        except FileNotFoundError:
            print(f"    ❌ الصورة غير موجودة: {image_path}")
            # إرسال كنص فقط
            await self._send_text_only(caption, False)

    async def _send_text_only(self, text: str, add_buttons: bool = False):
        """إرسال نص فقط"""
        try:
            # إضافة أزرار إذا طُلب
            reply_markup = None
            if add_buttons:
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup

                keyboard = [[InlineKeyboardButton("✅ تم إنجاز المهمة", callback_data="task_done")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )

        except Exception as e:
            print(f"    ❌ فشل إرسال النص: {e}")
            raise

    def send_weather_alert(self, weather_report: Optional[Dict] = None):
        """إرسال تنبيه طقس خاص"""
        if not weather_report:
            return

        alerts = []
        messages = []

        # إعداد الرسائل
        if weather_report.get('heat_wave'):
            messages.append({
                'ar': '🌡️ *تحذير: موجة حر* 🔥\\n\\n🔥 حرارة عالية متوقعة\\n🌿 تأكد من توفير الظل والماء البارد للدجاج\\n🎥 *أرفق صوراً أو فيديو للمزرعة أثناء موجة الحر*',
                'bn': '🌡️ *সতর্কতা: তাপ তরঙ্গ* 🔥\\n\\n🔥 উচ্চ তাপমাত্রা আশা করা যাচ্ছে\\n🌿 মুরগির জন্য ছায়া এবং ঠান্ডা পানি নিশ্চিত করুন\\n🎥 *তাপের তরঙ্গের সময় খামারের ছবি বা ভিডিও সংযুক্ত করুন*',
                'image': 'heat_warn.jpg'
            })

        if weather_report.get('cold_wave'):
            messages.append({
                'ar': '❄️ *تحذير: موجة برد* 🌬️\\n\\n❄️ درجة حرارة منخفضة متوقعة\\n🧥 تأكد من تدفئة الدجاج\\n🎥 *أرفق صوراً أو فيديو لتدابير تدفئة الدجاج*',
                'bn': '❄️ *সতর্কতা: ঠান্ডার তরঙ্গ* 🌬️\\n\\n❄️ নিম্ন তাপমাত্রা প্রত্যাশিত\\n🧥 মুরগিকে উষ্ণ রাখা নিশ্চিত করুন\\n🎥 *মুরগির উষ্ণ পদ্ধতির ছবি বা ভিডিও সংযুক্ত করুন*',
                'image': 'cold_warn.jpg'
            })

        if weather_report.get('high_humidity'):
            messages.append({
                'ar': '💧 *تحذير: رطوبة عالية* 🌧️\\n\\n💧 مخاطر ارتفاع الرطوبة\\n👁️ زيادة فحص الدجاج وإضافة فيتامينات\\n🎥 *أرفق صوراً أو فيديو لحالة المزرعة أثناء الرطوبة العالية*',
                'bn': '💧 *সতر্কতা: উচ্চ আদ্রতা* 🌧️\\n\\n💧 উচ্চ আদ্রতার ঝুঁকি\\n👁️ মুরগির পরিদর্শন এবং ভিটামিন যোগ করুন\\n🎥 *উচ্চ আদ্রতার সময় খামারের অবস্থার ছবি বা ভিডিও সংযুক্ত করুন*',
                'image': 'humidity_warn.jpg'
            })

        # إرسال الرسائل
        for msg in messages:
            asyncio.run(self._send_single_message(msg))

    async def _send_single_message(self, message_data: Dict):
        """إرسال رسالة واحدة"""
        try:
            await self._send_message_async(
                message_data['ar'],
                message_data.get('image'),
                False
            )

            await asyncio.sleep(0.5)  # تأخير قصير

            await self._send_message_async(
                message_data['bn'],
                None,
                False
            )

        except Exception as e:
            print(f"❌ فشل إرسال رسالة الطقس: {e}")

    def test_connection(self) -> bool:
        """اختبار الاتصال مع Telegram"""
        try:
            print("[Telegram] اختبار الاتصال...")

            # جلب معلومات البوت
            import asyncio
            bot_info = asyncio.run(self.bot.get_me())
            print(f"✅ الاتصال ناجح مع البوت: {bot_info.first_name} (@{bot_info.username})")

            # إرسال رسالة اختبار
            test_message = "🔧 <b>اختبار نظام التنبيه للمزرعة ✨</b>\n\n🎥 بعد تنفيذ أي مهمة، يرجى إضافة فيديو أو صورة توثّق الإنجاز!\n\nالنظام متصل ويعمل بشكل صحيح!"

            asyncio.run(self._send_single_message({
                'ar': test_message,
                'bn': "🔧 <b>Farm Alert System Test</b>\n\nSystem connected and working correctly!",
                'image': None
            }))

            return True

        except Exception as e:
            print(f"❌ فشل اختبار الاتصال: {e}")
            return False

    def send_daily_summary(self, tasks_completed: int, weather_status: str):
        """إرسال ملخص يومي"""
        try:
            summary_ar = f"""📊 <b>ملخص يومي للمزرعة 🌱</b>

✅ المهام المنجزة: {tasks_completed}
🌡️ حالة الطقس: {weather_status}
🕐 الوقت: {asyncio.get_event_loop().time()}
🎥 يرجى إرفاق صور/فيديو للمهام المنجزة

تم التشغيل التلقائي بواسطة نظام Farm Notifier"""

            summary_bn = f"""📊 <b>Daily Farm Summary 🌱</b>

✅ Tasks Completed: {tasks_completed}
🌡️ Weather Status: {weather_status}
🕐 Time: {asyncio.get_event_loop().time()}
🎥 Please attach photos/videos of completed tasks

Automated by Farm Notifier System"""

            import asyncio
            asyncio.run(self._send_single_message({
                'ar': summary_ar,
                'bn': summary_bn,
                'image': None
            }))

        except Exception as e:
            print(f"⚠️ فشل إرسال الملخص اليومي: {e}")

def test_telegram():
    """اختبار سريع لـ Telegram"""
    import os

    # قراءة التوكنات من environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("⚠️ لم يتم العثور على TELEGRAM_BOT_TOKEN أو TELEGRAM_CHAT_ID")
        print("💡 يمكنك إضافتها في .env file")
        return

    try:
        notifier = TelegramNotifier(bot_token, chat_id)
        if notifier.test_connection():
            print("✅ اختبار Telegram ناجح")
        else:
            print("❌ فشل اختبار Telegram")
    except Exception as e:
        print(f"❌ خطأ في اختبار Telegram: {e}")

if __name__ == "__main__":
    test_telegram()
