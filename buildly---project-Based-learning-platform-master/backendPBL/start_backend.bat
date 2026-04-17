@echo off
echo ========================================
echo    تشغيل الباك إند - Django Server
echo ========================================
echo.

REM تفعيل البيئة الافتراضية
echo [1/3] تفعيل البيئة الافتراضية...
call venv\Scripts\activate.bat

REM الانتقال لمجلد المشروع
echo [2/3] الانتقال لمجلد المشروع...
cd projectBPL

REM تشغيل السيرفر
echo [3/3] تشغيل السيرفر...
echo.
echo الباك إند يعمل الآن على: http://localhost:8000
echo اضغط CTRL+C لإيقاف السيرفر
echo.
python manage.py runserver

pause


