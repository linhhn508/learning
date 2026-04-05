---
name: backend-review
description: "Use when: reviewing back-end code, improving Flask routes, optimizing MongoDB queries, adding API endpoints, fixing security issues, improving error handling, adding authentication, reviewing upload logic, improving data validation, suggesting back-end features, database indexing, performance optimization. Triggers on: review backend, improve API, fix security, add auth, optimize query, review Flask, database index."
---

# Back-End Review & Enhancement

Review, improve, and extend Flask + MongoDB + MinIO back-end code. Always read `app.py` before proposing changes.

## Workflow

1. **Read `app.py`** — understand all routes, helpers, and configuration
2. **Check against the security and performance checklists** in references
3. **Propose improvements** — grouped by severity
4. **Implement** — follow the established patterns below

## Established Patterns (must follow)

### Route Structure
```python
@app.route('/<string:post_id>/action', methods=('GET', 'POST'))
def action(post_id):
    post = get_post(post_id)          # validate + fetch
    if request.method == 'POST':
        # validate input → flash errors or mutate → redirect
    return render_template('template.html', post=post)
```

### MongoDB
- Direct pymongo — no ORM/ODM
- `collection.find_one()` for single docs, `collection.find().sort()` for lists
- Always `post['id'] = str(post['_id'])` before passing to templates
- Wrap user-supplied IDs: `try: ObjectId(id) except InvalidId: abort(404)`

### Error Handling
- Form validation: `flash('message', 'danger')` + re-render
- Success: `flash('message', 'success')` + `redirect(url_for(...))`
- API endpoints: `jsonify({'error': '...'}), 400`

### File Uploads
- `secure_filename()` always
- Validate `post_id` with `ObjectId()` before using in S3 keys
- S3 key: `{post_id}/{filename}`, bucket: `blog-image`
- Return `MINIO_PUBLIC_URL` (browser-facing), not `MINIO_URL` (internal)

## When Reviewing

Check these references for specific checklists:
- **Security**: See [references/security.md](references/security.md)
- **Performance**: See [references/performance.md](references/performance.md)
- **Feature ideas**: See [references/feature-ideas.md](references/feature-ideas.md)

## Constraints

- DO NOT introduce an ORM (SQLAlchemy, MongoEngine)
- DO NOT split `app.py` into a package unless explicitly requested
- DO NOT change env var names without updating `docker-compose.yml` and `.env`
- DO NOT use `flask run` for production — use Gunicorn
- DO NOT hardcode credentials or connection strings
