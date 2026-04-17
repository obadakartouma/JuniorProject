# Script لتشغيل الباك إند
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   تشغيل الباك إند - Django Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# التحقق من وجود venv
Write-Host "[0/5] التحقق من venv..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "❌ venv غير موجود!" -ForegroundColor Red
    Write-Host "يرجى تشغيل: .\recreate_venv.ps1 أولاً" -ForegroundColor Yellow
    Read-Host "اضغط Enter للخروج"
    exit 1
}

# التحقق من Python في النظام
Write-Host "[1/5] التحقق من Python..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python غير مثبت أو غير موجود في PATH!" -ForegroundColor Red
    Read-Host "اضغط Enter للخروج"
    exit 1
}
Write-Host "✅ $pythonCheck" -ForegroundColor Green

# تفعيل البيئة الافتراضية
Write-Host "[2/5] تفعيل البيئة الافتراضية..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        throw "فشل تفعيل venv"
    }
} catch {
    Write-Host "❌ خطأ في تفعيل venv!" -ForegroundColor Red
    Write-Host "المشكلة: venv قد يكون من جهاز آخر" -ForegroundColor Yellow
    Write-Host "الحل: شغّل .\recreate_venv.ps1 لإعادة إنشاء venv" -ForegroundColor Yellow
    Read-Host "اضغط Enter للخروج"
    exit 1
}

# التحقق من Python في venv
Write-Host "[3/5] التحقق من Python في venv..." -ForegroundColor Yellow
$venvPython = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python لا يعمل في venv!" -ForegroundColor Red
    Write-Host "يرجى إعادة إنشاء venv: .\recreate_venv.ps1" -ForegroundColor Yellow
    Read-Host "اضغط Enter للخروج"
    exit 1
}
Write-Host "✅ $venvPython" -ForegroundColor Green

# الانتقال لمجلد المشروع
Write-Host "[4/5] الانتقال لمجلد المشروع..." -ForegroundColor Yellow
Set-Location projectBPL

# تطبيق migrations
Write-Host "[5/5] تطبيق migrations..." -ForegroundColor Yellow
python manage.py migrate

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   تشغيل السيرفر..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "الباك إند يعمل الآن على: http://localhost:8000" -ForegroundColor Green
Write-Host "اضغط CTRL+C لإيقاف السيرفر" -ForegroundColor Yellow
Write-Host ""

# تشغيل السيرفر
python manage.py runserver


