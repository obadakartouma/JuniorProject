Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   تشغيل الباك إند - Django Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# تفعيل البيئة الافتراضية
Write-Host "[1/3] تفعيل البيئة الافتراضية..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# الانتقال لمجلد المشروع
Write-Host "[2/3] الانتقال لمجلد المشروع..." -ForegroundColor Yellow
Set-Location projectBPL

# تشغيل السيرفر
Write-Host "[3/3] تشغيل السيرفر..." -ForegroundColor Yellow
Write-Host ""
Write-Host "الباك إند يعمل الآن على: http://localhost:8000" -ForegroundColor Green
Write-Host "اضغط CTRL+C لإيقاف السيرفر" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver


