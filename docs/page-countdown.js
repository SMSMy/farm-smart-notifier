/**
 * عداد زمني داخل الصفحات الفردية
 * Individual Page Countdown Timer
 */

class PageCountdownTimer {
  constructor(options = {}) {
    this.jsonFile = options.jsonFile || "notifications.json";
    this.language = options.language || "ar";
    this.pageType = options.pageType || this.detectPageType();
    this.updateInterval = options.updateInterval || 1000;

    this.notificationData = null;
    this.intervalId = null;
    this.container = null;

    this.init();
  }

  init() {
    this.createContainer();
    this.addStyles();
    this.fetchNotificationData();
    this.startCountdown();

    // تحديث البيانات كل 10 دقائق
    setInterval(() => {
      this.fetchNotificationData();
    }, 10 * 60 * 1000);
  }

  detectPageType() {
    const path = window.location.pathname;
    const filename = path.split("/").pop().replace(".html", "");
    return filename || "unknown";
  }

  createContainer() {
    // البحث عن مكان مناسب لإضافة العداد
    const cardElement = document.querySelector(".card");
    if (cardElement) {
      this.container = document.createElement("div");
      this.container.id = "page-countdown-container";
      this.container.className = "page-countdown-timer";

      // إضافة العداد بعد العنوان الرئيسي
      const cardTitle = cardElement.querySelector(".card-title");
      if (cardTitle) {
        cardTitle.parentNode.insertBefore(
          this.container,
          cardTitle.nextSibling
        );
      } else {
        cardElement.insertBefore(this.container, cardElement.firstChild);
      }
    }
  }

  addStyles() {
    if (!document.getElementById("page-countdown-styles")) {
      const style = document.createElement("style");
      style.id = "page-countdown-styles";
      style.textContent = `
                .page-countdown-timer {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 20px;
                    border-radius: 12px;
                    margin: 20px 0;
                    text-align: center;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                    position: relative;
                    overflow: hidden;
                }

                .page-countdown-timer::before {
                    content: '';
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                    animation: gentle-pulse 4s ease-in-out infinite;
                }

                @keyframes gentle-pulse {
                    0%, 100% { transform: scale(1); opacity: 0.3; }
                    50% { transform: scale(1.05); opacity: 0.6; }
                }

                .page-countdown-header {
                    position: relative;
                    z-index: 1;
                    margin-bottom: 12px;
                }

                .page-countdown-title {
                    font-size: 1.1rem;
                    font-weight: 600;
                    margin-bottom: 5px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }

                .page-countdown-subtitle {
                    font-size: 0.85rem;
                    opacity: 0.9;
                }

                .page-countdown-display {
                    position: relative;
                    z-index: 1;
                    display: flex;
                    justify-content: center;
                    gap: 12px;
                    flex-wrap: wrap;
                }

                .page-countdown-unit {
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    padding: 8px 12px;
                    min-width: 50px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }

                .page-countdown-number {
                    font-size: 1.3rem;
                    font-weight: 700;
                    display: block;
                    line-height: 1;
                }

                .page-countdown-label {
                    font-size: 0.7rem;
                    opacity: 0.9;
                    margin-top: 3px;
                }

                .page-countdown-loading {
                    position: relative;
                    z-index: 1;
                    padding: 15px;
                    opacity: 0.8;
                }

                .page-countdown-no-data {
                    position: relative;
                    z-index: 1;
                    background: rgba(108, 117, 125, 0.9);
                    padding: 12px;
                    border-radius: 8px;
                    font-size: 0.85rem;
                }

                .page-countdown-urgent {
                    background: linear-gradient(135deg, #dc3545 0%, #ff6b6b 100%);
                    animation: urgent-pulse 2s ease-in-out infinite;
                }

                .page-countdown-medium {
                    background: linear-gradient(135deg, #ff9800 0%, #ffc107 100%);
                }

                .page-countdown-normal {
                    background: linear-gradient(135deg, #28a745 0%, #4caf50 100%);
                }

                @keyframes urgent-pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                }

                /* تجاوب مع الشاشات الصغيرة */
                @media (max-width: 768px) {
                    .page-countdown-timer {
                        padding: 12px 15px;
                        margin: 15px 0;
                    }

                    .page-countdown-title {
                        font-size: 1rem;
                    }

                    .page-countdown-display {
                        gap: 8px;
                    }

                    .page-countdown-unit {
                        padding: 6px 10px;
                        min-width: 45px;
                    }

                    .page-countdown-number {
                        font-size: 1.1rem;
                    }

                    .page-countdown-label {
                        font-size: 0.65rem;
                    }
                }

                /* للغة البنغالية */
                .lang-bn .page-countdown-timer {
                    direction: ltr;
                }
            `;
      document.head.appendChild(style);
    }
  }

  async fetchNotificationData() {
    try {
      this.showLoading();

      // Check for file protocol
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
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      this.notificationData = data;
      this.updateDisplay();
    } catch (error) {
      console.error("خطأ في جلب بيانات الإشعارات للصفحة:", error);
      this.showNoData(); // Or show a specific error state
    }
  }

  startCountdown() {
    if (this.intervalId) return;

    this.intervalId = setInterval(() => {
      this.updateDisplay();
    }, this.updateInterval);
  }

  stopCountdown() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  updateDisplay() {
    if (!this.notificationData || !this.container) return;

    const relevantNotification = this.findRelevantNotification();

    if (relevantNotification) {
      this.renderCountdown(relevantNotification);
    } else {
      this.showNoData();
    }
  }

  findRelevantNotification() {
    if (!this.notificationData.upcoming_notifications) return null;

    const now = new Date();
    const pageTypeMapping = {
      deworming: ["deworming"],
      vitamins: ["vitamins"],
      sanitization: ["sanitization"],
      coccidiosis: ["coccidiosis"],
      weekly_cleaning: ["weekly_cleaning"],
      soil_turning: ["soil_turning"],
      ventilation: ["ventilation"],
      feeder_cleaning: ["feeder_cleaning"],
      water_station: ["water_station"],
      pipe_waterer: [
        "pipe_waterer_change_water",
        "pipe_waterer_rinse",
        "pipe_waterer_sanitize",
        "pipe_waterer_deep_clean",
      ],
      henna: ["fertilizer"],
      fig: ["fertilizer"],
      banana: ["fertilizer"],
      mango: ["fertilizer"],
      pomegranate: ["fertilizer"],
      grape: ["fertilizer"],
      jackfruit: ["fertilizer"],
      acacia: ["fertilizer"],
      bougainvillea: ["fertilizer"],
      mint: ["fertilizer"],
      moringa: ["fertilizer"],
      custard: ["fertilizer"],
    };

    const relevantTypes = pageTypeMapping[this.pageType] || [];

    // البحث عن الإشعارات المناسبة
    const relevantNotifications =
      this.notificationData.upcoming_notifications.filter((notification) => {
        const notificationTime = new Date(notification.datetime);
        if (notificationTime <= now) return false;

        if (relevantTypes.includes(notification.type)) {
          // للأشجار، فحص إضافي
          if (notification.type === "fertilizer") {
            const treeMapping = {
              henna: "henna",
              fig: "fig",
              banana: "banana",
              mango: ["mango_small", "mango_large"],
              pomegranate: "pomegranate",
              grape: "grape",
              jackfruit: "jackfruit_young",
              acacia: "acacia",
              bougainvillea: "bougainvillea",
              mint: "mint_basil",
              moringa: "moringa",
              custard: "custard_apple",
            };

            const expectedTree = treeMapping[this.pageType];
            if (expectedTree) {
              if (Array.isArray(expectedTree)) {
                return expectedTree.includes(notification.tree);
              } else {
                return notification.tree === expectedTree;
              }
            }
          }
          return true;
        }

        return false;
      });

    return relevantNotifications.length > 0 ? relevantNotifications[0] : null;
  }

  renderCountdown(notification) {
    const now = new Date();
    const targetTime = new Date(notification.datetime);
    const timeDiff = targetTime - now;

    if (timeDiff <= 0) {
      this.showNoData();
      return;
    }

    const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    const hours = Math.floor(
      (timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
    );
    const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

    // تحديد الأولوية والألوان
    let priorityClass = "normal";
    if (days === 0 && hours < 6) {
      priorityClass = "urgent";
    } else if (days < 3) {
      priorityClass = "medium";
    }

    const isArabic = this.language === "ar";
    const title = isArabic
      ? "الإشعار القادم لهذه المهمة"
      : "এই কাজের পরবর্তী বিজ্ঞপ্তি";
    const taskTitle = isArabic ? notification.title_ar : notification.title_bn;

    const labels = isArabic
      ? { days: "يوم", hours: "ساعة", minutes: "دقيقة", seconds: "ثانية" }
      : { days: "দিন", hours: "ঘন্টা", minutes: "মিনিট", seconds: "সেকেন্ড" };

    this.container.className = `page-countdown-timer page-countdown-${priorityClass}`;

    this.container.innerHTML = `
            <div class="page-countdown-header">
                <div class="page-countdown-title">
                    ${notification.icon} ${title}
                </div>
                <div class="page-countdown-subtitle">
                    ${taskTitle}
                </div>
            </div>
            <div class="page-countdown-display">
                ${
                  days > 0
                    ? `
                    <div class="page-countdown-unit">
                        <span class="page-countdown-number">${days}</span>
                        <div class="page-countdown-label">${labels.days}</div>
                    </div>
                `
                    : ""
                }
                <div class="page-countdown-unit">
                    <span class="page-countdown-number">${hours}</span>
                    <div class="page-countdown-label">${labels.hours}</div>
                </div>
                <div class="page-countdown-unit">
                    <span class="page-countdown-number">${minutes}</span>
                    <div class="page-countdown-label">${labels.minutes}</div>
                </div>
                <div class="page-countdown-unit">
                    <span class="page-countdown-number">${seconds}</span>
                    <div class="page-countdown-label">${labels.seconds}</div>
                </div>
            </div>
        `;
  }

  showLoading() {
    if (!this.container) return;

    const isArabic = this.language === "ar";
    const message = isArabic ? "جاري تحميل البيانات..." : "ডেটা লোড হচ্ছে...";

    this.container.innerHTML = `
            <div class="page-countdown-loading">
                ⏳ ${message}
            </div>
        `;
  }

  showNoData() {
    if (!this.container) return;

    const isArabic = this.language === "ar";
    const message = isArabic
      ? "لا توجد إشعارات مجدولة لهذه المهمة حالياً"
      : "এই কাজের জন্য বর্তমানে কোনো বিজ্ঞপ্তি নির্ধারিত নেই";

    this.container.innerHTML = `
            <div class="page-countdown-no-data">
                📅 ${message}
            </div>
        `;
  }

  setLanguage(language) {
    this.language = language;
    this.updateDisplay();
  }

  destroy() {
    this.stopCountdown();
    if (this.container) {
      this.container.remove();
    }
  }
}

// تهيئة تلقائية عند تحميل الصفحة
document.addEventListener("DOMContentLoaded", function () {
  // التأكد من أننا في صفحة فردية وليس الصفحة الرئيسية
  if (
    window.location.pathname.includes("index.html") ||
    window.location.pathname.endsWith("/")
  ) {
    return; // لا نضيف العداد في الصفحة الرئيسية
  }

  setTimeout(() => {
    const currentLang = document.documentElement.getAttribute("lang") || "ar";

    // إنشاء عداد الصفحة
    window.pageCountdownTimer = new PageCountdownTimer({
      language: currentLang,
      jsonFile: "notifications.json",
    });

    // ربط تغيير اللغة
    const langButtons = document.querySelectorAll(".lang-btn");
    langButtons.forEach((btn) => {
      btn.addEventListener("click", function () {
        const targetLang = this.dataset.lang;
        if (window.pageCountdownTimer) {
          window.pageCountdownTimer.setLanguage(targetLang);
        }
      });
    });
  }, 500);
});

// تصدير الكلاس
if (typeof module !== "undefined" && module.exports) {
  module.exports = PageCountdownTimer;
}
