# استخدم Python الرسمي
FROM python:3.12

# إعداد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي المشروع
COPY . .

# فتح البورت
EXPOSE 8000

# أمر التشغيل
CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]
