/**
 * عدادات زمنية داخل البطاقات
 * Card Countdown Timers
 */

class CardCountdownManager {
    constructor(options = {}) {
        this.jsonFile = options.jsonFile || 'notifications.json';
        this.language = options.language || 'ar';
        this.updateInterval = options.updateInterval || 1000;

        this.notificationData = null;
        this.intervalId = null;
        this.cardMappings = this.initializeCardMappings();

        this.init();
    }

    init() {
        this.addStyles();
        this.fetchNotificationData();
        this.startCountdown();

        // تحديث البيانات كل 10 دقائق
        setInterval(() => {
            this.fetchNotificationData();
        }, 10 * 60 * 1000);
    }

    initializeCardMappings() {
        // ربط البطاقات بأنواع الإشعارات
        return {
            // بطاقات الدواجن
            'deworming': {
                selector: 'a[href="deworming.html"]',
                types: ['deworming'],
                icon: '🪱',
                priority: 'high'
            },
            'vitamins': {
                selector: 'a[href="vitamins.html"]',
                types: ['vitamins'],
                icon: '💊',
                priority: 'medium'
            },
            'sanitization': {
                selector: 'a[href="sanitization.html"]',
                types: ['sanitization'],
                icon: '🧹',
                priority: 'medium'
            },
            'coccidiosis': {
                selector: 'a[href="coccidiosis.html"]',
                types: ['coccidiosis'],
                icon: '🦠',
                priority: 'high'
            },
            'weekly_cleaning': {
                selector: 'a[href="weekly_cleaning.html"]',
                types: ['weekly_cleaning'],
                icon: '🧽',
                priority: 'medium'
            },
            'soil_turning': {
                selector: 'a[href="soil_turning.html"]',
                types: ['soil_turning'],
                icon: '🌱',
                priority: 'low'
            },
            'ventilation': {
                selector: 'a[href="ventilation.html"]',
                types: ['ventilation'],
                icon: '💨',
                priority: 'medium'
            },
            'feeder_cleaning': {
                selector: 'a[href="feeder_cleaning.html"]',
                types: ['feeder_cleaning'],
                icon: '🪣',
                priority: 'medium'
            },
            'water_station': {
                selector: 'a[href="water_station.html"]',
                types: ['water_station'],
                icon: '💧',
                priority: 'medium'
            },
            'pipe_waterer': {
                selector: 'a[href="pipe_waterer.html"]',
                types: ['pipe_waterer_change_water', 'pipe_waterer_rinse', 'pipe_waterer_sanitize', 'pipe_waterer_deep_clean'],
                icon: '🚰',
                priority: 'medium'
            },
            // بطاقات الأشجار - عامة للتسميد
            'henna': {
                selector: 'a[href="henna.html"]',
                types: ['fertilizer'],
                tree: 'henna',
                icon: '🌿',
                priority: 'medium'
            },
            'fig': {
                selector: 'a[href="fig.html"]',
                types: ['fertilizer'],
                tree: 'fig',
                icon: '🍈',
                priority: 'medium'
            },
            'banana': {
                selector: 'a[href="banana.html"]',
                types: ['fertilizer'],
                tree: 'banana',
                icon: '🍌',
                priority: 'medium'
            },
            'mango': {
                selector: 'a[href="mango.html"]',
                types: ['fertilizer'],
                tree: ['mango_small', 'mango_large'],
                icon: '🥭',
                priority: 'medium'
            },
            'pomegranate': {
                selector: 'a[href="pomegranate.html"]',
                types: ['fertilizer'],
                tree: 'pomegranate',
                icon: '🍎',
                priority: 'medium'
            },
            'grape': {
                selector: 'a[href="grape.html"]',
                types: ['fertilizer'],
                tree: 'grape',
                icon: '🍇',
                priority: 'medium'
            },
            'jackfruit': {
                selector: 'a[href="jackfruit.html"]',
                types: ['fertilizer'],
                tree: 'jackfruit_young',
                icon: '🍈',
                priority: 'medium'
            },
            'acacia': {
                selector: 'a[href="acacia.html"]',
                types: ['fertilizer'],
                tree: 'acacia',
                icon: '🌳',
                priority: 'low'
            },
            'bougainvillea': {
                selector: 'a[href="bougainvillea.html"]',
                types: ['fertilizer'],
                tree: 'bougainvillea',
                icon: '🌺',
                priority: 'medium'
            },
            'mint': {
                selector: 'a[href="mint.html"]',
                types: ['fertilizer'],
                tree: 'mint_basil',
                icon: '🌿',
                priority: 'medium'
            },
            'moringa': {
                selector: 'a[href="moringa.html"]',
                types: ['fertilizer'],
                tree: 'moringa',
                icon: '🌿',
                priority: 'medium'
            },
            'custard': {
                selector: 'a[href="custard.html"]',
                types: ['fertilizer'],
                tree: 'custard_apple',
                icon: '🍏',
                priority: 'medium'
            }
        };
    }

    addStyles() {
        if (!document.getElementById('card-countdown-styles')) {
            const style = document.createElement('style');
            style.id = 'card-countdown-styles';
            style.textContent = `
                .card-countdown {
                    position: absolute;
                    top: 6px;
                    right: 6px;
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
                    color: white;
                    padding: 6px 10px;
                    border-radius: 15px;
                    font-size: 0.75rem;
                    font-weight: 700;
                    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.25);
                    backdrop-filter: blur(10px);
                    border: 1.5px solid rgba(255, 255, 255, 0.3);
                    z-index: 10;
                    min-width: 50px;
                    text-align: center;
                    line-height: 1.1;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }

                .card-countdown.high-priority {
                    background: linear-gradient(135deg, rgba(220, 53, 69, 0.95) 0%, rgba(255, 107, 107, 0.95) 100%);
                    animation: pulse-urgent 2s ease-in-out infinite;
                    border-color: rgba(255, 255, 255, 0.4);
                }

                .card-countdown.medium-priority {
                    background: linear-gradient(135deg, rgba(255, 152, 0, 0.95) 0%, rgba(255, 193, 7, 0.95) 100%);
                    color: white;
                    border-color: rgba(255, 255, 255, 0.4);
                }

                .card-countdown.low-priority {
                    background: linear-gradient(135deg, rgba(40, 167, 69, 0.95) 0%, rgba(76, 175, 80, 0.95) 100%);
                    border-color: rgba(255, 255, 255, 0.4);
                }

                .card-countdown.overdue {
                    background: linear-gradient(135deg, rgba(139, 69, 19, 0.9) 0%, rgba(160, 82, 45, 0.9) 100%);
                    animation: pulse-overdue 1s ease-in-out infinite;
                }

                @keyframes pulse-urgent {
                    0%, 100% { transform: scale(1); opacity: 0.9; }
                    50% { transform: scale(1.05); opacity: 1; }
                }

                @keyframes pulse-overdue {
                    0%, 100% { transform: scale(1); opacity: 0.8; }
                    50% { transform: scale(1.1); opacity: 1; }
                }

                .guide-card {
                    position: relative;
                }

                .card-countdown-text {
                    display: block;
                    font-size: 0.65rem;
                    line-height: 1;
                }

                .card-countdown-time {
                    display: block;
                    font-size: 0.6rem;
                    opacity: 0.9;
                    margin-top: 1px;
                }

                /* تجاوب مع الشاشات الصغيرة */
                @media (max-width: 768px) {
                    .card-countdown {
                        top: 4px;
                        right: 4px;
                        padding: 5px 8px;
                        font-size: 0.7rem;
                        min-width: 45px;
                        border-radius: 12px;
                        border-width: 1px;
                    }

                    .card-countdown-text {
                        font-size: 0.65rem;
                        font-weight: 800;
                    }

                    .card-countdown-time {
                        font-size: 0.55rem;
                        margin-top: 1px;
                    }
                }

                @media (max-width: 480px) {
                    .card-countdown {
                        top: 3px;
                        right: 3px;
                        padding: 4px 7px;
                        font-size: 0.65rem;
                        min-width: 42px;
                        border-radius: 10px;
                    }

                    .card-countdown-text {
                        font-size: 0.6rem;
                        font-weight: 900;
                    }

                    .card-countdown-time {
                        font-size: 0.5rem;
                    }
                }

                /* للغة البنغالية */
                .lang-bn .card-countdown {
                    left: 8px;
                    right: auto;
                }

                .lang-bn .card-countdown-text,
                .lang-bn .card-countdown-time {
                    direction: ltr;
                }

                @media (max-width: 768px) {
                    .lang-bn .card-countdown {
                        left: 4px;
                        right: auto;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    async fetchNotificationData() {
        try {
            const response = await fetch(this.jsonFile);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.notificationData = data;
            this.updateAllCards();

        } catch (error) {
            console.error('خطأ في جلب بيانات الإشعارات للبطاقات:', error);
        }
    }

    startCountdown() {
        if (this.intervalId) return;

        this.intervalId = setInterval(() => {
            this.updateAllCards();
        }, this.updateInterval);
    }

    stopCountdown() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    updateAllCards() {
        if (!this.notificationData) return;

        Object.keys(this.cardMappings).forEach(cardKey => {
            this.updateCard(cardKey);
        });
    }

    updateCard(cardKey) {
        const mapping = this.cardMappings[cardKey];
        const cardElement = document.querySelector(mapping.selector);

        if (!cardElement) return;

        // البحث عن الإشعار المناسب
        const nextNotification = this.findNextNotificationForCard(mapping);

        // إزالة العداد القديم
        const existingCountdown = cardElement.querySelector('.card-countdown');
        if (existingCountdown) {
            existingCountdown.remove();
        }

        if (nextNotification) {
            this.addCountdownToCard(cardElement, nextNotification, mapping.priority);
        }
    }

    findNextNotificationForCard(mapping) {
        if (!this.notificationData || !this.notificationData.notifications) return null;

        const now = new Date();

        // البحث عن الإشعارات المناسبة
        const relevantNotifications = this.notificationData.notifications.filter(notification => {
            const notificationTime = new Date(notification.datetime);
            if (notificationTime <= now) return false;

            // فحص نوع الإشعار
            if (mapping.types.includes(notification.type)) {
                // للأشجار، فحص إضافي
                if (notification.type === 'fertilizer' && mapping.tree) {
                    if (Array.isArray(mapping.tree)) {
                        return mapping.tree.includes(notification.tree);
                    } else {
                        return notification.tree === mapping.tree;
                    }
                }
                return true;
            }

            return false;
        });

        // إرجاع أقرب إشعار
        return relevantNotifications.length > 0 ? relevantNotifications[0] : null;
    }

    addCountdownToCard(cardElement, notification, priority) {
        const now = new Date();
        const targetTime = new Date(notification.datetime);
        const timeDiff = targetTime - now;

        if (timeDiff <= 0) return;

        const countdownElement = document.createElement('div');
        countdownElement.className = `card-countdown ${priority}-priority`;

        // حساب الوقت
        const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));

        // تنسيق النص
        const isArabic = this.language === 'ar';
        let timeText = '';
        let labelText = '';

        if (days > 0) {
            timeText = `${days}`;
            labelText = isArabic ? 'يوم' : 'দিন';
        } else if (hours > 0) {
            timeText = `${hours}`;
            labelText = isArabic ? 'ساعة' : 'ঘন্টা';
        } else {
            timeText = `${minutes}`;
            labelText = isArabic ? 'دقيقة' : 'মিনিট';
        }

        // إضافة كلاس للأولوية العالية إذا كان الوقت قريب
        if (days === 0 && hours < 6) {
            countdownElement.classList.add('high-priority');
        }

        countdownElement.innerHTML = `
            <span class="card-countdown-text">${timeText}</span>
            <span class="card-countdown-time">${labelText}</span>
        `;

        // إضافة العداد للبطاقة
        cardElement.style.position = 'relative';
        cardElement.appendChild(countdownElement);
    }

    setLanguage(language) {
        this.language = language;
        this.updateAllCards();
    }

    destroy() {
        this.stopCountdown();
        // إزالة جميع العدادات
        document.querySelectorAll('.card-countdown').forEach(el => el.remove());
    }
}

// تهيئة تلقائية عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // انتظار قليل للتأكد من تحميل البطاقات
    setTimeout(() => {
        const currentLang = document.documentElement.getAttribute('lang') || 'ar';

        // إنشاء مدير العدادات
        window.cardCountdownManager = new CardCountdownManager({
            language: currentLang,
            jsonFile: 'notifications.json'
        });

        // ربط تغيير اللغة
        const langButtons = document.querySelectorAll('.lang-btn');
        langButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const targetLang = this.dataset.lang;
                if (window.cardCountdownManager) {
                    window.cardCountdownManager.setLanguage(targetLang);
                }
            });
        });
    }, 500);
});

// تصدير الكلاس
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CardCountdownManager;
}
