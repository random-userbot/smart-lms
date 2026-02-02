# Smart LMS - Advanced Features Setup Script (PowerShell)
# Run this script to set up all new advanced features

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 Smart LMS - Advanced Features Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
$venvPath = ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    & $venvPath
    Write-Host "   ✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠️  No virtual environment found at .venv" -ForegroundColor Yellow
    Write-Host "   Continuing with system Python..." -ForegroundColor Yellow
}

Write-Host ""

# Install dependencies
Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
$packages = @("groq", "plotly", "pandas")

foreach ($package in $packages) {
    Write-Host "   Installing $package..." -ForegroundColor Gray
    python -m pip install $package --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $package installed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Failed to install $package" -ForegroundColor Red
    }
}

Write-Host ""

# Create storage directories
Write-Host "📁 Creating storage directories..." -ForegroundColor Yellow
$directories = @("storage", "ml_data\activity_logs")

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   ✅ Created $dir" -ForegroundColor Green
    } else {
        Write-Host "   ✅ $dir exists" -ForegroundColor Green
    }
}

Write-Host ""

# Check for config file
Write-Host "📝 Checking configuration..." -ForegroundColor Yellow
if (Test-Path "config.yaml") {
    Write-Host "   ✅ config.yaml found" -ForegroundColor Green
    
    # Check for required settings
    $configContent = Get-Content "config.yaml" -Raw
    $requiredSettings = @("activity_tracking", "session_tracking", "teaching_scores")
    $missing = @()
    
    foreach ($setting in $requiredSettings) {
        if ($configContent -notmatch $setting) {
            $missing += $setting
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Host "   ⚠️  Missing storage paths in config.yaml:" -ForegroundColor Yellow
        foreach ($item in $missing) {
            Write-Host "      - $item" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "   💡 Add these to the storage section of config.yaml:" -ForegroundColor Cyan
        Write-Host "   storage:" -ForegroundColor Gray
        Write-Host "     activity_tracking: `"./storage/activity_tracking.json`"" -ForegroundColor Gray
        Write-Host "     session_tracking: `"./storage/session_tracking.json`"" -ForegroundColor Gray
        Write-Host "     teaching_scores: `"./storage/teaching_scores.json`"" -ForegroundColor Gray
        Write-Host "     student_analytics: `"./storage/student_analytics.json`"" -ForegroundColor Gray
    } else {
        Write-Host "   ✅ All required storage paths found" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️  config.yaml not found" -ForegroundColor Yellow
    Write-Host "   💡 Copy config.example.yaml to config.yaml and update it" -ForegroundColor Cyan
}

Write-Host ""

# Check for API key
Write-Host "🔑 Checking API keys..." -ForegroundColor Yellow
$groqKey = $env:GROQ_API_KEY

if ($groqKey) {
    Write-Host "   ✅ GROQ_API_KEY found in environment" -ForegroundColor Green
} elseif ((Test-Path "config.yaml") -and ((Get-Content "config.yaml" -Raw) -match "groq:.*gsk_")) {
    Write-Host "   ✅ GROQ_API_KEY found in config.yaml" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  GROQ_API_KEY not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   💡 To enable AI Chatbot:" -ForegroundColor Cyan
    Write-Host "   1. Get free API key: https://console.groq.com/keys" -ForegroundColor Gray
    Write-Host "   2. Add to config.yaml under api_keys section:" -ForegroundColor Gray
    Write-Host "      api_keys:" -ForegroundColor Gray
    Write-Host "        groq: 'gsk_your_key_here'" -ForegroundColor Gray
    Write-Host "   3. Or set environment variable:" -ForegroundColor Gray
    Write-Host "      `$env:GROQ_API_KEY='gsk_your_key_here'" -ForegroundColor Gray
}

Write-Host ""

# Verify new files
Write-Host "📄 Verifying new files..." -ForegroundColor Yellow
$requiredFiles = @(
    "services\activity_tracker.py",
    "services\teaching_score.py",
    "services\ai_explainer_bot.py",
    "app\pages\tracking.py",
    "app\pages\student_activity.py",
    "app\pages\analytics_dashboard.py"
)

$allPresent = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Missing: $file" -ForegroundColor Red
        $allPresent = $false
    }
}

Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📊 Setup Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if ($allPresent) {
    Write-Host "🎉 Setup Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ All required files are present" -ForegroundColor Green
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    Write-Host "✅ Storage directories created" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Review and update config.yaml if needed" -ForegroundColor Gray
    Write-Host "   2. Add GROQ_API_KEY for AI Chatbot" -ForegroundColor Gray
    Write-Host "   3. Run the application:" -ForegroundColor Gray
    Write-Host "      streamlit run app\streamlit_app.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor Cyan
    Write-Host "   - ADVANCED_FEATURES_GUIDE.md (comprehensive)" -ForegroundColor Gray
    Write-Host "   - QUICK_START_ADVANCED_FEATURES.md (quick start)" -ForegroundColor Gray
    Write-Host "   - IMPLEMENTATION_SUMMARY.md (overview)" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Setup Incomplete" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Some files are missing. Please ensure all new files are present." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Pause at the end
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
