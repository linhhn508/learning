# Back-End Feature Ideas

Compatible with current Flask + pymongo + MinIO stack.

## Content Features

- **Tags / Categories** — add `tags: [str]` field to posts, filter on index with `?tag=python`
- **Draft status** — add `status: 'draft' | 'published'` field; show drafts only to author
- **Scheduled publishing** — `publish_at` datetime field; cron-like check or filter in query
- **Post versioning** — store edit history as an array of `{content, edited_at}` subdocuments
- **Full-text search** — MongoDB text index on `title` + `content`, replace `$regex`

## API & Integration

- **REST API** — `/api/posts` (GET list, POST create), `/api/posts/<id>` (GET, PUT, DELETE)
- **RSS feed** — `/feed.xml` route using `feedgen` library
- **Webhook on publish** — POST to a Slack/Discord URL when a new post is created
- **Export to PDF** — `weasyprint` or `pdfkit` to generate a PDF from post HTML

## User Management

- **Authentication** — Flask-Login with MongoDB user collection
- **Author field** — associate posts with user IDs, show author name on post
- **Admin panel** — simple admin-only route to manage all posts, users, uploads
- **OAuth login** — GitHub/Google login via `authlib`

## Media Management

- **Image gallery** — `/gallery` route listing all uploads from MinIO bucket
- **Image resize on upload** — Pillow to generate thumbnails on the server
- **File type validation** — allowlist image MIME types, reject non-images
- **Cleanup orphaned images** — background task comparing S3 objects to post content

## Infrastructure

- **Health endpoint** — `/health` returning `{"status": "ok", "db": true, "s3": true}`
- **Request logging** — structured JSON logs with `flask-logging` or custom `after_request`
- **Rate limiting** — `flask-limiter` on upload and create endpoints
- **Metrics** — Prometheus endpoint via `prometheus-flask-instrumentator`
