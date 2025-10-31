# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Smart LMS, please report it responsibly:

1. **DO NOT** open a public GitHub issue
2. Email security concerns to: [your-security-email@example.com]
3. Include: description, steps to reproduce, potential impact
4. Expected response time: 48 hours

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Security Best Practices for Deployment

### 1. Credential Management

**NEVER use default credentials in production.**

```bash
# Generate a strong secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set environment variables
export APP_SECRET_KEY=your_generated_key_here
export ADMIN_INITIAL_PASSWORD=strong_password_here
```

### 2. Configuration Security

- Copy `config.example.yaml` to `config.yaml` and customize
- Copy `.env.example` to `.env` and set all credentials
- Ensure `config.yaml` and `.env` are in `.gitignore`
- Set `app.debug: false` in production
- Use environment variables for all secrets

### 3. Initial Setup

**First-time deployment:**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
cp config.example.yaml config.yaml

# 3. Edit .env with secure credentials
nano .env

# 4. Create admin user (will prompt for secure password)
python scripts/init_storage.py --secure

# 5. Start application
streamlit run app/streamlit_app.py
```

### 4. Password Policy

Enforce strong passwords for all users:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- No dictionary words
- Force password change on first login
- Implement password expiration (90 days recommended)

### 5. Network Security

**Production deployment:**

```yaml
# Bind to specific interface
server:
  address: 127.0.0.1  # Or specific IP
  port: 8501
  
# Use reverse proxy (nginx/Apache) with:
- HTTPS/TLS 1.3
- Rate limiting
- IP whitelisting (if applicable)
- CSP headers
```

### 6. Data Privacy & GDPR Compliance

**PII Handling:**
- Face images/videos are NEVER stored by default
- Only derived engagement metrics are persisted
- Users can request data deletion
- Auto-anonymization after 180 days
- Data retention: 365 days (configurable)

**Configure in config.yaml:**

```yaml
privacy:
  require_consent: true
  store_raw_video: false
  data_retention_days: 365
  allow_data_deletion: true
  anonymize_after_days: 180
```

### 7. File Upload Security

**Implemented protections:**
- Filename sanitization
- MIME type validation
- File size limits
- Path traversal prevention
- Quarantine scanning (configure antivirus if available)

**Recommended additional steps:**
- Store uploads outside web root
- Use object storage (S3, Azure Blob) for production
- Implement virus scanning with ClamAV or similar

### 8. Subprocess Security

**OpenFace/External Tools:**
- Arguments are validated and escaped
- Strict timeouts enforced (300s default)
- No shell injection vectors
- Runs with minimal privileges
- Resource limits enforced

### 9. Database Security (Future)

When migrating from JSON to PostgreSQL/MySQL:

```bash
# Use encrypted connections
DB_SSL_MODE=require

# Principle of least privilege
- Separate read/write users
- No superuser access
- Use prepared statements (SQLAlchemy ORM)
```

### 10. Monitoring & Audit Logs

**Enable comprehensive logging:**

```yaml
logging:
  level: "INFO"  # DEBUG only in development
  file: "./logs/smart_lms.log"
  max_size: 10485760  # 10 MB
  backup_count: 5
```

**Monitor for:**
- Failed login attempts (auto-lockout after 5 attempts)
- Unusual access patterns
- Privilege escalation attempts
- Data export requests

### 11. Dependency Security

**Regular maintenance:**

```bash
# Check for vulnerabilities
pip install safety
safety check -r requirements.txt

# Update dependencies
pip install --upgrade pip
pip list --outdated

# Use pinned versions in production
pip freeze > requirements.lock
```

### 12. Secure Development Workflow

**Pre-commit checks:**

```bash
# Install hooks
pip install pre-commit
pre-commit install

# Run security linters
bandit -r services/ app/
pylint services/ app/
```

## Known Limitations

### JSON-Based Storage
- Not suitable for high-concurrency environments
- No transaction support
- Race conditions possible with concurrent writes
- **Recommendation:** Migrate to PostgreSQL for production

### Legacy Code
- `legacy/` folder contains archived Flask apps with known vulnerabilities
- **NEVER deploy legacy apps to production**
- Kept only for reference/migration purposes

### Demo Mode
- Default demo accounts are disabled in production builds
- If you need demo mode, it displays a prominent warning banner

## Data Handling Policy

### What We Collect
- User authentication data (bcrypt-hashed passwords)
- Engagement metrics (facial landmarks, gaze, attention)
- Behavioral logs (clicks, navigation, playback)
- Feedback text (for sentiment analysis)
- Quiz/assignment submissions

### What We DON'T Collect
- Raw webcam video (only processed features)
- Microphone audio
- Screen contents
- Personal conversations

### User Rights
- View all collected data
- Request data export (CSV/JSON)
- Request data deletion
- Opt-out of engagement tracking (with instructor approval)

## Incident Response

If a security breach occurs:

1. **Immediate Actions**
   - Rotate all secrets/keys
   - Reset all user passwords
   - Review audit logs
   - Isolate affected systems

2. **Notification**
   - Notify affected users within 72 hours
   - Report to relevant authorities (GDPR, FERPA, etc.)
   - Document timeline and scope

3. **Post-Incident**
   - Conduct root cause analysis
   - Update security controls
   - Retrain team
   - Update this policy

## Compliance

Smart LMS is designed with compliance in mind:

- **GDPR** (EU): Data minimization, consent, right to erasure
- **FERPA** (US): Student privacy protections
- **COPPA** (US): Parental consent for users under 13
- **CCPA** (California): Consumer privacy rights

**Deployers are responsible for:**
- Conducting Data Protection Impact Assessments (DPIA)
- Appointing Data Protection Officers where required
- Implementing appropriate technical controls
- Maintaining audit trails

## Security Checklist for Production

- [ ] All default credentials changed
- [ ] `debug: false` in config.yaml
- [ ] `.env` file configured with secrets
- [ ] HTTPS enabled with valid certificate
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] Regular backups configured
- [ ] Monitoring/alerting set up
- [ ] Audit logging enabled
- [ ] Data retention policy documented
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Incident response plan documented
- [ ] Security training completed
- [ ] Vulnerability scanning scheduled
- [ ] Dependency updates scheduled

## Contact

For security concerns: [security@example.com]  
For privacy questions: [privacy@example.com]  
General support: [support@example.com]

---

**Last Updated:** October 2025  
**Next Review:** January 2026
