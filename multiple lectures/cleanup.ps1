# Smart LMS Cleanup Script (PowerShell)
Write-Host "🧹 Starting Smart LMS cleanup..." -ForegroundColor Cyan

# 1. Create new directory structure
Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "legacy" | Out-Null
New-Item -ItemType Directory -Force -Path "data_archive" | Out-Null
New-Item -ItemType Directory -Force -Path "app\pages" | Out-Null
New-Item -ItemType Directory -Force -Path "services" | Out-Null
New-Item -ItemType Directory -Force -Path "ml\models" | Out-Null
New-Item -ItemType Directory -Force -Path "storage\courses" | Out-Null
New-Item -ItemType Directory -Force -Path "storage\assignments" | Out-Null
New-Item -ItemType Directory -Force -Path "storage\attendance" | Out-Null

# 2. Archive legacy files
Write-Host "📦 Archiving legacy files..." -ForegroundColor Yellow
if (Test-Path "app1.py") { Move-Item "app1.py" "legacy\" -Force }
if (Test-Path "multiple") { Move-Item "multiple" "legacy\" -Force }
if (Test-Path "model-trining.py") { Move-Item "model-trining.py" "legacy\" -Force }
if (Test-Path "prediction.py") { Move-Item "prediction.py" "legacy\" -Force }
if (Test-Path "engagement_model.pkl") { Move-Item "engagement_model.pkl" "legacy\" -Force }

# 3. Archive Flask app and templates (keep for reference)
Write-Host "📦 Archiving Flask app..." -ForegroundColor Yellow
if (Test-Path "app.py") { Copy-Item "app.py" "legacy\" -Force }
if (Test-Path "templates") { Copy-Item "templates" "legacy\" -Recurse -Force }
if (Test-Path "static") { Copy-Item "static" "legacy\" -Recurse -Force }

# 4. Remove redundant files
Write-Host "🗑️  Removing redundant files..." -ForegroundColor Yellow
if (Test-Path "events.csv") { Remove-Item "events.csv" -Force }
if (Test-Path "realtime-data.csv") { Remove-Item "realtime-data.csv" -Force }
if (Test-Path "backend") { Remove-Item "backend" -Force -ErrorAction SilentlyContinue }

# 5. Archive CSV data
Write-Host "📊 Archiving CSV data..." -ForegroundColor Yellow
Get-ChildItem -Filter "*.csv" | Copy-Item -Destination "data_archive\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Filter "*.pkl" | Copy-Item -Destination "data_archive\" -Force -ErrorAction SilentlyContinue

# 6. Clean Python cache
Write-Host "🧼 Cleaning Python cache..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Directory -Filter ".ipynb_checkpoints" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

# 7. Organize videos
Write-Host "🎥 Organizing video files..." -ForegroundColor Yellow
if (Test-Path "static\videos") {
    New-Item -ItemType Directory -Force -Path "storage\courses\computer_vision\lectures" | Out-Null
    New-Item -ItemType Directory -Force -Path "storage\courses\cryptography\lectures" | Out-Null
    New-Item -ItemType Directory -Force -Path "storage\courses\data_science\lectures" | Out-Null
    
    # Copy videos to organized structure
    if (Test-Path "static\videos\Lec_video.mp4") { Copy-Item "static\videos\Lec_video.mp4" "storage\courses\computer_vision\lectures\" -Force }
    if (Test-Path "static\videos\CV_L2.mp4") { Copy-Item "static\videos\CV_L2.mp4" "storage\courses\computer_vision\lectures\" -Force }
    if (Test-Path "static\videos\CNS_Lec_1.mp4") { Copy-Item "static\videos\CNS_Lec_1.mp4" "storage\courses\cryptography\lectures\" -Force }
    if (Test-Path "static\videos\CNS_Lec_2.mp4") { Copy-Item "static\videos\CNS_Lec_2.mp4" "storage\courses\cryptography\lectures\" -Force }
    if (Test-Path "static\videos\Lec_1.mp4") { Copy-Item "static\videos\Lec_1.mp4" "storage\courses\data_science\lectures\" -Force }
}

Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   - Legacy files moved to: .\legacy\" -ForegroundColor White
Write-Host "   - CSV data archived to: .\data_archive\" -ForegroundColor White
Write-Host "   - New structure created: .\app\, .\services\, .\ml\, .\storage\" -ForegroundColor White
Write-Host "   - Videos organized in: .\storage\courses\" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Ready for Smart LMS development!" -ForegroundColor Green
