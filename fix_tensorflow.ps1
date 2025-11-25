# Fix TensorFlow dependency issues
Write-Host "Fixing TensorFlow dependencies..." -ForegroundColor Cyan

# Uninstall problematic packages
Write-Host "Uninstalling conflicting packages..." -ForegroundColor Yellow
& ".venv/Scripts/python.exe" -m pip uninstall -y numpy pandas scikit-learn ml-dtypes jax jaxlib

# Reinstall with compatible versions
Write-Host "`nReinstalling with compatible versions..." -ForegroundColor Yellow
& ".venv/Scripts/python.exe" -m pip install numpy==1.26.4
& ".venv/Scripts/python.exe" -m pip install pandas==2.1.4
& ".venv/Scripts/python.exe" -m pip install scikit-learn==1.3.2
& ".venv/Scripts/python.exe" -m pip install ml-dtypes==0.4.1
& ".venv/Scripts/python.exe" -m pip install "jax[cpu]==0.4.23"

Write-Host "`nVerifying TensorFlow..." -ForegroundColor Cyan
& ".venv/Scripts/python.exe" -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__} loaded successfully!')"

Write-Host "`nTesting model loading..." -ForegroundColor Cyan
Push-Location "multiple lectures"
& "../.venv/Scripts/python.exe" test_model_loading.py
Pop-Location
