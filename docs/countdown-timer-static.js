/**
 * عداد زمني للإشعارات القادمة - نسخة GitHub Pages
 * Farm Notifier Countdown Timer - GitHub Pages Version
 */

class FarmNotifierCountdownStatic {
  constructor(options = {}) {
    this.jsonFile = options.jsonFile || "notifications.json";
    this.containerId = options.containerId || "countdown-container";
    this.updateInterval = options.updateInterval || 1000; // تحديث كل ثانية
    this.language = options.language || "ar";

    this.container = null;
    this.intervalId = null;
    this.notificationData = null;
    this.isRunning = false;

    this.init();
  }

  init() {
    this.createContainer();
    this.fetchNotificationData();
    this.startCountdown();

    // تحديث البيانات كل 10 دقائق
    setInterval(() => {
      this.fetchNotificationData();
    }, 10 * 60 * 1000);
  }

  createContainer() {
    // البحث عن الحاوية الموجودة أو إنشاء واحدة جديدة
    this.container = document.getElementById(this.containerId);

    if (!this.container) {
      this.container = document.createElement("div");
      this.container.id = this.containerId;
      this.container.className = "countdown-timer";

      // إضافة الحاوية إلى أعلى الصفحة
      const header = document.querySelector("header");
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
    if (!document.getElementById("countdown-styles")) {
      const style = document.createElement("style");
      style.id = "countdown-styles";
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

                .countdown-info {
                    position: relative;
                    z-index: 1;
                    background: rgba(23, 162, 184, 0.9);
                    padding: 10px;
                    border-radius: 8px;
                    margin-top: 10px;
                    font-size: 0.8rem;
                }

                .color-guide {
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    margin-top: 8px;
                    flex-wrap: wrap;
                }

                .color-item {
                    background: rgba(255, 255, 255, 0.2);
                    padding: 3px 8px;
                    border-radius: 12px;
                    font-size: 0.7rem;
                    font-weight: 600;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }

                .color-item.urgent {
                    background: rgba(220, 53, 69, 0.8);
                }

                .color-item.medium {
                    background: rgba(255, 152, 0, 0.8);
                }

                .color-item.normal {
                    background: rgba(40, 167, 69, 0.8);
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

  async fetchNotificationData() {
    try {
      this.showLoading();

      // Check for file protocol which might block fetch
      if (window.location.protocol === "file:") {
        console.warn(
          "Running via file:// protocol. Fetch might fail due to CORS."
        );
      }

      // Create a timeout promise
      const timeout = new Promise((_, reject) => {
        setTimeout(() => reject(new Error("Request timed out (10s)")), 10000);
      });

      // Race between fetch and timeout
      const response = await Promise.race([fetch(this.jsonFile), timeout]);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("Countdown data loaded:", data); // Debug log
      this.notificationData = data;
      this.updateDisplay();
    } catch (error) {
      console.error("Error fetching notification data:", error);
      this.showError(error.message);
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
    if (
      !this.notificationData ||
      !this.notificationData.countdown.next_notification
    ) {
      return;
    }

    const now = new Date();
    const targetTime = new Date(
      this.notificationData.countdown.next_notification.datetime
    );
    const timeDiff = targetTime - now;

    if (timeDiff <= 0) {
      // انتهى الوقت، إعادة جلب البيانات
      this.fetchNotificationData();
      return;
    }

    const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    const hours = Math.floor(
      (timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
    );
    const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

    this.renderCountdown({ days, hours, minutes, seconds });
  }

  updateDisplay() {
    if (!this.notificationData) {
      this.showError("لا توجد بيانات");
      return;
    }

    if (!this.notificationData.countdown.next_notification) {
      this.showNoNotifications();
      return;
    }

    this.updateCountdown();
  }

  renderCountdown(time) {
    const isArabic = this.language === "ar";
    const title = isArabic ? "الإشعار القادم" : "পরবর্তী বিজ্ঞপ্তি";
    const nextNotification = this.notificationData.countdown.next_notification;
    const taskTitle = isArabic
      ? nextNotification.title_ar
      : nextNotification.title_bn;

    const labels = isArabic
      ? { days: "يوم", hours: "ساعة", minutes: "دقيقة", seconds: "ثانية" }
      : { days: "দিন", hours: "ঘন্টা", minutes: "মিনিট", seconds: "সেকেন্ড" };

    // معلومات إضافية
    const generatedAt = new Date(this.notificationData.generated_at);
    const infoText = isArabic
      ? `آخر تحديث: ${generatedAt.toLocaleString("ar")}`
      : `সর্বশেষ আপডেট: ${generatedAt.toLocaleString("bn")}`;

    // شرح الألوان
    const colorGuideAr = `
            <div class="color-guide">
                <span class="color-item urgent">🔴 عاجل</span>
                <span class="color-item medium">🟡 متوسط</span>
                <span class="color-item normal">🟢 عادي</span>
            </div>
        `;

    const colorGuideBn = `
            <div class="color-guide">
                <span class="color-item urgent">🔴 জরুরি</span>
                <span class="color-item medium">🟡 মাঝারি</span>
                <span class="color-item normal">🟢 সাধারণ</span>
            </div>
        `;

    this.container.innerHTML = `
            <div class="countdown-header">
                <div class="countdown-title">
                    ${nextNotification.icon} ${title}
                </div>
                <div class="countdown-next-task">
                    ${taskTitle}
                </div>
                ${isArabic ? colorGuideAr : colorGuideBn}
            </div>
            <div class="countdown-display">
                ${
                  time.days > 0
                    ? `
                    <div class="countdown-unit">
                        <span class="countdown-number">${time.days}</span>
                        <div class="countdown-label">${labels.days}</div>
                    </div>
                `
                    : ""
                }
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
            <div class="countdown-info">
                ${infoText} | ${this.notificationData.total_count} إشعار مجدول
            </div>
        `;
  }

  showLoading() {
    const isArabic = this.language === "ar";
    const message = isArabic ? "جاري تحميل البيانات..." : "ডেটা লোড হচ্ছে...";

    this.container.innerHTML = `
            <div class="countdown-loading">
                ⏳ ${message}
            </div>
        `;
  }

  showError(error) {
    const isArabic = this.language === "ar";
    const message = isArabic ? "خطأ في تحميل البيانات" : "ডেটা লোড করতে ত্রুটি";

    this.container.innerHTML = `
            <div class="countdown-error">
                ❌ ${message}
                <br><small>${error}</small>
                <br><small>تأكد من وجود ملف ${this.jsonFile}</small>
            </div>
        `;
  }

  showNoNotifications() {
    const isArabic = this.language === "ar";
    const message = isArabic
      ? "لا توجد إشعارات مجدولة خلال الشهر القادم"
      : "আগামী মাসে কোনো বিজ্ঞপ্তি নির্ধারিত নেই";

    this.container.innerHTML = `
            <div class="countdown-no-notifications">
                ✅ ${message}
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
document.addEventListener("DOMContentLoaded", function () {
  // تحديد اللغة الحالية
  const currentLang = document.documentElement.getAttribute("lang") || "ar";

  // إنشاء العداد
  window.farmCountdownStatic = new FarmNotifierCountdownStatic({
    language: currentLang,
    jsonFile: "notifications.json",
  });

  // ربط تغيير اللغة بالعداد
  const langButtons = document.querySelectorAll(".lang-btn");
  langButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const targetLang = this.dataset.lang;
      if (window.farmCountdownStatic) {
        window.farmCountdownStatic.setLanguage(targetLang);
      }
    });
  });
});

// تصدير الكلاس للاستخدام الخارجي
if (typeof module !== "undefined" && module.exports) {
  module.exports = FarmNotifierCountdownStatic;
}
