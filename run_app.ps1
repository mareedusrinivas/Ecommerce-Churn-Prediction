# Ecommerce Churn Prediction Master Startup Script

Write-Host '🔧 Activating environment...' -ForegroundColor Cyan
if (Test-Path '.\.venv\Scripts\Activate.ps1') {
    . .\.venv\Scripts\Activate.ps1
}

Write-Host '🧠 Preparing ML Model...' -ForegroundColor Cyan
python create_models.py

Write-Host '🚀 Starting Flask Backend (Port 5000)...' -ForegroundColor Green
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'python main.py'

Write-Host '🎨 Starting React Frontend (Port 5173)...' -ForegroundColor Green
$frontend_cmd = 'cd frontend; npm run dev'
Start-Process powershell -ArgumentList '-NoExit', '-Command', $frontend_cmd

Write-Host '✅ All systems are starting!' -ForegroundColor Green
Write-Host '-----------------------------------------'
Write-Host 'Backend:  http://127.0.0.1:5000'
Write-Host 'Frontend: http://localhost:5173'
Write-Host '-----------------------------------------'
