# Get current project directory
$projectDir = Get-Location

Write-Host "🚀 Starting Readora AI (Backend + Frontend)..." -ForegroundColor Cyan

# 1. Start FastAPI Backend in a background process
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectDir\backend'; Set-ExecutionPolicy Unrestricted -Scope Process; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload" -PassThru

# 2. Wait a few seconds for FastAPI server to initialize
Start-Sleep -Seconds 3

# 3. Start Streamlit Frontend in the main terminal window
cd "$projectDir\backend"
Set-ExecutionPolicy Unrestricted -Scope Process
.\venv\Scripts\Activate.ps1
cd "$projectDir"
streamlit run FrontEnd/abc.py