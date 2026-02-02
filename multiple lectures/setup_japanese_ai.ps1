# Japanese AI Setup Script
# Quickly install required packages and test AI service

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Japanese AI Learning Assistant Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set paths
$venvPath = "C:/Users/revan/Downloads/multiple lectures/.venv/Scripts/python.exe"
$projectPath = "C:\Users\revan\Downloads\multiple lectures\multiple lectures"

# Check if virtual environment exists
if (-Not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment not found at: $venvPath" -ForegroundColor Red
    Write-Host "Please activate your virtual environment first" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Virtual environment found" -ForegroundColor Green
Write-Host ""

# Install AI packages
Write-Host "📦 Installing AI packages..." -ForegroundColor Yellow
Write-Host ""

# Install Groq (FREE, recommended)
Write-Host "Installing Groq (FREE, fast)..." -ForegroundColor Cyan
& $venvPath -m pip install groq --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Groq installed" -ForegroundColor Green
} else {
    Write-Host "  ❌ Groq installation failed" -ForegroundColor Red
}

# Install Google Gemini (FREE alternative)
Write-Host "Installing Google Gemini (FREE)..." -ForegroundColor Cyan
& $venvPath -m pip install google-generativeai --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Google Gemini installed" -ForegroundColor Green
} else {
    Write-Host "  ❌ Gemini installation failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test availability
Write-Host "🧪 Testing AI service..." -ForegroundColor Yellow
Write-Host ""

$testScript = @"
from services.japanese_ai_service import check_ai_availability
import json

availability = check_ai_availability()
print('AI Provider Status:')
for provider, available in availability.items():
    status = '✅ Ready' if available else '❌ Not configured'
    print(f'  {provider.capitalize()}: {status}')

if any(availability.values()):
    print('\n✅ At least one AI provider is configured!')
    print('\nYou can now use the Japanese Learning Assistant.')
else:
    print('\n⚠️ No AI providers configured.')
    print('\nNext steps:')
    print('1. Get FREE API key from https://console.groq.com')
    print('2. Set environment variable:')
    print('   $env:GROQ_API_KEY=\"your_key_here\"')
    print('3. Restart Streamlit')
"@

Set-Location $projectPath
& $venvPath -c $testScript

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📚 Quick Start Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-Not $env:GROQ_API_KEY -and -Not $env:GOOGLE_API_KEY -and -Not $env:OPENAI_API_KEY) {
    Write-Host "⚠️  No API keys detected" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To get started with FREE AI:" -ForegroundColor White
    Write-Host ""
    Write-Host "1. Get Groq API key (FREE):" -ForegroundColor Cyan
    Write-Host "   https://console.groq.com" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Set API key:" -ForegroundColor Cyan
    Write-Host "   `$env:GROQ_API_KEY=`"your_key_here`"" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Restart Streamlit:" -ForegroundColor Cyan
    Write-Host "   streamlit run app/streamlit_app.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "✅ API key detected!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You're ready to use the Japanese AI Assistant!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Features available:" -ForegroundColor Cyan
    Write-Host "  📖 Text Explainer - Translate & explain Japanese" -ForegroundColor White
    Write-Host "  ✍️  Writing Corrector - Fix grammar & get feedback" -ForegroundColor White
    Write-Host "  💬 Conversation Practice - Chat in Japanese" -ForegroundColor White
    Write-Host "  📝 Quiz Generator - Create custom quizzes" -ForegroundColor White
    Write-Host "  📊 Assignment Grader - Auto-grade with feedback" -ForegroundColor White
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📖 Documentation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Full guide: JAPANESE_AI_GUIDE.md" -ForegroundColor White
Write-Host "Service code: services/japanese_ai_service.py" -ForegroundColor White
Write-Host "UI page: app/pages/japanese_assistant.py" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Offer to open guide
$openGuide = Read-Host "Open JAPANESE_AI_GUIDE.md? (y/n)"
if ($openGuide -eq 'y' -or $openGuide -eq 'Y') {
    Start-Process notepad.exe "$projectPath\JAPANESE_AI_GUIDE.md"
}

Write-Host ""
Write-Host "Setup complete! 🎉" -ForegroundColor Green
Write-Host ""
