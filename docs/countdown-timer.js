/**
 * عداد زمني للإشعارات القادمة
 * Farm Notifier Countdown Timer
 */

class FarmNotifierCountdown {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || 'http://localhost:5000/api';
        this.containerId = options.containerId || 'countdown-container';
        this.updateInterval = options.updateInterval || 1000; // تحديث كل ثانية
        this.language = options.language || 'ar';

        this.container = null;
        this.intervalId = null;
        this.nextNotification = null;
        this.isRunning = false;

        this.init();
    }

    init() {
        this.createContainer();
        this.fetchNextNotification();
        this.startCountdown();

        // تحديث البيانات كل 5 دقائق
        setInterval(() => {
            this.fetchNextNotification();
        }, 5 * 60 * 1000);
    }

    createContainer() {
        // البحث عن الحاوية الموجودة أو إنشاء واحدة جديدة
        this.container = document.getElementById(this.containerId);

        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = this.containerId;
            this.container.className = 'countdown-timer';

            // إضافة الحاوية إلى أعلى الصفحة
            const header = document.querySelector('header');
            if (header) {
                header.parentNode.insertBefore(this.container, header.nextSibling);
            } else {
                document.body.insertBefore(this.container, document.body.firstChild);
            }
        }

        this.addStyles();
    }

    addStyles() {
        // إضافة CSS للعداد إذا لم يكن موجوداً
        if (!document.getElementById('countdown-styles')) {
            const style = document.createElement('style');
            style.id = 'countdown-styles';
            style.textContent = `
                .countdown-timer {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    margin: 20px 0;
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                }

                .countdown-timer::before {
                    content: '';
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                    animation: pulse 3s ease-in-out infinite;
                }

                @keyframes pulse {
                    0%, 100% { transform: scale(1); opacity: 0.5; }
                    50% { transform: scale(1.1); opacity: 0.8; }
                }

                .countdown-header {
                    position: relative;
                    z-index: 1;
                    margin-bottom: 15px;
                }

                .countdown-title {
                    font-size: 1.2rem;
                    font-weight: 600;
                    margin-bottom: 5px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }

                .countdown-next-task {
                    font-size: 0.9rem;
                    opacity: 0.9;
                    margin-bottom: 10px;
                }

                .countdown-display {
                    position: relative;
                    z-index: 1;
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    flex-wrap: wrap;
                }

                .countdown-unit {
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 10px;
                    padding: 10px 15px;
                    min-width: 60px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }

                .countdown-number {
                    font-size: 1.5rem;
                    font-weight: 700;
                    display: block;
                    line-height: 1;
                }

                .countdown-label {
                    font-size: 0.8rem;
                    opacity: 0.9;
                    margin-top: 5px;
                }

                .countdown-loading {
                    position: relative;
                    z-index: 1;
                    padding: 20px;
                    opacity: 0.8;
                }

                .countdown-error {
                    position: relative;
                    z-index: 1;
                    background: rgba(220, 53, 69, 0.9);
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 10px;
                }

                .countdown-no-notifications {
                    position: relative;
                    z-index: 1;
                    background: rgba(40, 167, 69, 0.9);
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 10px;
                }

                /* تجاوب مع الشاشات الصغيرة */
                @media (max-width: 768px) {
                    .countdown-timer {
                        margin: 10px 0;
                        padding: 15px;
                    }

                    .countdown-display {
                        gap: 10px;
                    }

                    .countdown-unit {
                        padding: 8px 12px;
                        min-width: 50px;
                    }

                    .countdown-number {
                        font-size: 1.3rem;
                    }

                    .countdown-title {
                        font-size: 1.1rem;
                    }
                }

                /* للغة البنغالية */
                .lang-bn .countdown-timer {
                    direction: ltr;
                    text-align: center;
                }
            `;
            document.head.appendChild(style);
        }
    }

    async fetchNextNotification() {
        try {
            const response = await fetch(`${this.apiUrl}/notifications/countdown`);
            const data = await response.json();

            if (data.success) {
                this.nextNotification = data.next_notification;
                this.updateDisplay();
            } else {
                this.showError(data.error || 'خطأ في جلب البيانات');
            }
        } catch (error) {
            console.error('خطأ في جلب الإشعار التالي:', error);
            this.showOfflineMode();
        }
    }

    startCountdown() {
        if (this.isRunning) return;

        this.isRunning = true;
        this.intervalId = setInterval(() => {
            this.updateCountdown();
        }, this.updateInterval);
    }

    stopCountdown() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.isRunning = false;
    }

    updateCountdown() {
        if (!this.nextNotification) return;

        const now = new Date();
        const targetTime = new Date(this.nextNotification.datetime);
        const timeDiff = targetTime - now;

        if (timeDiff <= 0) {
            // انتهى الوقت، جلب الإشعار التالي
            this.fetchNextNotification();
            return;
        }

        const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

        this.renderCountdown({ days, hours, minutes, seconds });
    }

    updateDisplay() {
        if (!this.nextNotification) {
            this.showNoNotifications();
            return;
        }

        this.updateCountdown();
    }

    renderCountdown(time) {
        const isArabic = this.language === 'ar';
        const title = isArabic ? 'الإشعار القادم' : 'পরবর্তী বিজ্ঞপ্তি';
        const taskTitle = isArabic ? this.nextNotification.title_ar : this.nextNotification.title_bn;

        const labels = isArabic ?
            { days: 'يوم', hours: 'ساعة', minutes: 'دقيقة', seconds: 'ثانية' } :
            { days: 'দিন', hours: 'ঘন্টা', minutes: 'মিনিট', seconds: 'সেকেন্ড' };

        this.container.innerHTML = `
            <div class="countdown-header">
                <div class="countdown-title">
                    ${this.nextNotification.icon} ${title}
                </div>
                <div class="countdown-next-task">
                    ${taskTitle}
                </div>
            </div>
            <div class="countdown-display">
                ${time.days > 0 ? `
                    <div class="countdown-unit">
                        <span class="countdown-number">${time.days}</span>
                        <div class="countdown-label">${labels.days}</div>
                    </div>
                ` : ''}
                <div class="countdown-unit">
                    <span class="countdown-number">${time.hours}</span>
                    <div class="countdown-label">${labels.hours}</div>
                </div>
                <div class="countdown-unit">
                    <span class="countdown-number">${time.minutes}</span>
                    <div class="countdown-label">${labels.minutes}</div>
                </div>
                <div class="countdown-unit">
                    <span class="countdown-number">${time.seconds}</span>
                    <div class="countdown-label">${labels.seconds}</div>
                </div>
            </div>
        `;
    }

    showLoading() {
        const isArabic = this.language === 'ar';
        const message = isArabic ? 'جاري تحميل البيانات...' : 'ডেটা লোড হচ্ছে...';

        this.container.innerHTML = `
            <div class="countdown-loading">
                ⏳ ${message}
            </div>
        `;
    }

    showError(error) {
        const isArabic = this.language === 'ar';
        const message = isArabic ? 'خطأ في تحميل البيانات' : 'ডেটা লোড করতে ত্রুটি';

        this.container.innerHTML = `
            <div class="countdown-error">
                ❌ ${message}
                <br><small>${error}</small>
            </div>
        `;
    }

    showNoNotifications() {
        const isArabic = this.language === 'ar';
        const message = isArabic ?
            'لا توجد إشعارات مجدولة خلال الأسبوع القادم' :
            'আগামী সপ্তাহে কোনো বিজ্ঞপ্তি নির্ধারিত নেই';

        this.container.innerHTML = `
            <div class="countdown-no-notifications">
                ✅ ${message}
            </div>
        `;
    }

    showOfflineMode() {
        const isArabic = this.language === 'ar';
        const message = isArabic ?
            'غير متصل - تأكد من تشغيل الخادم' :
            'অফলাইন - সার্ভার চালু আছে কিনা পরীক্ষা করুন';

        this.container.innerHTML = `
            <div class="countdown-error">
                📡 ${message}
                <br><small>API Server: ${this.apiUrl}</small>
            </div>
        `;
    }

    // تغيير اللغة
    setLanguage(language) {
        this.language = language;
        this.updateDisplay();
    }

    // تدمير العداد
    destroy() {
        this.stopCountdown();
        if (this.container) {
            this.container.remove();
        }
    }
}

// تهيئة تلقائية عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تحديد اللغة الحالية
    const currentLang = document.documentElement.getAttribute('lang') || 'ar';

    // إنشاء العداد
    window.farmCountdown = new FarmNotifierCountdown({
        language: currentLang,
        apiUrl: 'http://localhost:5000/api'  // يمكن تغييرها حسب البيئة
    });

    // ربط تغيير اللغة بالعداد
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetLang = this.dataset.lang;
            if (window.farmCountdown) {
                window.farmCountdown.setLanguage(targetLang);
            }
        });
    });
});

// تصدير الكلاس للاستخدام الخارجي
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FarmNotifierCountdown;
}

