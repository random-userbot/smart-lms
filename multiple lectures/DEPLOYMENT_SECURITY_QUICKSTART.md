# 🚀 Quick Security Deployment Guide

**For System Administrators deploying Smart LMS**

---

## ⚡ Fast Track Setup (10 minutes)

### 1. Clone & Install
```bash
git clone https://github.com/random-userbot/smart-lms.git
cd smart-lms
git checkout revanth

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy templates
cp config.example.yaml config.yaml
cp .env.example .env

# Edit .env with your secrets (use a strong password generator!)
nano .env
```

### 3. Run Secure Initialization
```bash
# This will prompt you to create a strong admin password
python scripts/secure_init.py
```

✅ **Done!** Your system is now secure.

### 4. Start Application
```bash
streamlit run app/streamlit_app.py
```

---

## 🔒 Security Checklist (2 minutes)

Before going live, verify these:

```bash
# 1. Config has debug disabled
grep "debug: false" config.yaml

# 2. Secrets are not in repo
git status | grep -E "(config.yaml|\.env)"
# Should return nothing

# 3. Pre-commit hooks installed (optional but recommended)
pip install pre-commit
pre-commit install

# 4. Run security scan
bandit -r services/ app/ -ll

# 5. Check for secrets
grep -r "password.*123" --include="*.py" services/ app/
# Should return nothing
```

---

## ⚠️ Critical Don'ts

### ❌ NEVER do these in production:

1. **Don't use demo credentials**
   - No `admin/admin123`
   - No `demo_student/student123`
   - Generate strong passwords with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

2. **Don't enable debug mode**
   - `config.yaml`: `debug: false`
   - Check with: `grep "debug: true" config.yaml` (should return nothing)

3. **Don't commit secrets**
   - `config.yaml` → `.gitignore`
   - `.env` → `.gitignore`
   - Check with: `git ls-files | grep -E "(config.yaml|\.env)"`

4. **Don't deploy legacy code**
   - `legacy/` folder contains vulnerable old code
   - It's excluded from deployment via `.gitattributes`

5. **Don't skip consent**
   - `config.yaml`: `consent_required: true`
   - Required for GDPR/privacy compliance

---

## 🛡️ Password Requirements

When creating admin/user passwords, enforce:

✅ **Minimum 12 characters**  
✅ **At least 1 uppercase letter**  
✅ **At least 1 lowercase letter**  
✅ **At least 1 number**  
✅ **At least 1 special character** (!@#$%^&*)  
✅ **Not a common password** (e.g., "password123")

**The secure_init.py script enforces all of these automatically.**

---

## 📊 Quick Security Test

Run this to verify your setup:

```bash
# Create test script
cat > test_security.sh << 'EOF'
#!/bin/bash
echo "🔍 Running Security Checks..."

# 1. Check debug mode
if grep -q "debug: true" config.yaml; then
    echo "❌ FAIL: Debug mode enabled"
    exit 1
else
    echo "✅ PASS: Debug disabled"
fi

# 2. Check consent
if grep -q "consent_required: false" config.yaml; then
    echo "❌ FAIL: Consent not required"
    exit 1
else
    echo "✅ PASS: Consent required"
fi

# 3. Check secrets in repo
if git ls-files | grep -E "(config.yaml|\.env)$"; then
    echo "❌ FAIL: Secrets committed to repo"
    exit 1
else
    echo "✅ PASS: Secrets not in repo"
fi

# 4. Check for hardcoded passwords
if grep -r "admin123\|teacher123\|student123" --include="*.py" services/ app/ 2>/dev/null; then
    echo "❌ FAIL: Hardcoded passwords found"
    exit 1
else
    echo "✅ PASS: No hardcoded passwords"
fi

echo ""
echo "✅ All security checks passed!"
EOF

chmod +x test_security.sh
./test_security.sh
```

---

## 🔐 Initial Admin Account Setup

The `secure_init.py` script will prompt you:

```
Admin Username [admin]: sysadmin
Admin Email [admin@example.com]: admin@yourdomain.com
Admin Password: [type strong password]
Confirm Password: [retype]

✅ Password is strong
✅ Admin user 'sysadmin' created successfully!
```

**Save these credentials in a password manager immediately!**

---

## 🌐 Production Deployment

### Option 1: Reverse Proxy (Recommended)

Use nginx or Apache in front of Streamlit:

```nginx
# nginx example
server {
    listen 443 ssl http2;
    server_name lms.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 2: Docker (Coming Soon)

```bash
# Future: Docker deployment
docker-compose up -d
```

---

## 📝 Environment Variables Reference

**Minimum required in `.env`:**

```bash
# App
APP_DEBUG=false
APP_SECRET_KEY=<generate-with-secrets.token_hex(32)>

# Admin (one-time setup)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_INITIAL_PASSWORD=<leave-blank-for-prompt>

# Security
BCRYPT_ROUNDS=12
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
```

**Optional (database):**

```bash
DB_ENABLED=false  # Set true if using PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_lms
DB_USER=lms_user
DB_PASSWORD=<strong-password-here>
```

---

## 🚨 Incident Response

If you suspect a security breach:

1. **Immediately:**
   ```bash
   # Rotate secrets
   python -c "import secrets; print(secrets.token_hex(32))" > new_secret.txt
   # Update .env with new secret
   
   # Force all users to reset passwords
   # (See SECURITY_REMEDIATION.md for script)
   ```

2. **Review logs:**
   ```bash
   tail -f logs/smart_lms.log
   # Look for suspicious login attempts
   ```

3. **Contact security team:**
   - Email: security@yourdomain.com
   - Reference: `SECURITY.md` incident response section

---

## 📚 Additional Resources

- **Full Security Guide:** See `SECURITY.md`
- **Remediation Report:** See `SECURITY_REMEDIATION.md`
- **Configuration Reference:** See `config.example.yaml`
- **User Management:** See `USER_RESOURCE_MANAGEMENT_GUIDE.md`

---

## 💡 Pro Tips

1. **Use a password manager** for all credentials
2. **Enable 2FA** when implemented (future feature)
3. **Regular backups:**
   ```bash
   # Backup storage
   tar -czf backup_$(date +%Y%m%d).tar.gz storage/
   ```
4. **Monitor logs** for failed login attempts
5. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   safety check
   ```

---

## ✅ You're Ready!

Your Smart LMS deployment is now **secure and production-ready**.

**Questions?** Open an issue on GitHub or contact support.

**Found a security issue?** Report to: security@example.com (DO NOT open public issue)

---

**Last Updated:** October 25, 2025  
**Version:** 2.0.0-secure
