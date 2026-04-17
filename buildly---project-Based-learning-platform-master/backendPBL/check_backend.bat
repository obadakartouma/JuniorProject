@echo off
echo ========================================
echo    التحقق من الباك إند
echo ========================================
echo.

echo جاري التحقق من الباك إند على http://localhost:8000...
echo.

curl -s http://localhost:8000 > nul 2>&1

if %errorlevel% == 0 (
    echo.
    echo ✅ الباك إند يعمل بشكل صحيح!
    echo.
    echo يمكنك فتح المتصفح على: http://localhost:8000
    echo.
) else (
    echo.
    echo ❌ الباك إند لا يعمل
    echo.
    echo تأكد من:
    echo 1. تشغيل الباك إند باستخدام: start_backend.bat
    echo 2. عدم وجود أخطاء في Terminal
    echo.
)

pause


