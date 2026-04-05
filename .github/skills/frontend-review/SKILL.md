---
name: frontend-review
description: "Use when: reviewing front-end code, improving UI/UX, adding responsive design, enhancing accessibility, optimizing CSS, suggesting new front-end features, integrating third-party widgets, fixing layout issues, improving dark mode, adding animations, reviewing Bootstrap/Jinja2 templates, improving TinyMCE editor integration. Triggers on: review UI, improve frontend, add CSS, fix layout, responsive design, accessibility audit, dark mode, animation."
---

# Front-End Review & Enhancement

Review, improve, and extend front-end code following best practices. Always read the existing templates and CSS before proposing changes.

## Workflow

1. **Read existing code** — scan `templates/`, `static/css/style.css`, and the TinyMCE config in `base.html`
2. **Identify issues** — check against the checklists in the references below
3. **Propose improvements** — group by priority (critical → nice-to-have)
4. **Implement** — make changes that follow existing patterns (Bootstrap 4, Jinja2 blocks, hyphen-case CSS)

## When Reviewing Templates

- Verify all templates extend `base.html` and override `{% block title %}` + `{% block content %}`
- Check flash messages use `get_flashed_messages(with_categories=true)` with Bootstrap alert classes
- Verify active nav links use `request.endpoint` comparison
- Ensure `| safe` is only used on trusted content (TinyMCE output stored in the DB)
- Verify forms use POST for mutations; no action attribute means submit to current URL

## When Reviewing CSS

- Follow section comment format: `/* ══ SECTION NAME ══ */`
- Use hyphen-case class names (`.post-card`, `.img-float-left`)
- Every dark mode override must use `body.dark-mode .component` pattern
- Add `transition: background-color 0.3s` on elements that change in dark mode
- Card hover effects: `transform: translateY(-5px)` + `box-shadow`

## When Suggesting Features

Before suggesting, check the reference files for ideas that fit the current stack:
- **UI patterns**: See [references/ui-patterns.md](references/ui-patterns.md)
- **Accessibility**: See [references/accessibility.md](references/accessibility.md)

## Constraints

- DO NOT upgrade to Bootstrap 5 — templates use v4 classes (`badge-info`, `data-toggle`)
- DO NOT add a JS build step — frontend is vanilla JS + jQuery
- DO NOT add external CSS frameworks alongside Bootstrap
- DO NOT remove dark mode support when editing CSS
