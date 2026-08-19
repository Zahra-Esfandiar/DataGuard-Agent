# 🛡️ DataGuard Agent

این بار پروژه برای دیتاست ساختگی نیست؛ کاربر **دیتاست واقعی خودش** را وارد می‌کند.

DataGuard قبل از مدل‌سازی بررسی می‌کند:
- Missing Value
- Duplicate
- IDهای تکراری
- Typeهای اشتباه
- Dateهای خراب
- Labelهای ناسازگار
- Outlier
- Rare Category
- High Cardinality
- Target Leakage احتمالی
- Class Imbalance
- Split اشتباه
- Data Drift بین Training و Production

## دو حالت اصلی

### 1) Single Dataset Audit
فایل واقعی را Upload کن و Data Readiness Report بگیر.

### 2) Reference vs Current Drift
مثلاً Training Data و Production Data را Upload کن و Schema/Distribution Drift را بررسی کن.

## Gemini اختیاری است

هسته اصلی پروژه بدون API هم کار می‌کند.

اگر Gemini را روشن کنی، **دیتای خام ارسال نمی‌شود**؛ فقط خروجی فشرده Audit برای Reviewer ارسال می‌شود تا مشکلات را اولویت‌بندی و توضیح دهد.

## خروجی‌ها

- Readiness Score
- Issue table با Severity + Evidence + Recommendation
- Leakage warnings
- Split recommendation
- Quick EDA
- Cleaning starter
- Validation spec
- Markdown / HTML report
- Drift report

## اجرای ویندوز

1. ZIP را Extract کن.
2. `install_windows.bat` را اجرا کن.
3. `run_windows.bat` را اجرا کن.
4. دیتاست واقعی را Upload کن.
5. در صورت نیاز Target، ID و Time را مشخص کن.
6. `Run DataGuard Audit` را بزن.

فلسفه پروژه:

> **Detect deterministically. Explain with AI.**
