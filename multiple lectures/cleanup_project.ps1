# Smart LMS - Project Cleanup Script
# Removes legacy files and organizes the project structure

Write-Host "🧹 Starting Smart LMS Project Cleanup..." -ForegroundColor Cyan
Write-Host ""

# Create directories if they don't exist
Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
$directories = @(
    "legacy",
    "data_archive",
    "app\pages",
    "services",
    "ml\models",
    "storage\courses",
    "storage\assignments",
    "storage\attendance",
    "scripts"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}

# Archive legacy Flask files
Write-Host "📦 Archiving legacy Flask files..." -ForegroundColor Yellow
$legacyFiles = @(
    "app.py",
    "app1.py",
    "balance.py",
    "label-engage.py",
    "model-trining.py",
    "prediction.py",
    "refine-data.py",
    "train-accu.py"
)

foreach ($file in $legacyFiles) {
    if (Test-Path $file) {
        Copy-Item $file "legacy\" -Force
        Write-Host "  ✓ Archived: $file" -ForegroundColor Green
    }
}

# Archive legacy directories
Write-Host "📦 Archiving legacy directories..." -ForegroundColor Yellow
$legacyDirs = @(
    "templates",
    "static",
    "multiple",
    "backend"
)

foreach ($dir in $legacyDirs) {
    if (Test-Path $dir) {
        Copy-Item $dir "legacy\" -Recurse -Force
        Write-Host "  ✓ Archived: $dir" -ForegroundColor Green
    }
}

# Archive CSV and PKL files
Write-Host "📊 Archiving data files..." -ForegroundColor Yellow
Get-ChildItem -Filter "*.csv" | ForEach-Object {
    Copy-Item $_.FullName "data_archive\" -Force
    Write-Host "  ✓ Archived: $($_.Name)" -ForegroundColor Green
}

Get-ChildItem -Filter "*.pkl" | ForEach-Object {
    Copy-Item $_.FullName "data_archive\" -Force
    Write-Host "  ✓ Archived: $($_.Name)" -ForegroundColor Green
}

# Remove redundant files
Write-Host "🗑️  Removing redundant files..." -ForegroundColor Yellow
$filesToRemove = @(
    "events.csv",
    "realtime-data.csv",
    "multiple.zip"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✓ Removed: $file" -ForegroundColor Green
    }
}

# Clean Python cache
Write-Host "🧼 Cleaning Python cache..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Directory -Filter ".ipynb_checkpoints" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
Write-Host "  ✓ Python cache cleaned" -ForegroundColor Green

# Clean IDE files
Write-Host "🧼 Cleaning IDE files..." -ForegroundColor Yellow
if (Test-Path ".idea") {
    Remove-Item ".idea" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Removed .idea" -ForegroundColor Green
}

if (Test-Path ".vscode") {
    Remove-Item ".vscode" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Removed .vscode" -ForegroundColor Green
}

# Remove empty directories
Write-Host "🗑️  Removing empty directories..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory | Where-Object { 
    (Get-ChildItem $_.FullName -Force | Measure-Object).Count -eq 0 
} | Remove-Item -Force -ErrorAction SilentlyContinue

# Organize videos if they exist
Write-Host "🎥 Organizing video files..." -ForegroundColor Yellow
if (Test-Path "static\videos") {
    $videoMapping = @{
        "Lec_video.mp4" = "storage\courses\computer_vision\lectures"
        "CV_L2.mp4" = "storage\courses\computer_vision\lectures"
        "CNS_Lec_1.mp4" = "storage\courses\cryptography\lectures"
        "CNS_Lec_2.mp4" = "storage\courses\cryptography\lectures"
        "Lec_1.mp4" = "storage\courses\data_science\lectures"
    }
    
    foreach ($video in $videoMapping.Keys) {
        $sourcePath = "static\videos\$video"
        $destPath = $videoMapping[$video]
        
        if (Test-Path $sourcePath) {
            New-Item -ItemType Directory -Force -Path $destPath | Out-Null
            Copy-Item $sourcePath "$destPath\$video" -Force
            Write-Host "  ✓ Organized: $video" -ForegroundColor Green
        }
    }
}

# Summary
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 58 -ForegroundColor Cyan
Write-Host "✅ Cleanup Complete!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 58 -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   ✓ Legacy files archived to: .\legacy\" -ForegroundColor White
Write-Host "   ✓ Data files archived to: .\data_archive\" -ForegroundColor White
Write-Host "   ✓ Python cache cleaned" -ForegroundColor White
Write-Host "   ✓ IDE files removed" -ForegroundColor White
Write-Host "   ✓ Videos organized in: .\storage\courses\" -ForegroundColor White
Write-Host ""

Write-Host "📁 Current Project Structure:" -ForegroundColor Cyan
Write-Host "   .\app\                    - Streamlit application" -ForegroundColor White
Write-Host "   .\services\               - Backend services" -ForegroundColor White
Write-Host "   .\storage\                - JSON data storage" -ForegroundColor White
Write-Host "   .\ml\models\              - ML models" -ForegroundColor White
Write-Host "   .\scripts\                - Utility scripts" -ForegroundColor White
Write-Host "   .\legacy\                 - Archived old files" -ForegroundColor White
Write-Host "   .\data_archive\           - Archived data files" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Run: python scripts\init_storage.py" -ForegroundColor White
Write-Host "   2. Run: streamlit run app\streamlit_app.py" -ForegroundColor White
Write-Host ""
