# GitHub Copilot Instructions

## Priority Guidelines

When generating code for this repository:

1. **Version Compatibility**: Respect the exact versions in `pyproject.toml` — Python ≥3.12, Flask ≥3.1.3, pymongo ≥4.16.0, boto3 ≥1.42.83
2. **Codebase Patterns**: Match the patterns established in `app.py` — all routes, helpers, and configuration follow a single-file Flask convention
3. **Architectural Consistency**: This is a monolithic Flask app with MongoDB (pymongo) and MinIO (boto3 S3). There is no ORM — all queries use pymongo directly
4. **Code Quality**: Prioritize security (input validation, filename sanitization) and maintainability
5. **No Assumptions**: Only use patterns actually present in the codebase

---

## Technology Stack (exact versions)

| Layer | Technology | Version / Source |
|-------|-----------|-----------------|
| Language | Python | ≥3.12 (`pyproject.toml`) |
| Package manager | uv | Used in Dockerfile, manages venv |
| Web framework | Flask | ≥3.1.3 |
| Database | MongoDB | 7.0 (Docker image `mongo:7.0`) |
| DB driver | pymongo | ≥4.16.0 |
| Object storage | MinIO (S3-compatible) | `minio/minio` Docker image |
| S3 client | boto3 | ≥1.42.83 |
| Templating | Jinja2 | Bundled with Flask |
| CSS framework | Bootstrap | 4.3.1 (CDN) |
| JS library | jQuery | 3.3.1 (CDN) |
| Rich text editor | TinyMCE | Self-hosted (GPLv2, `static/js/tinymce/`) |
| Reverse proxy | Nginx | 1.27-alpine (Docker image) |
| Containerization | Docker + Docker Compose | Multi-service compose |

---

## Project Structure

```
app.py                      # Single-file Flask application (all routes and config)
pyproject.toml              # Dependencies managed by uv
Dockerfile.web_app          # Python 3.12-slim, uv sync, flask/gunicorn
docker-compose.yml          # nginx, web, mongo, minio, minio-init
load-balancer/nginx.conf    # Nginx reverse proxy config
.env                        # Environment variables (gitignored)
templates/
    base.html               # Base layout: navbar, footer, TinyMCE init, dark mode JS
    index.html              # Post listing with search, sort, thumbnails
    post.html               # Single post view with share buttons, prev/next nav
    create.html             # New post form with draft_id for image scoping
    edit.html               # Edit form with delete modal
    about.html              # About page with timeline
static/
    css/style.css           # All custom CSS (light + dark mode)
    js/tinymce/             # Self-hosted TinyMCE editor
```

---

## Python / Flask Patterns

### Import Organization
Standard library imports first, then third-party, then Flask imports grouped together:
```python
import boto3
import re
from botocore.client import Config
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import os
```

### Configuration
All external config comes from environment variables at module level:
```python
MONGODB_HOST = os.environ["MONGODB_HOST"]       # Required — crashes on startup if missing
MINIO_PUBLIC_URL = os.environ.get("MINIO_PUBLIC_URL", MINIO_URL)  # Optional with fallback
```
Never hardcode connection strings or credentials.

### Route Conventions
- View functions use `@app.route()` decorator directly on the function
- URL parameters use `<string:post_id>` for MongoDB ObjectIds
- GET+POST routes use tuple syntax: `methods=('GET', 'POST')`
- POST-only routes use list syntax: `methods=['POST']`
- Route handlers follow the pattern: validate → query/mutate → flash → redirect/render

### MongoDB Patterns
- Use `pymongo` directly — no ODM/ORM
- Database: `client['blog']`, collection: `db['posts']`
- Always convert `_id` to string for templates: `post['id'] = str(post['_id'])`
- Use `ObjectId(post_id)` with `try/except InvalidId` for all user-supplied IDs
- Queries use `find_one()` for single docs, `find()` with `.sort()` for lists
- Sort by `_id` to leverage the embedded timestamp — no separate `created_at` index needed

### Error Handling
- Invalid ObjectId → `abort(404)` via `get_post()` helper
- Missing required fields → `flash('message', 'danger')` + re-render form
- Successful actions → `flash('message', 'success')` + `redirect(url_for(...))`
- API endpoints (upload_image) → `jsonify({'error': '...'}), 400`

### MinIO / S3 Patterns
- boto3 client with `addressing_style: 'path'` (required for MinIO)
- Bucket name: `'blog-image'`
- Object keys: `{post_id}/{filename}` (per-post subfolder)
- Return URL: `f"{MINIO_PUBLIC_URL}/blog-image/{object_key}"` (browser-facing URL, not internal)
- Always `secure_filename()` before using in object keys
- Always validate `post_id` with `ObjectId()` before using in S3 keys (prevents path traversal)

---

## Jinja2 Template Patterns

### Block Structure
```
base.html defines: {% block title %}, {% block content %}, {% block tinymce_upload_url %}
Child templates override these blocks. tinymce_upload_url is used to pass post_id to the upload endpoint.
```

### Common Filters Used
- `| safe` — render HTML content (TinyMCE output)
- `| striptags` — strip HTML for text-only previews and word counts
- `| truncate(N)` — limit preview text length
- `| wordcount` — calculate reading time (÷ 200 = minutes)
- `| tojson` — safely pass Python strings to JavaScript

### Template Conventions
- Flash messages use `get_flashed_messages(with_categories=true)` with Bootstrap alert classes
- Active nav links use `request.endpoint` comparison
- Forms use `method="post"` — no `action` means submit to current URL
- Hidden inputs carry state across form re-renders (e.g., `draft_id`)
- Delete actions use Bootstrap modals, not `onclick="confirm(...)"`

---

## CSS Patterns

### Organization in `style.css`
Sections are separated by comment headers:
```css
/* ══════════════════════════════════════════════════
   SECTION NAME
   ══════════════════════════════════════════════════ */
```

### Naming
- Image float classes: `.img-float-left`, `.img-float-right`, `.img-center`
- State classes: `.dark-mode` (on body), `.fade-in-card`
- Component classes: `.site-footer`, `.scroll-top-btn`, `.about-avatar`, `.timeline`
- Uses hyphen-case for all custom classes

### Dark Mode
- Toggled by adding `.dark-mode` class to `<body>`
- Preference stored in `localStorage`
- All dark overrides use `body.dark-mode .component` selector pattern
- Every colored surface needs a `transition: background-color 0.3s` for smooth switching

### Animations
- Cards use `@keyframes fadeInUp` with staggered `animation-delay` via `:nth-child()`
- Hover effects use `transform: translateY(-5px)` + `box-shadow` transition

---

## Docker / DevOps Patterns

### Dockerfile
- Base: `python:3.12-slim`
- Install `uv` via pip, then `uv sync` for dependencies
- Copy config files first (layer caching), then source code
- CMD runs via `uv run --`

### Docker Compose
- Services: `nginx`, `web`, `mongo`, `minio`, `minio-init`
- All config via `.env` file with `${VAR}` interpolation
- Healthchecks on `mongo` and `minio` — dependents use `condition: service_healthy`
- `minio-init` is a one-shot container (runs `mc` commands then exits)
- Use `$$` for shell variables inside `entrypoint:` (double-dollar escapes Compose interpolation)
- Named volumes for persistent data (`mongo_data`, `minio_data`)

### Environment Variable Naming
- Uppercase with underscores: `MONGODB_HOST`, `MINIO_URL`, `MINIO_PUBLIC_URL`, `MINIO_USR`, `MINIO_PWD`
- Distinguish internal vs external URLs: `MINIO_URL` (Docker internal) vs `MINIO_PUBLIC_URL` (browser-facing)

### Nginx
- Upstream block: `upstream flask_app { server web:5000; }`
- Proxy headers: `Host`, `X-Real-IP`
- `client_max_body_size 100M` for image uploads

---

## Security Checklist

When adding new features, always:

1. **Validate ObjectIds** — wrap `ObjectId(user_input)` in `try/except InvalidId`
2. **Sanitize filenames** — always use `secure_filename()` before touching the filesystem or S3
3. **Use env vars for secrets** — never hardcode credentials, keys, or connection strings
4. **POST for mutations** — all create/update/delete operations must be POST, never GET
5. **Flash + redirect after POST** — follow Post/Redirect/Get pattern to prevent double submissions
6. **No raw string formatting in queries** — use pymongo's query operators, never f-string injection into queries

---

## What NOT to Do

- Do NOT introduce an ORM (SQLAlchemy, MongoEngine) — this project uses pymongo directly
- Do NOT add TypeScript or a JS build step — frontend is vanilla JS + jQuery
- Do NOT upgrade Bootstrap to v5 — the templates use v4-specific classes (`badge-info`, `data-toggle`)
- Do NOT split `app.py` into a package unless explicitly requested — it is intentionally a single file
- Do NOT use `flask run` in production — use Gunicorn behind Nginx
- Do NOT add features from newer Python versions without checking `requires-python = ">=3.12"`
