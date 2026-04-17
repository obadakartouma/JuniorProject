# 🔧 حل مشكلة venv - Python من جهاز آخر

## ❌ المشكلة

إذا ظهرت رسالة خطأ مثل:
```
No Python at '"C:\Users\LENOVO\AppData\Local\Programs\Python\Python312\python.exe'
```

هذا يعني أن **venv تم إنشاؤه على جهاز آخر** (LENOVO) والآن أنت على جهاز مختلف (bassa).

---

## ✅ الحل: إعادة إنشاء venv

### الطريقة 1: استخدام ملف PowerShell (موصى به)

1. افتح PowerShell في مجلد `backendPBL`
2. نفذ الأمر التالي:

```powershell
.\recreate_venv.ps1
```

**إذا ظهرت رسالة خطأ حول "Execution Policy":**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
ثم حاول مرة أخرى.

### الطريقة 2: استخدام ملف .bat

1. افتح مجلد `backendPBL`
2. انقر نقراً مزدوجاً على `recreate_venv.bat`

### الطريقة 3: يدوياً

```powershell
# 1. حذف venv القديم
Remove-Item -Recurse -Force venv

# 2. إنشاء venv جديد
python -m venv venv

# 3. تفعيل venv
.\venv\Scripts\Activate.ps1

# 4. ترقية pip
python -m pip install --upgrade pip

# 5. الانتقال لمجلد المشروع وتثبيت الحزم
cd projectBPL
pip install -r requirements.txt
```

---

## 📝 الخطوات بعد إعادة إنشاء venv

بعد إعادة إنشاء venv، نفذ الخطوات التالية:

```powershell
# 1. الانتقال لمجلد المشروع
cd projectBPL

# 2. تثبيت الحزم
pip install -r requirements.txt

# 3. تطبيق migrations
python manage.py migrate

# 4. تشغيل السيرفر
python manage.py runserver
```

---

## ✅ التحقق من أن venv يعمل

بعد تفعيل venv، نفذ:

```powershell
python --version
```

يجب أن ترى إصدار Python بدون أخطاء.

---

## ⚠️ ملاحظات مهمة

1. **لا تحذف venv** إلا إذا كنت متأكداً من إعادة إنشائه
2. **احتفظ بنسخة من requirements.txt** - ستحتاجها لإعادة تثبيت الحزم
3. **بعد إعادة إنشاء venv**، ستحتاج لتثبيت جميع الحزم مرة أخرى

---

## 🎯 ملخص سريع

```powershell
# في مجلد backendPBL:
.\recreate_venv.ps1
cd projectBPL
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**بالتوفيق! 🚀**

