# Back-End Security Checklist

## Input Validation

- [ ] All user-supplied ObjectIds wrapped in `try/except InvalidId`
- [ ] `secure_filename()` used on every uploaded file before filesystem/S3 operations
- [ ] Search queries use pymongo operators (`$regex`), never string interpolation
- [ ] `SECRET_KEY` loaded from env var, not hardcoded (current: `'123'` — must fix)
- [ ] POST required for all state-changing operations (create, edit, delete, upload)

## Authentication & Authorization (when adding)

- Prefer Flask-Login for session-based auth
- Hash passwords with `werkzeug.security.generate_password_hash` (pbkdf2)
- Never store plaintext passwords
- Protect routes with `@login_required` decorator
- CSRF protection: use Flask-WTF or hidden token pattern

## File Upload Security

- [ ] Validate MIME type (`file.content_type`) against an allowlist before saving
- [ ] Limit file size — set `app.config['MAX_CONTENT_LENGTH']` (e.g., 16MB)
- [ ] Generated filenames avoid collisions — prepend timestamp or UUID to `secure_filename()`
- [ ] S3 keys validated — `post_id` verified as ObjectId before building key path

## HTTP Headers

- Add `X-Content-Type-Options: nosniff` — prevents MIME sniffing
- Add `X-Frame-Options: DENY` — prevents clickjacking
- Add `Content-Security-Policy` — restrict script/image sources
- Flask-Talisman can add all of these with one line

## MongoDB Injection

- pymongo is safe from string injection by design (BSON queries, not string concatenation)
- Still avoid: `collection.find(json.loads(user_input))` — never parse user JSON into queries
- Use specific field queries: `{"title": {"$regex": query, "$options": "i"}}` ✓
