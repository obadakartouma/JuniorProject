@echo off
echo ========================================
echo    إعادة إنشاء venv
echo ========================================
echo.

echo [1/5] إيقاف venv الحالي...
call venv\Scripts\deactivate.bat 2>nul

echo [2/5] حذف venv القديم...
if exist venv (
    rmdir /s /q venv
    echo تم حذف venv القديم
) else (
    echo venv غير موجود
)

echo [3/5] إنشاء venv جديد...
python -m venv venv
if errorlevel 1 (
    echo خطأ في إنشاء venv!
    pause
    exit /b 1
)

echo [4/5] تفعيل venv الجديد...
call venv\Scripts\activate.bat

echo [5/5] ترقية pip...
python -m pip install --upgrade pip

echo.
echo ========================================
echo    venv جاهز الآن!
echo ========================================
echo.
echo الخطوة التالية:
echo 1. cd projectBPL
echo 2. pip install -r requirements.txt
echo.

pause


