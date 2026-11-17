# MediPredict AI

An educational medical decision-support prototype using a transparent Bayesian Network-style probabilistic model.

## Requirements
- Windows 10/11
- Python 3.10 or newer
- VS Code

## Run on Windows (PowerShell)
```powershell
cd path\to\MediPredict_AI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Mobile
The site is responsive. On Android Chrome, open the site using your computer's local network IP (same Wi-Fi), then use Chrome menu > Add to Home screen. For public installation, deploy behind HTTPS first. This PWA is a mobile-friendly web app, not a native APK.

## Important safety note
This is a student/educational prototype. Its probability tables are illustrative and not clinically validated. It must not be used to diagnose, rule out disease, recommend treatment, or delay care. A clinician must assess symptoms and medical history. Chest pain or breathing difficulty requires urgent medical assessment.

## Before real deployment
- Replace `app.secret_key` with a long random secret stored in an environment variable.
- Use HTTPS, secure cookies, CSRF protection, rate limiting and production hosting.
- Add consent, privacy policy, retention/deletion controls and access auditing.
- Have clinicians validate the model using representative, high-quality datasets and external testing.
- Do not collect real patient data in this demo.
