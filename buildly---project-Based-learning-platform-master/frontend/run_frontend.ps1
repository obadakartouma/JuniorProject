# Script لتشغيل الفرونت إند
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   تشغيل الفرونت إند - React/Vite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# التحقق من Node.js
Write-Host "[1/3] التحقق من Node.js..." -ForegroundColor Yellow
node --version

# تثبيت الحزم (إذا لم تكن مثبتة)
Write-Host "[2/3] التحقق من الحزم..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "تثبيت الحزم..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "الحزم مثبتة بالفعل" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   تشغيل السيرفر..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "الفرونت إند يعمل الآن على: http://localhost:3000" -ForegroundColor Green
Write-Host "اضغط CTRL+C لإيقاف السيرفر" -ForegroundColor Yellow
Write-Host ""

# تشغيل السيرفر
npm run dev


