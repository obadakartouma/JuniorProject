Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   إعادة إنشاء venv" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# التحقق من Python
Write-Host "[0/6] التحقق من Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python غير مثبت أو غير موجود في PATH!" -ForegroundColor Red
    Write-Host "يرجى تثبيت Python من https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "اضغط Enter للخروج"
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green
Write-Host ""

# إيقاف venv الحالي
Write-Host "[1/6] إيقاف venv الحالي (إن وجد)..." -ForegroundColor Yellow
if (Get-Command deactivate -ErrorAction SilentlyContinue) {
    deactivate
    Write-Host "✅ تم إيقاف venv" -ForegroundColor Green
} else {
    Write-Host "ℹ️  لا يوجد venv مفعّل حالياً" -ForegroundColor Gray
}

# حذف venv القديم
Write-Host "[2/6] حذف venv القديم..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Remove-Item -Recurse -Force venv
    Write-Host "✅ تم حذف venv القديم" -ForegroundColor Green
} else {
    Write-Host "ℹ️  venv غير موجود" -ForegroundColor Gray
}

# إنشاء venv جديد
Write-Host "[3/6] إنشاء venv جديد..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ خطأ في إنشاء venv!" -ForegroundColor Red
    Write-Host "تأكد من أن Python مثبت بشكل صحيح" -ForegroundColor Yellow
    Read-Host "اضغط Enter للخروج"
    exit 1
}
Write-Host "✅ تم إنشاء venv جديد" -ForegroundColor Green

# تفعيل venv الجديد
Write-Host "[4/6] تفعيل venv الجديد..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ خطأ في تفعيل venv!" -ForegroundColor Red
    Write-Host "حاول تشغيل: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "اضغط Enter للخروج"
    exit 1
}
Write-Host "✅ تم تفعيل venv" -ForegroundColor Green

# التحقق من Python في venv
Write-Host "[5/6] التحقق من Python في venv..." -ForegroundColor Yellow
$venvPython = python --version 2>&1
Write-Host "✅ $venvPython" -ForegroundColor Green

# ترقية pip
Write-Host "[6/6] ترقية pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  تحذير: فشل ترقية pip (قد يكون هذا طبيعياً)" -ForegroundColor Yellow
} else {
    Write-Host "✅ تم ترقية pip" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ venv جاهز الآن!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "الخطوات التالية:" -ForegroundColor Cyan
Write-Host "1. cd projectBPL" -ForegroundColor White
Write-Host "2. pip install -r requirements.txt" -ForegroundColor White
Write-Host "3. python manage.py migrate" -ForegroundColor White
Write-Host "4. python manage.py runserver" -ForegroundColor White
Write-Host ""


