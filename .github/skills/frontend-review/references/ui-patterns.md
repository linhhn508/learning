# Front-End UI Patterns

Feature ideas compatible with Bootstrap 4 + Jinja2 + jQuery.

## Layout & Navigation

- **Breadcrumbs** — `<nav aria-label="breadcrumb">` on post/edit pages
- **Pagination** — split index into pages (10 posts/page) with `?page=N` param
- **Sticky navbar** — `position: sticky; top: 0; z-index: 1030;`
- **Table of contents** — auto-generated from `<h2>`/`<h3>` in post content via JS
- **Reading progress bar** — thin bar at top of post page showing scroll %

## Content Display

- **Related posts** — show 2-3 posts at bottom of post page (by recent or random)
- **Image lightbox** — click to expand images in post content (use Bootstrap modal)
- **Code syntax highlighting** — add Prism.js or Highlight.js for `<pre><code>` blocks
- **Tags / Categories** — badge-based filtering on index page
- **Estimated publish date** — "Published 3 days ago" using JS `Intl.RelativeTimeFormat`

## Forms & Interactions

- **Auto-save drafts** — periodically POST to `/auto_save` via `setInterval` + fetch
- **Unsaved changes warning** — `beforeunload` event if form is dirty
- **Drag-and-drop image upload** — TinyMCE supports this with `paste_data_images: true`
- **Title slug preview** — show URL-friendly slug below title input as user types
- **Confirmation toasts** — replace flash alerts with Bootstrap toasts for less intrusive messaging

## Visual Polish

- **Loading skeleton** — CSS placeholder cards while content loads
- **Smooth scroll** — `html { scroll-behavior: smooth; }` for anchor links
- **Card hover gradient** — subtle gradient overlay on card thumbnails
- **Print stylesheet** — `@media print` to hide nav, footer, buttons on post page
- **Favicon** — add a simple emoji favicon via `<link rel="icon" href="data:image/svg+xml,...">`
