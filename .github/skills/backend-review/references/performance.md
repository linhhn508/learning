# Back-End Performance Checklist

## MongoDB

- [ ] Index on frequently queried fields — `title` (text search), `_id` (already indexed)
- [ ] Use `projection` to limit returned fields when full document not needed
- [ ] Use `limit()` for paginated queries instead of loading all posts
- [ ] Avoid `find()` without a filter in production (full collection scan)
- [ ] Consider a text index for full-text search: `collection.create_index([("title", "text"), ("content", "text")])`

## Flask

- [ ] Use Gunicorn with multiple workers (`-w 4`) instead of `flask run`
- [ ] Set `app.config['MAX_CONTENT_LENGTH']` to reject oversized uploads early
- [ ] Use `after_request` for common headers instead of repeating in each route
- [ ] Consider `flask-compress` for gzip responses (CSS, HTML, JSON)

## MinIO / S3

- [ ] Use `upload_fileobj()` (streaming) not `upload_file()` (disk) — already correct ✓
- [ ] Generate presigned URLs for large files to offload bandwidth from Flask
- [ ] Set `Cache-Control` headers on uploaded objects so browsers cache images

## Nginx

- [ ] Serve static files directly from Nginx (bypass Flask for CSS/JS/images)
- [ ] Enable gzip in Nginx config for text-based responses
- [ ] Set `proxy_buffering on` for large responses
- [ ] Add `keepalive` to the upstream block for connection reuse

## Caching Strategies

- Template fragment caching with `flask-caching` for expensive renders
- HTTP cache headers on static assets (`Cache-Control: max-age=31536000`)
- ETags on post pages for conditional requests
